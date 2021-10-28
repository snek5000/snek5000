dev:
	pip install -e .[dev]

test:
	pytest

testslow:
	pytest --runslow
