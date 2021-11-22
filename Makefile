dev:
	pip install -e .[dev]
	pip install --no-deps -e ./docs/examples/snek5000-canonical/

test:
	pytest

testslow:
	pytest -v --runslow

coverage_html:
	coverage html
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/html/index.html"

black:
	black src tests
