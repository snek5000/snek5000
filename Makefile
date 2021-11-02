dev:
	pip install -e .[dev]

test:
	pytest

testslow:
	pytest --runslow

coverage_html:
	coverage html
	@echo "Code coverage analysis complete. View detailed report:"
	@echo "file://${PWD}/.coverage/html/index.html"

black:
	black src tests
