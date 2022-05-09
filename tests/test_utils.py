# stdlib
import sys
from typing import List

# 3rd party
import click
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from importcheck import load_toml, paths_to_modules, redirect_output


def test_redirect_output() -> None:
	with redirect_output() as (stdout, stderr):
		print("I'm going to stdout")
		click.echo("I'm going to stderr", file=sys.stderr)
		click.echo("I'm also going to stdout", file=stdout)
		print("I'm also going to stderr", file=stderr)

	assert stdout.getvalue() == "I'm going to stdout\nI'm also going to stdout\n"
	assert stderr.getvalue() == "I'm going to stderr\nI'm also going to stderr\n"


def test_redirect_output_combine() -> None:
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
		) -> None:

	filename = tmp_pathplus / "pyproject.toml"
	filename.write_lines(content)
	advanced_data_regression.check(load_toml(filename))


def test_load_toml_errors(tmp_pathplus: PathPlus):
	with pytest.raises(FileNotFoundError):
		load_toml(tmp_pathplus / "too.txt")

	(tmp_pathplus / "pyproject.toml").write_text("[build-system]\n")

	with pytest.raises(KeyError, match="No such table 'importcheck' or 'tool.importcheck'"):
		load_toml(tmp_pathplus / "pyproject.toml")


def test_paths_to_modules(tmp_pathplus: PathPlus) -> None:
	modules = [
			tmp_pathplus / "my_module.py",
			tmp_pathplus / "my_code" / "my_module.py",
			]

	for file in modules:
		file.parent.maybe_make()
		file.touch()

	with in_directory(tmp_pathplus):
		expected = ["my_module", "my_code.my_module"]
		assert list(paths_to_modules(*(m.relative_to(tmp_pathplus) for m in modules))) == expected

	expected = ["my_module.py", "my_code.my_module.py"]
	assert list(paths_to_modules(*(m.relative_to(tmp_pathplus) for m in modules))) == expected

	assert list(paths_to_modules("collections")) == ["collections"]
