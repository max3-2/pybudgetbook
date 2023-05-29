Steps to take when releasing a new version:
* Bump version number in `pybudgetbook/__init__.py`.
* Add the release notes to `releases.md`.
* Add a dedicated commit for the version bump.
* Tag the commit with the version number, use git tag -a tagname to specify message
* Push the commit (but not the tag)
* Publish to PyPI by running `deploy/publish.py`.
* Check that meta information is correct on PyPI.
* Then push the tag
