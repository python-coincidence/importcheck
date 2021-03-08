# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

pytest_plugins = ("coincidence", )


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
			'"platform_system == \\"Darwin\\"" = [ "plistlib",]',
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
