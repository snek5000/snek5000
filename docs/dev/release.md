# How to release

## Via GitHub Actions

- Update [Unreleased](../CHANGELOG.md#unreleased) with version comparison links and
  detailed description.
- Update version and date in `CITATION.cff`.
- Make a [new release] on Github.
- Inspect upload in [TestPyPI].
- Execute manual [deploy workflow] to download from [TestPyPI], run tests and publish to
  [PyPI].

## Manual method (not recommended)

```{note}
For demonstration's sake, we assume that the next version is `$VERSION`.
```

- Install nox:

  ```sh
  pip install nox
  ```

- Ensure tests pass locally and on CI:

  ```sh
  nox -s tests
  ```

- Compile documentation:

  ```sh
  nox -s docs
  ```

- Commit changes and make an annotated tag:

  ```sh
  git commit
  git tag -a $VERSION
  ```

- Build and upload to [TestPyPI]:

  ```sh
  nox -s testpypi
  ```

- Download, test and upload to [PyPI]:

  ```sh
  nox -s pypi
  ```

- Upload to repository:

  ```sh
  git push --follow-tags --atomic origin main
  ```

[deploy workflow]: https://github.com/snek5000/snek5000/actions/workflows/deploy.yaml
[new release]: https://github.com/snek5000/snek5000/releases/new
[pypi]: https://pypi.org/project/snek5000/
[testpypi]: https://test.pypi.org/project/snek5000/
