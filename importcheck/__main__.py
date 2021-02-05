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
import platform
import sys
from typing import Optional, cast

# 3rd party
import click
from consolekit import click_command
from consolekit.options import colour_option, flag_option, verbose_option, version_option
from consolekit.terminal_colours import Back, ColourTrilean, Style, resolve_color_default
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike

# this package
from importcheck import check_module, evaluate_markers, load_toml

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["main"]


def about(level: int = 1):
	"""
	Print information about ``importcheck``.
	"""

	if not level:
		return

	output = [f"importcheck version {__version__}"]

	if level > 1:
		output.append(f"on {platform.python_implementation()} v{platform.python_version()}")

	click.echo(' '.join(output))


def version_callback(ctx: click.Context, param: click.Option, value: int):  # noqa: D103
	if not value or ctx.resilient_parsing:  # pragma: no cover
		return

	about(value)
	ctx.exit()


@click.option(
		"-c",
		"--config-file",
		type=click.STRING,
		help="The path to the TOML configuration file to use.",
		default="pyproject.toml",
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
@verbose_option()
@version_option(version_callback)
@click_command()
def main(
		config_file: PathLike,
		colour: ColourTrilean = None,
		verbose: bool = False,
		show: Optional[bool] = None,
		count: Optional[bool] = None,
		):
	"""
	Check modules can be imported.
	"""

	retv = 0

	echo = functools.partial(click.echo, color=resolve_color_default(colour))

	stats = {"passed": 0, "failed": 0}

	config = load_toml(config_file)
	modules_to_check = evaluate_markers(config)

	if "config" in config:
		if show is None:
			show = config["config"].get("show", show)
		if count is None:
			count = config["config"].get("count", count)

	if verbose:
		about(2)
	else:
		about()
	click.echo()

	if verbose == 2:
		show = True

	longest_name = max(map(len, modules_to_check))
	longest_name += 15

	for module in modules_to_check:
		echo(Style.BRIGHT(f"Checking {module!r}".ljust(longest_name, '.')), nl=False)

		ret = check_module(module, combine_output=True)

		if ret:
			retv |= 1
			echo(Back.RED("Failed"))
			stats["failed"] += 1

			if show:
				echo(Style.BRIGHT("Captured output:"))
				stdout = StringList(ret.stdout)  #
				stdout.blankline(ensure_single=True)
				echo(stdout)
		else:
			echo(Back.GREEN("Passed"))
			stats["passed"] += 1

	# TODO: global config for stats and show

	if (retv and not show) or count:
		echo()

	if retv and count:
		echo(f"{stats['passed']}/{sum(stats.values())} modules imported successfully.")
	elif not retv and count:
		echo(f"All {stats['passed']} modules imported successfully.")

	if retv and not show:
		echo("Tip: run with '--show' to show tracebacks for failed imports.")

	sys.exit(retv)


if __name__ == "__main__":
	sys.exit(main())
