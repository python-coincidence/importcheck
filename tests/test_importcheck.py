# stdlib
import platform
import re

# 3rd party
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture, check_file_regression
from coincidence.selectors import not_macos, not_windows, only_macos, only_version, only_windows
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from pytest_regressions.file_regression import FileRegressionFixture

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


@pytest.fixture()
def demo_environment(tmp_pathplus: PathPlus) -> PathPlus:

	filename = tmp_pathplus / "pyproject.toml"

	filename.write_lines([
			"[build-system]",
			'requires = [ "setuptools>=40.6.0", "wheel>=0.34.2",]',
			'build-backend = "setuptools.build_meta"',
			'',
			"[tool.importcheck]",
			'always = [ "collections", "pathlib", "importcheck", "domdf_python_tools", "coincidence",]',
			'',
			"[tool.importcheck.only_if]",
			'"platform_system == \\"Windows\\"" = [ "msvcrt",]',
			'"platform_system == \\"Linux\\"" = [ "posix",]',
			'',
			"[tool.importcheck.config]",
			"show = true",
			"count = false",
			])

	return filename


@pytest.fixture()
def errored_environment(tmp_pathplus: PathPlus) -> PathPlus:

	filename = tmp_pathplus / "pyproject.toml"

	filename.write_lines([
			"[build-system]",
			'requires = [ "setuptools>=40.6.0", "wheel>=0.34.2",]',
			'build-backend = "setuptools.build_meta"',
			'',
			"[tool.importcheck]",
			'always = [ "collections", "i_dont_exist", "this-is&invalid", "domdf_python_tools", "coincidence",]',
			])

	return filename


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

versions = pytest.mark.parametrize(
		"version",
		[
				pytest.param(3.6, marks=only_version(3.6, reason="Output differs on Python 3.6")),
				pytest.param(3.7, marks=only_version(3.7, reason="Output differs on Python 3.7")),
				pytest.param(3.8, marks=only_version(3.8, reason="Output differs on Python 3.8")),
				pytest.param(3.9, marks=only_version(3.9, reason="Output differs on Python 3.9")),
				pytest.param("3.10", marks=only_version("3.10", reason="Output differs on Python 3.10")),
				]
		)


@platforms
def test_cli(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		platform: str,
		demo_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--no-colour"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 0


@platforms
def test_cli_verbose(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		platform: str,
		demo_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--verbose"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 0


def test_cli_verbose_errors(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		errored_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--verbose"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")

	assert result.exit_code == 1


@versions
def test_cli_verbose_verbose_errors(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		errored_environment,
		version,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--verbose", "--verbose"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")

	assert result.exit_code == 1


@versions
def test_cli_errors_show(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		errored_environment,
		version,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--show", "--no-colour"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 1


def test_cli_errors_count(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		errored_environment,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--count", "--no-colour"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 1


@pytest.mark.parametrize("args", [
		("collections", "importlib", "--count"),
		("collections", "--count"),
		])
def test_cli_count_modules_as_args(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		args,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=[*args, "--no-colour"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 0


def test_cli_help(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--help", "--no-colour"])

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 0


def test_cli_bad_config(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):

	(tmp_pathplus / "pyproject.toml").write_lines([
			"[build-system]",
			'requires = [ "setuptools>=40.6.0", "wheel>=0.34.2",]',
			'build-backend = "setuptools.build_meta"',
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result: Result = runner.invoke(main, args=["--no-colour"])

	assert result.exit_code == 1
	assert not result.stdout
	check_file_regression(fix_stdout(result.stderr), file_regression, extension=".txt")


@pytest.mark.parametrize("verbosity", [0, 1, 2])
def test_cli_no_op(
		tmp_pathplus: PathPlus,
		file_regression: FileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
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

	check_file_regression(fix_stdout(result.stdout), file_regression, extension=".txt")
	assert result.exit_code == 0
