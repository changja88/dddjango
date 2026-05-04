.PHONY: release publish test-release

release:
	python3 scripts/release.py

publish:
	python3 scripts/publish.py

test-release:
	python3 -m unittest discover -s tests
