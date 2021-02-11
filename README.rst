############
importcheck
############

.. start short_desc

**A tool to check all modules can be correctly imported.**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy| |pre_commit_ci|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/importcheck/latest?logo=read-the-docs
	:target: https://importcheck.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/domdfcoding/importcheck/workflows/Docs%20Check/badge.svg
	:target: https://github.com/domdfcoding/importcheck/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/domdfcoding/importcheck/workflows/Linux/badge.svg
	:target: https://github.com/domdfcoding/importcheck/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/importcheck/workflows/Windows/badge.svg
	:target: https://github.com/domdfcoding/importcheck/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/domdfcoding/importcheck/workflows/macOS/badge.svg
	:target: https://github.com/domdfcoding/importcheck/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/domdfcoding/importcheck/workflows/Flake8/badge.svg
	:target: https://github.com/domdfcoding/importcheck/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/domdfcoding/importcheck/workflows/mypy/badge.svg
	:target: https://github.com/domdfcoding/importcheck/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://requires.io/github/domdfcoding/importcheck/requirements.svg?branch=master
	:target: https://requires.io/github/domdfcoding/importcheck/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/domdfcoding/importcheck/master?logo=coveralls
	:target: https://coveralls.io/github/domdfcoding/importcheck?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/importcheck?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/importcheck
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/importcheck
	:target: https://pypi.org/project/importcheck/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/importcheck?logo=python&logoColor=white
	:target: https://pypi.org/project/importcheck/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/importcheck
	:target: https://pypi.org/project/importcheck/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/importcheck
	:target: https://pypi.org/project/importcheck/
	:alt: PyPI - Wheel

.. |license| image:: https://img.shields.io/github/license/domdfcoding/importcheck
	:target: https://github.com/domdfcoding/importcheck/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/importcheck
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/importcheck/v0.2.0
	:target: https://github.com/domdfcoding/importcheck/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/importcheck
	:target: https://github.com/domdfcoding/importcheck/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2021
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/importcheck
	:target: https://pypi.org/project/importcheck/
	:alt: PyPI - Downloads

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/domdfcoding/importcheck/master.svg
	:target: https://results.pre-commit.ci/latest/github/domdfcoding/importcheck/master
	:alt: pre-commit.ci status

.. end shields

Installation
--------------

.. start installation

``importcheck`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install importcheck

.. end installation
