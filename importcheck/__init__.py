#!/usr/bin/env python3
#
#  __init__.py
"""
A tool to check all modules can be correctly imported.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import contextlib
import functools
import importlib
import importlib.machinery
import importlib.util
import traceback
from typing import Any, Dict, Iterable, Iterator, List, Mapping, NamedTuple, Tuple, Union, cast

# 3rd party
import click
import dom_toml
from click.globals import resolve_color_default
from consolekit.terminal_colours import Back, Style
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from domdf_python_tools.utils import redirect_output
from domdf_python_tools.words import Plural
from packaging.markers import Marker
from typing_extensions import TypedDict

__all__ = [
		"ConfigDict",
		"Error",
		"OK",
		"check_module",
		"evaluate_markers",
		"load_toml",
		"paths_to_modules",
		"ImportChecker"
		]

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.4.0"
__email__: str = "dominic@davis-foster.co.uk"

_module = Plural("module", "modules")


class ConfigDict(TypedDict, total=False):
	"""
	:class:`typing.TypedDict` representing the configuration mapping parsed from ``pyproject.toml`` or similar.
	"""

	#: List of modules to always try to import.
	always: List[str]

	#: Mapping of :pep:`508` markers to lists of imports to try to import if the markers evaluate to :py:obj:`True`.
	only_if: Mapping[str, List[str]]

	#: Configuration for ``importcheck``.
	config: Dict[str, Any]


def load_toml(filename: PathLike) -> ConfigDict:
	"""
	Load the ``importcheck`` configuration mapping from the given TOML file.

	:param filename:
	"""

	config = dom_toml.load(filename)

	if "importcheck" in config:
		return cast(ConfigDict, config["importcheck"])
	elif "tool" in config and "importcheck" in config["tool"]:
		return cast(ConfigDict, config["tool"]["importcheck"])
	else:
		raise KeyError("No such table 'importcheck' or 'tool.importcheck'")


def evaluate_markers(config: ConfigDict) -> List[str]:
	"""
	Evaluate the markers in the ``only_if`` key and return a list of all modules to try to import.

	:param config:
	"""

	modules_to_check: List[str] = []

	if "always" in config:
		modules_to_check.extend(config["always"])

	if "only_if" in config:
		for marker, modules in config["only_if"].items():
			if Marker(marker).evaluate():
				modules_to_check.extend(modules)

	return modules_to_check


@prettify_docstrings
class OK(NamedTuple):
	"""
	Returned by :func:`~.check_module` if the module is successfully imported.
	"""

	#: The name of the module being checked.
	module: str

	@property
	def stdout(self):  # noqa: D102
		raise NotImplementedError

	@property
	def stderr(self):  # noqa: D102
		raise NotImplementedError

	def __bool__(self):
		"""
		:class:`~.OK` objects always evaluate as :py:obj:`False`.
		"""
		return False


@prettify_docstrings
class Error(NamedTuple):
	"""
	Returned by :func:`~.check_module` if the module could not be successfully imported.
	"""

	#: The name of the module being checked.
	module: str

	stdout: str
	"""
	The standard output from importing the module.

	This may also contain standard error if the streams are combined by :func:`~.check_module`
	"""

	stderr: str
	"""
	Standard error generated by importing the module.

	This may also contain standard out if the streams are combined by :func:`~.check_module`.
	"""

	def __bool__(self):
		return True


def check_module(module: str, combine_output: bool = False) -> Union[OK, Error]:
	"""
	Try to import ``module``, otherwise handle the resulting error.

	:param module:
	:param combine_output: If :py:obj:`True` ``stderr`` is combined with ``stdout``.
	"""

	with redirect_output(combine_output) as (stdout, stderr):
		try:
			importlib.import_module(module)
			return OK(module)
		except Exception as e:
			traceback_frames = traceback.extract_tb(e.__traceback__)
			tb_e = traceback.TracebackException(
					type(e),
					e,
					e.__traceback__,  # type: ignore
					)

			if traceback_frames[0].filename == __file__:
				del traceback_frames[0]

			buf = ['Traceback (most recent call last):\n']
			buf.extend(traceback.format_list(traceback_frames))

			while buf[-1] == '\n':  # pragma: no cover
				del buf[-1]

			buf.extend(tb_e.format_exception_only())

			click.echo(''.join(buf), file=stderr)

			return Error(module, stdout.getvalue(), stderr.getvalue())


def paths_to_modules(*paths: PathLike) -> Iterator[str]:
	r"""
	Convert filesystem paths (e.g. ``foo/bar.py``) into dotted import names (e.g. ``foo.bar``).

	.. versionadded:: 0.3.0

	:param \*paths: The paths to convert.
	"""

	for path in paths:
		path = PathPlus(path)

		if path.is_file() and path.suffix == ".py":
			path = path.with_suffix('')

		yield '.'.join(path.parts)


class ImportChecker:
	"""
	Class for checking modules can be imported.

	.. versionadded:: 0.3.0

	:param modules: The list of modules to be checked.
	:param show: Whether to show stdout and stderr generated from imports.
	:param colour: Whether to use coloured output.
	"""

	def __init__(
			self,
			modules: Iterable[str],
			*,
			show: bool = False,
			colour: bool = False,
			):

		#: The list of modules to be checked.
		self.modules: List[str] = list(modules)

		#: Dictionary holding statistics about passing/failing imports.
		self.stats: Dict[str, int] = {"passed": 0, "failed": 0}

		#: Whether to show stdout and stderr generated from imports.
		self.show = show

		#: Whether to use coloured output.
		self.colour = colour

	def check_modules(self) -> Iterator[Tuple[str, int]]:
		"""
		Checks modules can be imported.

		:returns: An iterator of 2-element tuples comprising the name of the module and the import status:

			0. The module was imported successfully.
			1. The module could not be imported. If :attr:`~.show` is :py:obj:`True` the traceback will be shown.
		"""

		longest_name = 15
		echo = functools.partial(click.echo, color=resolve_color_default(self.colour))

		if self.modules:
			longest_name += max(map(len, self.modules))
		else:
			return

		for module_name in self.modules:
			echo(Style.BRIGHT(f"Checking {module_name!r}".ljust(longest_name, '.')), nl=False)

			ret = check_module(module_name, combine_output=True)

			if ret:
				echo(Back.RED("Failed"))
				self.stats["failed"] += 1

				if self.show:
					echo(Style.BRIGHT("Captured output:"))
					stdout = StringList(ret.stdout)
					stdout.blankline(ensure_single=True)
					echo(stdout)

				yield module_name, 1

			else:
				echo(Back.GREEN("Passed"))
				self.stats["passed"] += 1
				yield module_name, 0

	def format_statistics(self) -> str:
		"""
		Returns a string reporting the number of modules imported successfully.
		"""

		if self.stats["failed"]:
			total_modules = sum(self.stats.values())
			return f"{self.stats['passed']}/{total_modules} {_module(total_modules)} imported successfully."

		else:
			n_passed = self.stats["passed"]

			if not n_passed:
				return f"No modules to check."
			elif n_passed == 1:
				return f"{self.stats['passed']} module imported successfully."
			else:
				return f"All {self.stats['passed']} modules imported successfully."
