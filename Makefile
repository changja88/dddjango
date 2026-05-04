.PHONY: release test-release

release:
	python3 scripts/release.py

test-release:
	python3 -m unittest discover -s tests
