========
Usage
========

Command Line
--------------

.. click:: importcheck.__main__:main
	:prog: importcheck
	:nested: none


Configuration
--------------

``importcheck`` is configured in a `TOML <https://github.com/toml-lang/toml>`_ file.
By default this is `pyproject.toml <https://snarky.ca/what-the-heck-is-pyproject-toml/>`_,
but any other ``TOML`` file can be used by setting the :option:`-c` option.
In ``pyproject.toml``, the configuration is placed in the ``tool.importcheck`` table.
In other ``TOML`` files the configuration may also be placed in the top-level ``importcheck`` table.

The structure of the configuration is as follows:

* **always**: An array of strings giving modules which ``importcheck`` should always try to import.
* **only_if**: A table mapping :pep:`508` markers to arrays of strings giving modules which ``importcheck`` should try to import only if the markers evaluate to :py:obj:`True`. Each key may contain multiple markers.
* **config**: A mapping of internal configuration for ``importcheck``. The currently supported values are:

  + ``show`` (boolean) -- Sets a default value for :option:`-s / --show <-s>`.
  + ``count`` (boolean) -- Sets a default value for :option:`-C / --count <-C>`.

  These can be overridden on the command line.

|

**Example configuration**:

.. code-block:: toml

	[tool.importcheck]
	always = [ "mypackage", "mypackage.submodule",]

	[tool.importcheck.only_if]
	"sys_platform == \"linux\"" = [ "mypackage._linux_helpers",]

	[tool.importcheck.config]
	show = true
	count = true
