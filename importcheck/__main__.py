#!/usr/bin/env python3
#
#  __main__.py
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
import functools
import operator
import platform
import re
import sys
from typing import Iterable, Optional

# 3rd party
import click
from consolekit import click_command
from consolekit.options import auto_default_option, colour_option, flag_option, verbose_option, version_option
from consolekit.terminal_colours import ColourTrilean, resolve_color_default
from domdf_python_tools.typing import PathLike

# this package
from importcheck import ImportChecker, __version__, evaluate_markers, load_toml, paths_to_modules

__all__ = ("main", )


def about(level: int = 1) -> None:
	"""
	Print information about ``importcheck``.
	"""

	if not level:
		return  # pragma: no cover

	output = [f"importcheck version {__version__}"]

	if level > 1:
		output.append(f"on {platform.python_implementation()} v{platform.python_version()}")

	click.echo(' '.join(output))


def version_callback(
		ctx: click.Context,
		param: click.Option,
		value: int,
		) -> None:
	if not value or ctx.resilient_parsing:  # pragma: no cover
		return

	about(value)
	ctx.exit()


@auto_default_option(
		"-c",
		"--config-file",
		type=click.STRING,
		help="The path to the TOML configuration file to use.",
		show_default=True,
		)
@colour_option()
@flag_option(
		"-s",
		"--show/--no-show",
		default=None,
		help="Whether to show stdout and stderr generated from imports.",
		)
@flag_option(
		"-C",
		"--count/--no-count",
		default=None,
		help="Whether to show a count of the passed and failed imports at the end.",
		)
@click.argument("module", type=click.STRING, nargs=-1)
@verbose_option()
@version_option(version_callback)
@click_command()
def main(
		module: Iterable[str] = (),
		config_file: PathLike = "pyproject.toml",
		colour: ColourTrilean = None,
		verbose: bool = False,
		show: Optional[bool] = None,
		count: Optional[bool] = None,
		) -> None:
	"""
	Check modules can be imported.

	Modules can be given as the MODULE argument or in the configuration file.
	"""

	echo = functools.partial(click.echo, color=resolve_color_default(colour))

	if module:
		if module == ('-', ):
			modules_to_check = list(filter(bool, map(str.strip, re.split("[\n ]", sys.stdin.read()))))
		else:
			modules_to_check = list(module)

		try:
			config = load_toml(config_file)
		except (KeyError, FileNotFoundError):
			config = {}

	else:
		try:
			config = load_toml(config_file)
		except KeyError as e:
			if e.args and e.args[0] == "No such table 'importcheck' or 'tool.importcheck'":
				click.echo(f"KeyError: {e.args[0]} in {config_file!r}", err=True)
				raise click.Abort()
			else:
				raise e

		modules_to_check = evaluate_markers(config)

	if "config" in config:
		if show is None:
			show = config["config"].get("show", show)
		if count is None:
			count = config["config"].get("count", count)

	if verbose == 2:
		show = True

	# if / in path replace with . and remove .py* extension
	modules_to_check = list(paths_to_modules(*modules_to_check))

	if not modules_to_check:
		if verbose:
			echo("No modules to check.")

		sys.exit(0)

	about(2 if verbose else 1)
	click.echo()

	checker = ImportChecker(modules_to_check, show=show or False, colour=colour or False)
	retv = functools.reduce(operator.or_, map(operator.itemgetter(1), checker.check_modules()), 0)

	if (retv and not show) or count:
		echo()

	if count:
		echo(checker.format_statistics())

	if retv and not show:
		echo("Tip: run with '--show' to show tracebacks for failed imports.")

	sys.exit(retv)


if __name__ == "__main__":
	sys.exit(main())
