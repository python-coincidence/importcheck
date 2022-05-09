# stdlib

# stdlib
from typing import Iterable

# 3rd party
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture, AdvancedFileRegressionFixture
from coincidence.selectors import only_version
from domdf_python_tools.paths import PathPlus

# this package
from importcheck import ImportChecker


@pytest.mark.parametrize(
		"modules",
		[
				pytest.param(("collections", "importlib"), id="collections_importlib"),
				pytest.param(("importlib", ), id="importlib"),
				pytest.param(("collections", ), id="collections"),
				pytest.param((), id="empty"),
				]
		)
@pytest.mark.parametrize("show", [True, False])
def test_importchecker(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		modules: Iterable[str],
		show: bool,
		) -> None:

	checker = ImportChecker(modules, show=show)

	advanced_data_regression.check(dict(checker.check_modules()))
	advanced_file_regression.check(checker.format_statistics())


@pytest.mark.parametrize(
		"version",
		[
				pytest.param(3.6, marks=only_version(3.6, reason="Output differs on Python 3.6")),
				pytest.param(3.7, marks=only_version(3.7, reason="Output differs on Python 3.7")),
				pytest.param(3.8, marks=only_version(3.8, reason="Output differs on Python 3.8")),
				pytest.param(3.9, marks=only_version(3.9, reason="Output differs on Python 3.9")),
				pytest.param("3.10", marks=only_version("3.10", reason="Output differs on Python 3.10")),
				pytest.param("3.11", marks=only_version("3.11", reason="Output differs on Python 3.11")),
				]
		)
@pytest.mark.parametrize("show", [True, False])
def test_importchecker_errors_show(
		tmp_pathplus: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		advanced_data_regression: AdvancedDataRegressionFixture,
		version: str,
		show: bool,
		) -> None:

	checker = ImportChecker(
			["collections", "i_dont_exist", "this-is&invalid", "domdf_python_tools", "coincidence"],
			show=show,
			)

	advanced_data_regression.check(dict(checker.check_modules()))
	advanced_file_regression.check(checker.format_statistics())
