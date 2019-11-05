.DEFAULT_GOAL := help
pkg_src = example
tests_src = tests

isort = isort -rc $(pkg_src) $(tests_src)
autoflake = autoflake -r --remove-all-unused-imports --ignore-init-module-imports $(pkg_src) $(tests_src)
black = black $(pkg_src) $(tests_src)
flake8 = flake8 $(pkg_src) $(tests_src)
mypy_base = mypy --show-error-codes
mypy = $(mypy_base) $(pkg_src)
mypy_tests = $(mypy_base) $(pkg_src) $(tests_src)

.PHONY: all  ## Run the most common rules used during development
all: format lint mypy-tests test

.PHONY: format  ## Auto-format the source code (isort, autoflake, black)
format:
	$(isort)
	$(autoflake) -i
	$(black)

.PHONY: check-format  ## Check the source code format without changes
check-format:
	$(isort) --check-only
	@echo $(autoflake) --check
	@( set -o pipefail; $(autoflake) --check | (grep -v "No issues detected!" || true) )
	$(black) --check

.PHONY: lint  ## Run flake8 over the application source and tests
lint:
	$(flake8)

.PHONY: mypy  ## Run mypy over the application source
mypy:
	$(mypy)

.PHONY: mypy-tests  ## Run mypy over the application source *and* tests
mypy-tests:
	$(mypy_tests)

.PHONY: test  ## Run tests
test:
	./scripts/dev/test.sh
	@echo "All tests passed"

.PHONY: testcov  ## Run tests, generate a coverage report, and open in browser
testcov:
	./scripts/dev/testcov.sh
	@echo "opening coverage html in browser"
	@open htmlcov/index.html

.PHONY: default  ## CI-friendly checks
default: check-format lint mypy test

.PHONY: regenerate  ## Regenerate the example client
regenerate:
	./scripts/dev/regenerate-example.sh
	@echo "Regeneration succeeded"

.PHONY: clean  ## Run all CI validation steps without making any changes to code
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf `find . -type d -name '*.egg-info' `
	rm -rf `find . -type d -name 'pip-wheel-metadata' `
	rm -rf `find . -type d -name 'tmp*' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf generated

.PHONY: lock  ## Update the lockfile
lock:
	poetry lock

.PHONY: develop  ## Set up the development environment, or reinstall from the lockfile
develop:
	./scripts/dev/install.sh

.PHONY: version  ## Bump the version in pyproject.toml (usage: `make version version=minor`)
version:
	poetry version $(version)

.PHONY: help  ## Display this message
help:
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-16s\033[0m %s\n", $$2, $$3}'
