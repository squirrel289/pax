---
name: migrate-pip-to-uv
category: tools
license: MIT
description: Skill to migrate a monorepo Python project from pip/pip-tools to uv, converting requirements files to pyproject.toml and uv.lock, and updating workflows for universal, locked, multi-group dependencies.
keywords: [migration, pip, uv, monorepo, python, requirements, pyproject.toml, lockfile]
---

# Migrate pip/pip-tools Monorepo to uv

A skill for automating the migration of a Python monorepo project from pip/pip-tools workflows (requirements files, pip-compile, etc) to uv's project workflow (pyproject.toml, uv.lock, universal resolution).

## Purpose

- Convert requirements files (requirements.in, requirements.txt, requirements-dev.in, requirements-dev.txt, etc) to pyproject.toml and uv.lock
- Migrate development, docs, and platform-specific dependency groups
- Ensure universal, locked dependencies for all platforms
- Update project workflows to use uv commands and environments

## Workflow Steps

1. **Analyze Existing Requirements Files**
   - Detect requirements.in, requirements.txt, requirements-dev.in, requirements-dev.txt, requirements-docs.in, requirements-docs.txt, etc
   - Identify platform-specific requirements files (e.g. requirements-win.txt, requirements-linux.txt)
2. **Initialize uv Project**
   - Run `uv init` to create pyproject.toml if not present
3. **Import Base Dependencies**
   - Run `uv add -r requirements.in -c requirements.txt` to preserve locked versions
4. **Import Development Dependencies**
   - Run `uv add --dev -r requirements-dev.in -c requirements-dev.txt`
   - If requirements-dev.in includes `-r requirements.in`, strip those lines before import
5. **Import Docs/Other Groups**
   - Run `uv add -r requirements-docs.in -c requirements-docs.txt --group docs` (repeat for other groups)
6. **Import Platform-Specific Constraints**
   - For each platform file, use `uv pip compile requirements.in -o requirements-<platform>.txt --python-platform <platform> --no-strip-markers`
   - Add with `uv add -r requirements.in -c requirements-win.txt -c requirements-linux.txt ...`
7. **Import Dependency Sources**
   - For local paths or git dependencies, ensure they are mapped in `[tool.uv.sources]` in pyproject.toml
8. **Sync and Lock**
   - Run `uv lock` to generate uv.lock
   - Run `uv sync` to create .venv and sync environment
9. **Update Project Workflows**
   - Replace pip/pip-tools commands with uv equivalents (e.g. `uv run pytest`)
   - Document new workflow in README.md

## Example Usage

```plaintext
migrate-pip-to-uv
```

## Example Migration Commands

- `uv init`
- `uv add -r requirements.in -c requirements.txt`
- `uv add --dev -r requirements-dev.in -c requirements-dev.txt`
- `uv add -r requirements-docs.in -c requirements-docs.txt --group docs`
- `uv pip compile requirements.in -o requirements-win.txt --python-platform windows --no-strip-markers`
- `uv add -r requirements.in -c requirements-win.txt -c requirements-linux.txt`
- `uv lock`
- `uv sync`
- `uv run pytest`

## Best Practices

- Use pyproject.toml for all dependency groups
- Use uv.lock for universal, platform-agnostic locking
- Prefer uv run for all commands in the environment
- Document migration steps and new workflow for contributors
- Remove obsolete requirements files after migration

## References

- [uv migration guide](https://docs.astral.sh/uv/guides/migration/pip-to-project/)
- [uv concepts: projects](https://docs.astral.sh/uv/concepts/projects/)
- [uv universal resolution](https://docs.astral.sh/uv/concepts/resolution/#universal-resolution)
- [uv dependency sources](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-sources)
