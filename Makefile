.PHONY: build ci compile docs lint local-check local-config local-down local-up services test

services:
	node scripts/list-services.mjs

compile:
	python3 -m compileall apps/services packages/python

lint:
	pnpm lint

local-check:
	pnpm local:check

local-config:
	pnpm local:config

local-up:
	docker compose -f infra/docker/compose.yaml up --build

local-down:
	docker compose -f infra/docker/compose.yaml down

test:
	pnpm test

build:
	pnpm build

ci: compile lint local-check test

docs:
	@find docs -type f | sort
