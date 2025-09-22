licensecheck:
	liccheck -r src/requirements.txt

test:
    export PYTHONPATH='../src/' \
	pytest src/tests --cov-config pyproject.toml

install-pre-commit: install-test-requirements
	pre-commit install --install-hooks

uninstall-pre-commit:
	pre-commit uninstall
	pre-commit uninstall --hook-type pre-push
