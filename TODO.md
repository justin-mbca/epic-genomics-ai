# Project TODO

This file was generated from the agent's internal task list.

- [x] Restore minimal Mermaid diagram
  - Keep a minimal, GitHub-safe Mermaid flowchart in `README.md` (done).
- [x] Add legend below diagram
  - Provide one-line descriptions under the diagram in `README.md` (done).
- [x] Commit & push README changes
  - Commit README edits and push to `origin main` (done).
- [ ] Verify rendering on GitHub
  - Open the repo page and confirm the Mermaid diagram renders and legend shows; report any parse errors to fix.
- [ ] Push current branch
  - Run `git push origin main` to ensure latest commits are on remote.
- [ ] Run linter (ruff) and fix issues
  - Run ruff over the repo and fix Python/notebook lint warnings (notebooks need imports at top of cells, remove unused imports).
- [ ] Run smoke tests
  - Run existing smoke test script(s) to validate ETL and DB outputs (e.g., `tests/smoke_test_run_etl.py`).
- [ ] Decide on Git LFS migration
  - If you want to keep large artifacts, install git-lfs and plan migration; otherwise keep artifacts out of repo.
- [ ] Finalize notebook hygiene
  - Finish notebook linting, ensure bootstrap cell present, remove unneeded diagnostic cells, commit cleaned notebooks.
- [ ] Add CI: lint + tests
  - Add simple CI workflow to run ruff and smoke tests on push (GitHub Actions).
