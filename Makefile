.PHONY: test lint contract policy helm verify

test:
	python -m pytest

lint:
	python -m ruff check .

contract:
	python -c "import yaml; yaml.safe_load(open('contracts/openapi/cloudspace-v1.yaml'))"

policy:
	opa fmt --fail policies && opa test policies

helm:
	helm lint deploy/helm/platform-api deploy/helm/console

verify:
	./ci/verify.sh
