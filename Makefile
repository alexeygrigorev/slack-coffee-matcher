build:
	bash build.sh

publish: build
	bash publish.sh

.PHONY: build publish