init:
	pip install -r requirements.txt

test:
	@echo "Running Python tests"
	py.test --verbose --color=yes unittests.py

.PHONY: init test
