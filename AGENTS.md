# AGENTS.md

Guidance for AI coding agents working on the **diagrams** project
(online-diagrams, https://github.com/BITPlan/diagrams).

## PLAN AND ASK BEFORE DO

NEVER perform any action (reading, modifying, running) without first
explaining the plan and waiting for positive confirmation (`go!`).

Format:
> I understood that `<ANALYSIS>` so that I plan to `<GOALS>` by
> `<ACTIONS TO BE CONFIRMED>` estimating `<# ITEMS>` `<ITEMS>`. confirm with go!

## DMAIC

Follow the DMAIC principle (Define, Measure, Analyze, Improve, Control).
Before starting work, read the known-problems log to avoid repeating past
mistakes:
- https://media.bitplan.com/index.php/AGENTS-DMAIC
- https://media.bitplan.com/index.php/Agents (wiki id: `media`)

## Security

NEVER leak credentials, passwords (even hashed), internal hostnames, IPs,
database names, usernames, or any infrastructure detail to public platforms
(GitHub issues/PRs, Discourse, public wiki pages). This is a firing offense.

## Project Layout

- `dgs/` — Python package (NiceGUI-based webserver, generators)
  - `dgs/diagrams_cmd.py` — CLI entry point (`diagrams`)
  - `dgs/ngwebserver.py` — web server based on `ngwidgets`
  - `dgs/__init__.py` — single source of truth for `__version__`
  - `dgs/version.py` — `Version` metadata (keep `updated` current)
- `diagrams_examples/` — example diagrams
- `tests/` — test suite (run with `green` or unittest)

## Conventions

- Version lives in `dgs/__init__.py`; bump it and the `updated` date in
  `dgs/version.py` together on each release.
- Depends on `ngwidgets`; APIs there change between releases. When an import
  breaks (e.g. a removed module), verify against the installed version before
  patching and prefer removing dead code over re-adding obsolete shims.
- Verify the import chain after dependency-related changes:
  `python -c "from dgs.diagrams_cmd import main"`

## Documentation

Daily / problem documentation goes to the MediaWiki at
https://media.bitplan.com (wiki id `media`) via the `wikipush` MCP, using
ISO-dated pages (e.g. `Qn_Migration/2026-06-11/diagrams`).
