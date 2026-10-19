# Development setup

Tooling is [mise](https://mise.jdx.dev) (installs python, uv and pre-commit, runs tasks) plus
[uv](https://docs.astral.sh/uv) (manages `.venv`, `uv.lock`, builds and publishes).

```
mise install        # python 3.12, uv, pre-commit; versions pinned in mise.toml
mise run install    # uv sync (.venv with editable tapper + extras + dev tools) and installs git hooks
mise tasks          # list everything below
```

| task                  | does                                                   |
|-----------------------|--------------------------------------------------------|
| `mise run test`       | pytest with coverage                                   |
| `mise run lint`       | ruff check + ruff format --check                       |
| `mise run fix`        | ruff auto-fix + format                                 |
| `mise run typecheck`  | pyright (config in `pyproject.toml`)                   |
| `mise run check`      | all three, same as CI                                  |
| `mise run upgrade`    | bump every pin in `uv.lock`, then re-sync `.venv`      |
| `mise run build`      | clean `dist/`, then sdist + wheel into it              |

### Other Python versions (what tox used to do)

tox's job (one isolated env per interpreter, same commands in each) is split between uv and mise:
uv's `uv.lock` is resolved for every Python in `requires-python`, and a mise *environment*
swaps the interpreter and venv while keeping the tasks identical. `mise.upper.toml` defines one
for the upper bound: the newest Python minor **minus one** (`sub-0.1:latest`, so 3.14 while 3.15
is current, moving up by itself when 3.16 is released). One minor behind the bleeding edge means
every dependency ships wheels for it, so a failure there is significant rather than noise.

```
mise -E upper install        # install that python
mise -E upper run install    # .venv-upper from the same uv.lock
mise -E upper run test       # or check, lint, typecheck, build ...
```

CI runs `mise run check` on ubuntu and windows for both 3.12 (default) and upper (`MISE_ENV=upper`).
Code must stay compatible with 3.12; the upper job is there to catch deprecations and dependency drift early.

With mise activated in your shell (`mise activate`), `.venv` is on PATH inside the repo,
so plain `python`, `pytest`, `ruff`, `pyright` and `uv` work directly. For anything without a task,
use uv or the venv directly, e.g. `python tests/manual/tapper_simple.py` to run a script. `pip install -e .` into any other
environment still works too (the build backend is `uv_build`).

Git hooks are the [pre-commit](https://pre-commit.com) framework, configured in `.pre-commit-config.yaml`.
The ruff and pyright hooks are `language: system` and call `uv run ...`, so they use the versions
in `uv.lock`, not separately downloaded ones. `uv` must be on PATH when git runs the hook, which
mise activation (or shims) provides. `pre-commit run --all-files` runs everything on the repo.

Dependencies live only in `pyproject.toml`: runtime deps and user extras (`tray`, `img`, `all`)
under `[project]`, contributor tools in `[dependency-groups] dev`. After editing them, run
`mise run install` to update `uv.lock` and the venv; commit `uv.lock`. To move every dependency
to its newest allowed version, run `mise run upgrade`, then `mise run check` before committing the lock.

### Using a local checkout from another project

The build backend (`uv_build`) supports editable installs, so another environment can depend on
this working tree and pick up edits without reinstalling:

```
pip install -e "/path/to/tapper[all]"          # plain pip, as before
uv pip install -e "/path/to/tapper[all]"       # same, via uv
uv add --editable ../tapper --extra all        # from another uv project
```

The last form records `tapper[all]` in that project's dependencies plus a
`[tool.uv.sources]` entry pointing at the path, so its `uv sync` keeps reinstalling from
your checkout. Prefer a relative path if the consumer is committed.

Caveat: pip downloads `uv_build` from PyPI to build the package, so an offline `pip install -e`
needs `--no-build-isolation` with `uv_build` already installed. uv caches the backend after
first use.

### Releasing

Bump `version` in `pyproject.toml` (CalVer `YYYY.M.MICRO`), update `CHANGELOG.md`, tag and publish
a GitHub release; `.github/workflows/publish.yml` builds and uploads to PyPI via trusted publishing
(no token; the repo + workflow must be registered once under the project's Publishing settings on pypi.org).

Manual upload, if ever needed: `mise run build`, then `uv publish` with a project-scoped PyPI API token
in `UV_PUBLISH_TOKEN` (set it inline, or in the gitignored `mise.local.toml` under `[env]`).
