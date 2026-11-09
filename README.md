# Cert SRS (cert-srs)

Spaced repetition for tech certs.

Cert SRS is a flashcard app inspired by Anki, built to prepare for technical certification exams. It schedules reviews with [FSRS-6](https://github.com/open-spaced-repetition/ts-fsrs), mixes recall cards with exam-style scenario questions, and estimates readiness per exam domain. The first deck covers the Databricks Data Engineer Associate exam. The app is one self-contained HTML page published as a claude.ai artifact, with cards and review history in that artifact's database.

Cert SRS was called CertAnki until November 2026. Review rows written before app 1.3.2 carry `certanki-sched/1.1.0` instead of `cert-srs-sched/1.1.0`; the scheduler is the same.

> **Disclaimer.** Cert SRS is an independent personal project. It is not affiliated with, endorsed by or sponsored by Databricks, Inc. or the Anki project. "Databricks" is a trademark of Databricks, Inc. The cards are original material written from the public Databricks documentation; they are not exam questions and may be wrong or out of date.

## Build package

Source, tests and content tooling for Cert SRS v1, as of 9 November 2026 (app 1.3.2, scheduler 1.1.0, content revisions 1–3).

**Milestone 3 done:** 50 concepts are live (the 10 samples plus the 40 in `content/batch_m3.py`, chunks 1–4): 85 tracks and 335 variants, 35 concepts with a scenario track, 7 pick-two variants and 23 constraint-flip pairs.

**Milestone 4 done:** Progress (readiness estimate per domain and overall, the formula one tap away, coverage), Notes (missed Academy questions, Academy practice scores, open flags) and Settings (exam date, daily minutes, JSON backup and restore). The scheduler is unchanged.

**Sharing (app 1.3.0):** the app can be shared with colleagues in the org. The page reads `user.isOwner()` at boot. The owner sees exactly the 1.2.0 app (private flags and notes for the weekly session), plus a **From colleagues** inbox at the top of Notes with a Mark done button on each item. Everyone else gets a one-time welcome (beta, not official Databricks material), colleague-facing copy wherever the page used to mention the Project chat or the weekly session, an About section in Settings, and backups of their own rows only. Their flags, **Send feedback** messages and ticked **Suggest a card** missed questions go to `reports/{their id}/items` instead of private rows. Share at **Contributor**: Viewers and Commenters can't save anything, not even their own progress, and Editors can read every report.

- App: https://claude.ai/artifact/RsCDTyFr4Sd81qV4bpWV52
- Spec: https://claude.ai/artifact/RkurXmhGDeS9HnC3d2V35N (the spec wins wherever this package and it disagree)

Content and your review history live only in the app's artifact database. This package holds the code that produces and checks them, not the data itself.

## Layout

| Folder | What it holds |
| --- | --- |
| `scheduler/` | `scheduler.js`, the scheduler core the app inlines unchanged: FSRS-6 via ts-fsrs 5.4.2, variant rotation, the 20-minute budget, the new-material throttle, learn-ahead, option drawing. Plus its tests, the py-fsrs cross-check and the pacing simulation. |
| `app/` | `app.src.html` (the page, with a placeholder where the scheduler is inlined), `build.js`, a jsdom harness with an in-memory stand-in for the artifact database, Playwright screenshot scripts, and `published-cert-srs.html`, a copy of the live page. |
| `content/` | `build_content.py`: the exam blueprint (August 2026 guide), the 10 sample concepts and the card-rule validator; it imports `batch_m3.py`, the milestone 3 concepts written in chunks, each with an `EVIDENCE` list. `factcheck.py` opens every source page those concepts link (HTTP 200, no redirects) and tests each evidence line against it. `db_versions.json` records each document's database version, for pinned updates. Writes one JSON file per document to `content/out/` and `content/all.json` for the tests. |
| `sim/` | The original pacing prototype from the design session (py-fsrs), kept for comparison. |
| `tools/` | `snapshot.py` turns a `read_db` dump (Artifact tool, `out_dir`) into one backup file in the app's format. `restore_content.py` splits a backup's content into files and `write_db` batches, since content is restored from chat. |

## Running it

Needs Node 18+ and Python 3.10+. Network access is needed once, for `npm install` and `pip install`.

With [mise](https://mise.jdx.dev), `mise install` pins the toolchain from `.mise.toml` and `mise run test` runs the whole sequence below except the optional checks; `mise tasks` lists the rest (scripts in `.mise/tasks/`). The plain commands below still work without mise.

```bash
# content first: the app tests read content/all.json
cd content && python3 build_content.py
pip install beautifulsoup4 markdownify lxml && python3 factcheck.py   # optional: concept-id prefixes narrow it

# scheduler
cd ../scheduler && npm install
node unit.test.js        # 11 tests
node pacing.sim.js       # 8 runs over 372 planned tracks, with and without the 20-minute cap
node ts_run.js           # scripted 47-review history through ts-fsrs -> ts_out.json

# py-fsrs cross-check
pip install fsrs==6.3.2
python3 py_run.py        # same history through py-fsrs -> py_out.json
# To compare like with like, apply pyfsrs-calendar-days.patch to a copy of py-fsrs,
# put that copy on PYTHONPATH, then run py_run.py and py_check.py.

# app
cd ../app && npm install
node build.js            # -> build/cert-srs.html (publish this) and test.html (local ts-fsrs, for tests)
node ui.test.js && node replay.test.js && node real.test.js
node share.test.js       # sharing: db rules, colleague flags/feedback/suggestions, owner inbox, Viewer can't save
CERT_SRS_SNAPSHOT=/path/to/backup.json node m4.test.js   # milestone 4 screens; the snapshot is optional (real rows for the restore round trip)
python3 shots_m4.py /path/to/backup.json                  # each new screen at 390x844, light and dark, fails on sideways scroll
pip install playwright && python3 shots_code.py "$PWD/test.html" shot   # phone-width screenshots
node play_chunk.js 11 50   # plays every variant of concepts with order 11-50 through the app, incl. a wrong pick per scenario track
python3 shots_batch.py test.html shot '[["dea-2-4-database-connector-parts","scenario","s1","ask"]]'   # chosen cards at 390x844
```

`shots.py` reads a `fixture.json`. Make it first with `node -e "process.stdout.write(JSON.stringify(require('./testdata.js')))" > fixture.json`.

`python3 tools/bundle.py` (from the repo root) writes `cert-srs-build.txt`, every file git tracks as one text file, for upload to the claude.ai Project.

## Decisions the tests rely on

**ts-fsrs and py-fsrs conventions.**

- They differ in two places:
  - **Elapsed days:** ts-fsrs counts calendar days (UTC); py-fsrs rounds the time gap down.
  - **Good versus Hard:** ts-fsrs keeps a Good interval at least one day longer than Hard, as Anki does.
- The app keeps ts-fsrs's behaviour.
- With the calendar-day patch applied, all 47 scripted reviews match. States are identical, difficulty agrees to 1e-8 and stability to 8e-6. The only due-date differences are the 7 cases of the Good-versus-Hard rule.

**Retrievability.** It's computed from the exact fractional elapsed time. ts-fsrs's `get_retrievability` rounds days down: checked 9 minutes before its due time, a card reads 0.947 instead of 0.910. Using that version inflated the simulated pass rate.

**Throttle.** New tracks per day are 9, 7, 5 or 2, set by the average measured minutes over the days studied in the previous 7 calendar days. The thresholds are 80%, 92.5% and 105% of the daily budget, and the counts scale if the budget changes.

**Learn-ahead (scheduler 1.1.0).** When nothing else is left, a missed card shows up to 20 minutes early, as in Anki. You never wait out the 10-minute step.

**Pacing.**

| Run | Weeks to introduce all | New tracks/day | Minutes/day while introducing | Minutes/day after |
| --- | --- | --- | --- | --- |
| With the 20-minute cap | 8.0 to 9.3 | 6.1 | 17.4 | 9.9 |
| Without the cap | 8.0 to 9.0 | 6.2 | 18.0 | about 10 |

The run without the cap matches the original prototype.

## Publishing and the database

The page is published with the Artifact tool from `app/build/cert-srs.html`, with these capabilities:

```json
{"db": {"rules": [{"path": "", "read": "view", "write": "owner"}, {"path": "data/users/{self}", "write": "interact"}, {"path": "reports", "read": "admin", "write": "owner"}, {"path": "reports/{self}", "read": "interact", "write": "interact"}]}, "downloads": true, "user": {"scopes": ["profile"]}}
```

In words: everyone reads cards and exams and only the owner writes them; each viewer's `data/users/` subtree is private, even from the owner; each colleague writes and reads only their own `reports/{id}`; the owner and any Editor read all reports, and only the owner can mark one done. `profile` scope lets the inbox show names; only ids are stored. `fakeclaude.js` (`viewAs`) enforces the same rules in the tests.

Every release publishes the full `app/build/cert-srs.html`; small changes go through the same build and tests as large ones.

| Path | Holds | Written by |
| --- | --- | --- |
| `exams/databricks-dea` | Blueprint: 7 domains, weights, 33 objectives, format | Chat (`write_db`) |
| `concepts/{id}` | One concept: setting terms, objective, sources, revision, both tracks' variants, diagrams | Chat (`write_db`) |
| `data/users/{me}/settings` | `exam`, `dailyMinutes`, `examDate` (YYYY-MM-DD, absent when unset), `retention` (defaults apply when absent); a save keeps unknown fields | App (Settings) |
| `data/users/{me}/state` | `days`: measured minutes and card count per study day, last 30 days | App |
| `data/users/{me}/state/tracks/{concept}:r` and `:s` | FSRS state, variants seen, last variant | App |
| `data/users/{me}/state/reviews/{ms}_{track}` | One row per review, including scheduler version and content revision | App |
| `data/users/{me}/state/flags/{ms}_{track}` | Reason, note and variant. Resolved from chat with `status`, `resolution`, `resolvedOn`, `fixedInRev` | App, then chat |
| `data/users/{me}/state/notes/{ms}_missed` | `t`, `kind: "missed"`, `status: "open"`, `where`, `question`, `mine`, `right`, `domain`, `exam`, `edited`. Processed from chat by setting `status: "processed"`, `processedOn` and `result` (shown under Processed) | App, then chat |
| `reports/{uid}` | `last`: time of the colleague's latest report. Exists so the owner can list who has sent anything | App (colleagues) |
| `reports/{uid}/items/{ms}_{rand}` | `t`, `kind` (`flag`, `missed` or `feedback`), `status: "open"`, `from`, `exam`, `app`. Flags add `track`, `concept`, `cardKind`, `variant`, `reason`, `note`, `contentRev`; missed adds the missed-question fields; feedback adds `text`. Closed with `status: "resolved"` and `resolvedOn`, from the inbox or from chat | App (colleagues), then owner |
| `data/users/{me}/state/notes/{ms}_score` | `t`, `kind: "score"`, `status`, `date`, `percent`, `questions`, `test`, `domains` (`{"2": "60%"}`), `note` | App, then chat |

Content goes in from chat as a `write_db` batch that reads each document from `content/out/` (`file_path`). Every write to an existing document is pinned with `if_version` to the version in `db_versions.json`; new documents have no version to pin. Each chunk is read back and compared with `content/out/`. Wording changes keep review history. A substantive answer change resets that track, as the spec says.

## Card rules the validator enforces

The build fails on any of these:

- fewer than 3 variants in a track
- a scenario question whose distractor pool isn't 4–6, or whose correct-answer count doesn't match its pick count
- an option without an explanation
- an "all of the above" or "none of the above" option
- a cloze or code card without exactly one gap
- a bad occlusion mask or source index
- a straight quote in prose
- a prompt that doesn't name its setting, unless the variant is marked `settingIsAnswer`
- a code line over 40 characters, counting a gap as 9
- a `flip` field whose partner variant is missing, doesn't point back, or has the same answer (constraint-flip pairs)
- duplicate concept ids or `order` values

Option lengths more than 2.2 times apart are printed as notes.

## Milestone 4 decisions

**Navigation.** Tabs above the review header; `#progress`, `#notes` and `#preferences` route to those screens (`settings` is reserved by claude.ai). Leaving Today pauses the open card's timer and keeps the card; returning resumes it. `nextCard` does nothing while another screen shows, so a learn-ahead timer can't draw over Notes.

**Readiness.** Exactly the spec's formula: per objective, coverage (introduced of written tracks) times mean retrievability on exam day from the scheduler's exact-time `retrievability`; objectives average within a domain; domains weight by the blueprint. Exam day is 09:00 local on the Settings date, or 14 days from now when none is set or it has passed. Coverage counts tracks written so far, so it reads high while content is incomplete; that is an open question in the spec.

**Backup format** (`format: "cert-srs-backup"`, `version: 1`): `content` maps `exams/…`, `concepts/…`, `heldout/…` to bodies; `private` maps paths relative to `data/users/{uid}` (`settings`, `state`, `params`, `state/{tracks|reviews|flags|notes|mocks}/{id}`) to bodies; plus `created`, `createdMs`, `source`, `uid`, `counts`. Reviews are read in pages of 500 by `t`. A backup writes nothing; the last-backup date is in the browser.

**Restore.** Private rows only (content is read-only to the app; restore it from chat with `tools/restore_content.py`). It validates every key and body first, shows what it will write and delete, needs two taps, writes the rows (the `state` day summary last) and deletes private rows not in the backup. It follows the signed-in user, so it works across user ids, and rerunning after an interruption finishes the job.

## License

MIT, see [LICENSE](LICENSE). Third-party code keeps its own license: [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs) (MIT, loaded from jsDelivr and installed for tests) and [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) (MIT, used by the optional cross-check; `scheduler/pyfsrs-calendar-days.patch` is a patch against it).
