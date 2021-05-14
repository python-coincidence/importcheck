# stdlib
import platform
import re

# 3rd party
import click
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from coincidence.selectors import (
		not_macos,
		not_pypy,
		not_windows,
		only_macos,
		only_pypy,
		only_version,
		only_windows
		)
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from importcheck.__main__ import __version__, main


def fix_stdout(stdout: str) -> str:
	stdout = stdout.rstrip().replace(
			f"{platform.python_implementation()} v{platform.python_version()}", "FakePython v1.2.3"
			)
	stdout = stdout.replace(f"importcheck version {__version__}", "importcheck version 0.0.0")
	stdout = re.sub(r"python3.(\d+)", "python3.8", stdout)
	stdout = re.sub(r'File ".*[/\\]importlib[/\\]__init__.py"', 'File ".../importlib/__init__.py"', stdout)
	return stdout


platforms = pytest.mark.parametrize(
		"platform",
		[
				pytest.param("Windows", marks=only_windows("Output differs on Windows")),
				pytest.param(
						"Linux",
						marks=[not_windows("Output differs on Linux"), not_macos("Output differs on Linux")]
						),
				pytest.param("Darwin", marks=only_macos("Output differs on macOS")),
				]
		)

only_pp = only_pypy(reason="Output differs on PyPy")
not_pp = not_pypy(reason="Output differs on PyPy")

versions = pytest.mark.parametrize(
		"version",
		[
				pytest.param("3.6", marks=[only_version(3.6, reason="Output differs on Python 3.6"), not_pp]),
				pytest.param("3.7", marks=[only_version(3.7, reason="Output differs on Python 3.7"), not_pp]),
				pytest.param(
						"3.6-pypy", marks=[only_version(3.6, reason="Output differs on Python 3.6"), only_pp]
						),
				pytest.param(
						"3.7-pypy", marks=[only_version(3.7, reason="Output differs on Python 3.7"), only_pp]
						),
				pytest.param("3.8", marks=only_version(3.8, reason="Output differs on Python 3.8")),
				pytest.param("3.9", marks=only_version(3.9, reason="Output differs on Python 3.9")),
				pytest.param("3.10", marks=only_version("3.10", reason="Output differs on Python 3.10")),
				]
		)

# TODO: check_modules


@platforms
def test_cli(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		platform: str,
		demo_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--no-colour"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


@platforms
def test_cli_verbose(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		platform: str,
		demo_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--verbose"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


def test_cli_verbose_errors(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		errored_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--verbose"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 1


@versions
def test_cli_verbose_verbose_errors(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		errored_environment,
		version,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--verbose", "--verbose"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 1


@versions
def test_cli_errors_show(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		errored_environment,
		version,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--show", "--no-colour"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 1


def test_cli_errors_count(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		errored_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--count", "--no-colour"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 1


@pytest.mark.parametrize("args", [
		("collections", "importlib", "--count"),
		("collections", "--count"),
		])
def test_cli_count_modules_as_args(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		args,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=[*args, "--no-colour"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


@pytest.mark.skipif(click.__version__.split(".")[0] != "7", reason="Output differs on Click 8")
def test_cli_help(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--help", "--no-colour"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


@pytest.mark.skipif(click.__version__.split(".")[0] == "7", reason="Output differs on Click 8")
def test_cli_help_click8(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--help", "--no-colour"])

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


def test_cli_bad_config(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = [ "setuptools>=40.6.0", "wheel>=0.34.2",]',
			'build-backend = "setuptools.build_meta"',
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--no-colour"])

	assert not result.stdout
	assert result.exit_code == 1
	advanced_file_regression.check(fix_stdout(result.stderr))


@pytest.mark.parametrize("verbosity", [0, 1, 2])
def test_cli_no_op(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		verbosity: int,
		):

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = [ "setuptools>=40.6.0", "wheel>=0.34.2",]',
			'build-backend = "setuptools.build_meta"',
			'',
			"[tool.importcheck]",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner()
		result: Result = runner.invoke(main, args=["--no-colour"] + (["--verbose"] * verbosity))

	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


def test_cli_stdin(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=['-', "--no-colour"], input="collections importlib functools")

	assert not result.stderr
	advanced_file_regression.check(fix_stdout(result.stdout))
	assert result.exit_code == 0


def test_cli_version(tmp_pathplus: PathPlus, ):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--version"])

	assert not result.stderr
	assert fix_stdout(result.stdout) == "importcheck version 0.0.0"
	assert result.exit_code == 0
