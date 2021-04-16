Release checklist for maintainers
=================================

.. note::

   For demonstration's sake, we assume that the next version is ``$VERSION``
   and the package name is ``$PACKAGE``::

      PACKAGE=snek5000; VERSION=...

- Ensure tests pass locally and on CI::

      pytest

- Update changelog with by inspecting list of
  :ref:`unreleased changes <changelog/unreleased>`

.. - Compile changelog from `news fragments`_ and verify the output, for example::
..
..       towncrier build --version $VERSION --draft
..
.. - Apply the changelog to ``CHANGES.rst`` and edit the links as required::
..
..       towncrier build --version $VERSION

- Compile documentation::

      cd docs/
      make html

- Commit changes and tag a release::

      git commit
      git tag $VERSION

- Prepare source distribution package and wheel::

      rm -rf dist
      python setup.py sdist bdist_wheel

- Verify the package with twine::

      twine check dist/*

- Upload to TestPyPI_ and verify::

      twine upload --repository testpypi dist/*
      cd /tmp
      python -m venv testpypi
      source testpypi/bin/activate
      pip install \
          --index-url https://test.pypi.org/simple \
          --extra-index-url https://pypi.org/simple \
          $PACKAGE

- Upload to PyPI_::

      twine upload dist/*

.. _TestPyPI: https://packaging.python.org/guides/using-testpypi/
.. _PyPI: https://pypi.org/
