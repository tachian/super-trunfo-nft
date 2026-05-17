.PHONY: build ci compile docs lint services test

services:
	node scripts/list-services.mjs

compile:
	python -m compileall apps/services packages/python

lint:
	pnpm lint

test:
	pnpm test

build:
	pnpm build

ci: compile lint test

docs:
	@find docs -type f | sort

