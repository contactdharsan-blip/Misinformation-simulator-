# Repository Guidelines

## Project Structure & Module Organization
- `sim/` contains the core simulation engine (cognition, dynamics, world, town, metrics, io, dashboard).
- `configs/` holds scenario YAMLs (e.g., `configs/world_baseline.yaml`).
- `tests/` contains pytest suites (`test_*.py`).
- `scripts/` includes validation and analysis helpers.
- `docs/` and root `*.md` files capture methods, architecture, and research notes.
- `runs/` is the default output location for simulation artifacts.

## Build, Test, and Development Commands
- `uv venv` then `uv pip install -e .` sets up a local dev environment (recommended).
- `python -m venv .venv` then `pip install -e .` is the pip alternative.
- `pip install -e ".[dev]"` installs dev tools (pytest, ruff, mypy).
- `python -m sim run --config configs/world_baseline.yaml --out runs/baseline/` runs a baseline sim.
- `python -m sim sweep --configs configs/world_*.yaml --out runs/sweep/` runs multi-config sweeps.
- `python -m sim dashboard --run runs/baseline/` launches the Streamlit dashboard.

## Coding Style & Naming Conventions
- Python 3.11+ with PEP 8 conventions and type hints on function signatures.
- Formatting via `ruff format sim tests`; lint via `ruff check sim tests`.
- Line length is 100 (see `pyproject.toml`).
- Keep function names descriptive; modules align with domain areas (e.g., `sim/cognition/`).

## Testing Guidelines
- Framework: pytest (configured in `pyproject.toml`).
- Test files live in `tests/` and use the `test_*.py` naming pattern.
- Run all tests with `python -m pytest`.
- Add tests for new functionality; validation tests are expected for new research claims.

## Commit & Pull Request Guidelines
- Git history shows short, sentence-case summaries (e.g., “Add emotion presets…”); no strict convention enforced.
- Use feature branches (`feature/your-feature`) and open PRs from forks.
- PRs should include a clear description and confirm quality checks were run (tests, ruff, mypy).

## Configuration & Outputs
- Simulation outputs include `summary.json`, `daily_metrics.csv`, and `run_metadata.json` in the run folder.
- For reproducibility, keep configs in `configs/` and point runs to `runs/...` paths.
