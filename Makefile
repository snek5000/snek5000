NOX ?= nox

.PHONY: Makefile

dev:
	pip install -e .[dev]
	pip install --no-deps -e ./docs/examples/snek5000-canonical/
	pip install --no-deps -e ./docs/examples/snek5000-tgv/

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

list-sessions:
	@nox --version 2>/dev/null || pip install nox
	@$(NOX) -l

# Catch-all target: route all unknown targets to nox sessions
%: Makefile
	@nox --version 2>/dev/null || pip install nox
	@$(NOX) -s $@
