# Cert SRS (cert-srs)

A spaced-repetition study app for the Databricks Data Engineer Associate exam, formerly CertAnki. It runs as one self-contained HTML page published as a claude.ai artifact, with its cards and everyone's review history in that artifact's database.

- Live page: https://claude.ai/artifact/RsCDTyFr4Sd81qV4bpWV52
- Spec: https://claude.ai/artifact/RkurXmhGDeS9HnC3d2V35N

Precedence: the spec wins over README.md, and README.md wins over this file. README.md is the reference for design decisions, the database layout, the card rules and the capabilities JSON; this file covers how work flows from the repo to the live app.

## How it ships

The repo is the source of truth for code and card content. The artifact is the deploy target, and it has two independent release paths:

| Path | What changes | Tool | Source in the repo |
| --- | --- | --- | --- |
| **Page release** | The app's HTML/JS, including the inlined scheduler | `Artifact` (publish) | `app/build/cert-srs.html` |
| **Content release** | Exam blueprint and concept documents in the database | `ArtifactData` (`write_db` batch) | `content/out/*.json` |

Republishing the page leaves the database untouched, so review history survives every page release. Live data stays in the artifact: the repo holds the code that produces and checks content, never database dumps, backups or review rows.

## Layout

| Path | Role |
| --- | --- |
| `scheduler/scheduler.js` | Scheduler core (FSRS-6 via ts-fsrs 5.4.2). Inlined unchanged into the page. |
| `app/app.src.html` | The page source, with a `/*__SCHEDULER__*/` placeholder. |
| `app/build.js` | Writes `build/cert-srs.html` (what gets published) and `test.html` (ts-fsrs inlined from `scheduler/node_modules`, for tests). |
| `app/*.test.js`, `app/fakeclaude.js` | jsdom tests against an in-memory stand-in for the artifact database that enforces the same access rules. |
| `app/published-cert-srs.html` | Byte-for-byte copy of what is live. The baseline for every release. |
| `content/build_content.py` | Blueprint, the 10 sample concepts, the card-rule validator, the `REV` map of content revisions. Imports `batch_m3.py` (40 concepts in `CHUNKS`). Writes `content/out/` and `content/all.json`. |
| `content/db_versions.json` | Database versions as of 2026-11-09; no longer maintained (see Content release). |
| `tools/snapshot.py`, `tools/restore_content.py` | Turn a `read_db` dump into a backup file; split a backup into `write_db` batches. |
| `tools/live_compare.py` | Compares a saved `Artifact` read of the live page with a local file, ignoring the document skeleton publishing adds. |
| `.mise.toml` | Toolchain pins (node, python, uv) and the `.venv` virtualenv mise creates and activates. |
| `.mise/tasks/` | mise file tasks, one executable script per task. A subfolder is a task group: `.mise/tasks/app/test` runs as `mise run app:test`, and a group's `_default` script runs as the bare group name. |

Generated and ignored: `app/build/`, `app/test.html`, `content/out/`, `content/all.json`, `.venv/`.

## Toolchain and tasks (mise)

mise manages the toolchain and runs every development command. Run work through `mise run <task>`, not through bare `node`, `npm`, `python3` or `cd` chains: the task sets the working directory, uses the pinned tools and the `.venv`, and runs its dependencies first. `mise tasks` lists them all.

| Task | Does |
| --- | --- |
| `setup:node` | `npm ci` in `scheduler/` and `app/` (skipped while the lockfiles are unchanged) |
| `setup:python` | Optional-check packages into `.venv` (bs4, markdownify, lxml, fsrs 6.3.2, Playwright + Chromium) |
| `setup` | Both of the above |
| `content:build` | `build_content.py`: validator, `content/out/`, `content/all.json` |
| `content:factcheck [prefix...]` | `factcheck.py`; needs `setup:python` and network |
| `scheduler:test` | Scheduler unit tests |
| `scheduler:pacing` | Pacing simulation |
| `scheduler:crosscheck` | ts-fsrs and py-fsrs runs of the scripted history; needs `setup:python` |
| `app:build` | `build/cert-srs.html` and `test.html` |
| `app:test` | Content build, app build, then the ui, replay, real, m4 and share tests |
| `test` | Full check: content, scheduler tests, pacing, app tests |
| `release:diff` | Rebuild and diff against `app/published-cert-srs.html` |
| `release:compare <read> [file]` | Compare a saved live read with `app/published-cert-srs.html` (or the given file) |
| `release:record` | Copy the build to `app/published-cert-srs.html` and print the tag to make |

Rules for tasks:

- A new repeatable command becomes a script in `.mise/tasks/`, in the group subfolder it belongs to (`setup`, `content`, `scheduler`, `app`, `release`); a task that spans groups stays at the top level. Make it executable, start it with `#!/usr/bin/env bash` and `set -euo pipefail`, and set its properties in `#MISE` header lines (`description`, `dir="{{config_root}}/<folder>"`, `depends`). Extra command-line args reach the script as `"$@"`.
- Express ordering with `depends`, not by chaining commands inside a script.
- Change tool versions in `.mise.toml` only, then run `mise install`.
- One-off commands that need no task (an `m4.test.js` run with `CERT_SRS_SNAPSHOT`, a single screenshot script) still run with the pinned tools: `mise exec -- node ...` or `mise exec -- python ...`, from the folder the README gives.

## Building and testing

`mise run test` builds the content, runs the scheduler tests and pacing simulation, and runs the app tests, in dependency order (`app/build.js` reads ts-fsrs from `scheduler/node_modules`; the app tests read `content/all.json`). On a fresh clone run `mise install` first.

Optional checks that need extra installs: `mise run setup:python`, then `content:factcheck` or `scheduler:crosscheck`. The Playwright screenshot scripts and the patched py-fsrs comparison are in README.md under "Running it".

## Page release

Each step ends when its check holds.

1. **Baseline.** `Artifact` read of the live URL, then `mise run release:compare <saved read>`. Done when it reports the live page identical to `app/published-cert-srs.html`. (Publishing wraps the page in a one-line document skeleton; the compare strips it.) If it differs, the live page was changed outside the repo: stop and show Josh the difference, so the change can be brought into `app.src.html` first.
2. **Edit source.** Change `app/app.src.html` and/or `scheduler/scheduler.js`. Bump versions in pairs: `APP_VERSION` in `app.src.html` with `app/package.json`; `VERSION` in `scheduler.js` with `scheduler/package.json`. Tests pin the scheduler version string, so update those assertions with a scheduler bump.
3. **Test.** `mise run test`. Done when every test passes.
4. **Review the build.** `mise run release:diff`. Done when every changed line is one you intended.
5. **Publish.** `Artifact` publish with `file_path` `app/build/cert-srs.html`, `url` set to the live page, and `capabilities` copied verbatim from README.md, "Publishing and the database". Expect an approval prompt, since the publish declares capabilities. A capabilities change goes into README.md in the same commit.
6. **Confirm.** `Artifact` read of the live URL, then `mise run release:compare <saved read> app/build/cert-srs.html`. Done when it reports them identical.
7. **Record.** `mise run release:record` (copies `app/build/cert-srs.html` to `app/published-cert-srs.html`), then commit and tag `v<app version>`.

To try a change without touching the live page, publish the build without `url`. That creates a separate private artifact with an empty database.

## Content release

From 2026-11-09 the artifact database is the master copy of content, and content is managed from claude.ai: the Cert SRS Project's `weekly-review` doc is the procedure. This repo keeps the tooling and is read-only to those sessions; nothing there needs a push. `content/build_content.py` and the batch modules are the archive of how content was written up to 2026-11-09, and `content/db_versions.json` is no longer maintained (each run pins writes to the versions it reads).

The tools a claude.ai session uses on a `read_db` dump:

1. `tools/workspace.py init <dump> <ws>`: copies `exams/` and `concepts/` into an editable workspace plus an untouched `base/`, and writes `<ws>/all.json`. After edits, `workspace.py build <ws>`.
2. `tools/validate.py <ws>`: the card-rule validator, shared with `build_content.py`.
3. `content/factcheck.py --all <ws>/all.json [ids]`: tests each concept's own `evidence` field ([source index, regex] pairs) against its sources.
4. `CERT_SRS_ALL=<ws>/all.json node app/play_chunk.js <lo> <hi>` and `app/shots_batch.py` with the same variable.
5. `tools/workspace.py diff <ws> <versions.json>`: lists changed and new documents and writes pinned `write_db` batches.

## Database boundaries

Releases write only `exams/`, `concepts/` and `heldout/`. The `data/users/` and `reports/` paths belong to the app and its users. Chat touches them only when Josh asks to resolve flags, process notes or close reports, using the fields README.md documents. Backups and `read_db` dumps go to a scratch folder outside the repo.

Review rows written before app 1.3.2 carry `sched: "certanki-sched/1.1.0"` (the project's old name). Treat it as the same scheduler as `cert-srs-sched/1.1.0`.

## The claude.ai Project

The Project reads the code from the public GitHub repo (https://github.com/JoshuaBotha/cert-srs). Push after every release so it sees the current code.
