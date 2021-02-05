# stdlib
import sys
from typing import List

# 3rd party
import click
import pytest
from coincidence import AdvancedDataRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from importcheck import load_toml, redirect_output


def test_redirect_output():
	with redirect_output() as (stdout, stderr):
		print("I'm going to stdout")
		click.echo("I'm going to stderr", file=sys.stderr)
		click.echo("I'm also going to stdout", file=stdout)
		print("I'm also going to stderr", file=stderr)

	assert stdout.getvalue() == "I'm going to stdout\nI'm also going to stdout\n"
	assert stderr.getvalue() == "I'm going to stderr\nI'm also going to stderr\n"


def test_redirect_output_combine():
	with redirect_output(combine=True) as (stdout, stderr):
		click.echo("I'm going to stdout")
		print("I'm going to stderr", file=sys.stderr)
		print("I'm also going to stdout", file=stdout)
		click.echo("I'm also going to stderr", file=stderr)

	expected = "I'm going to stdout\nI'm going to stderr\nI'm also going to stdout\nI'm also going to stderr\n"
	assert stdout.getvalue() == expected
	assert stderr.getvalue() == expected


pyproject_content = [
		"[build-system]",
		'requires = [ "setuptools>=40.6.0", "wheel>=0.34.2",]',
		'build-backend = "setuptools.build_meta"',
		'',
		"[tool.importcheck]",
		'always = [ "importcheck", "foo",]',
		'',
		"[tool.importcheck.only_if]",
		'"sys_platform == \\"linux\\"" = [ "importcheck.__main__",]',
		'',
		"[tool.importcheck.config]",
		"show = true",
		"count = true",
		]

importcheck_content = [
		"[importcheck]",
		'always = [ "importcheck", "foo",]',
		'',
		"[importcheck.only_if]",
		'"sys_platform == \\"linux\\"" = [ "importcheck.__main__",]',
		'',
		"[importcheck.config]",
		"show = true",
		"count = true",
		]


@pytest.mark.parametrize(
		"content",
		[
				pytest.param(pyproject_content, id="pyproject.toml"),
				pytest.param(importcheck_content, id="importcheck.toml"),
				]
		)
def test_load_toml(
		content: List[str],
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	filename = tmp_pathplus / "pyproject.toml"
	filename.write_lines(content)
	advanced_data_regression.check(load_toml(filename))


def test_load_toml_errors(tmp_pathplus: PathPlus):
	with pytest.raises(FileNotFoundError):
		load_toml(tmp_pathplus / "too.txt")

	(tmp_pathplus / "pyproject.toml").write_text("[build-system]\n")

	with pytest.raises(KeyError, match="No such table 'importcheck' or 'tool.importcheck'"):
		load_toml(tmp_pathplus / "pyproject.toml")
