# Tools

This folder contains shared utilities and grouped projects used across the Pi Top Projects collection. It is intended to hold small, focused demos and helper modules that can be imported by challenge entry scripts placed at the repository root.

## Top-level file
### - `tools.py`
  - Purpose: a centralized collection of helper functions and small abstractions used by the subprojects. Typical contents include initialization helpers for the Pi-Top SDK, motor and sensor wrappers, logging helpers, configuration loaders, and safe shutdown functions.
  - Conventions:
    - Keep hardware-agnostic helpers here (e.g., logging, config parsing, math helpers).
    - If a function is only used by one subproject, prefer placing it inside that subproject to avoid tight coupling.
    - Keep `tools.py` small and easy to import from root-level challenge scripts.

## How to use
- Importing from a root script:
  - Example: `from Tools import tools` or `from Tools.OBJDET import cisoc`
  - If running from within the `Tools/` folder, Python's import path may require adding the repo root to `PYTHONPATH` or using a relative import. For challenge scripts kept at the repo root, imports should work out-of-the-box.

## Development tips
- Keep the helpers small and well-documented. Add docstrings to anything non-trivial in `tools.py` so it’s easy to reuse.
- Add small README files to subfolders (see the project-specific READMEs) to describe usage, wiring, and run instructions.
