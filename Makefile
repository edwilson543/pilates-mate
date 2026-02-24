.PHONY: run
run:
	cd backend && make api & cd frontend && make fe

.PHONY: local_ci
local_ci:
	cd backend && make local_ci & cd frontend && make local_ci
