# Installation.

.PHONY:install
install:
	pnpm install

# Application.
.PHONY:fe
fe:
	pnpm dev

# Static analysis.

local_ci: lint

lint: check

.PHONY:format
format:
	pnpm format

.PHONY:check
check:
	pnpm lint
	pnpm tsc
	pnpm build
