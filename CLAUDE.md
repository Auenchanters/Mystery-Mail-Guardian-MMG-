# CLAUDE.md — Project agent guidance

Token-efficient, context-aware workflow for **this repository only**.
All tooling here is **project-local** (lives in `.venv/`, `.tools/`, `scripts/`). Nothing is installed globally and no machine-wide Claude/shell settings are touched.

---

## Working rules (token efficiency)

- Work in **minimal steps**: do one thing, verify it worked, then continue.
- Prefer **diffs / targeted edits** over full-file rewrites.
- Reference code by **`path:line`** instead of pasting long blocks.
- Don't repeat what's already in context; don't summarize what you just did — state only what's next.
- Compress shell output: surface **errors, warnings, and final status** only.
- Don't explain well-known concepts unless asked.

## Session protocol (Handoff)

- **At session start:** read [HANDOFF.md](HANDOFF.md) before doing anything else. Treat each session as fresh; don't rely on prior chat history.
- **At session end:** update [HANDOFF.md](HANDOFF.md) — completed / in progress / blocked / next steps / commands used / files touched.

## Intent layer

Before executing a task, restate it as: **(1) core intent, (2) constraints, (3) success criteria.** If any of the three is unclear, ask one clarifying question before acting.

## Caveman (smallest steps)

Never assume — check before proceeding. Prefer reading existing files over generating from scratch. When unsure, ask.

---

## Local tooling — when and how to use

### code-review-graph (structural code graph)
Use **before broad file reading** to find the blast radius of a change, once the repo has a `.git` dir and source files.
- Build/update: `scripts/crg.ps1 build`  (stores graph in project-local `.crg/graph.db`)
- Impact of pending changes: `scripts/crg.ps1 detect-changes`
- Stats: `scripts/crg.ps1 status`
- ⚠️ Do **not** run `code-review-graph install` / `init` — those register a **global** MCP server. Avoided by design here.
- Precondition: needs a `.git` (or `.code-review-graph`) marker + actual source files, or it errors with "does not look like a project root".

### Headroom (context compression, local proxy) — ⚠️ NOT ACTIVE ON WINDOWS
`headroom-ai` has **no Windows wheel** (macOS/Linux only); on Windows it must compile a
Rust extension, which needs a global Rust toolchain. Not installed (project-local-only policy).
- Launcher is staged at `scripts/run-claude-with-headroom.ps1` but will refuse to run until
  `headroom.exe` exists in `.venv`. It uses **session-scoped** env vars only (no global Claude edits).
- To enable: install Rust (with approval) then `uv pip install --python .venv\Scripts\python.exe "headroom-ai[proxy]"`, **or** run under WSL/Linux.

### RTK (shell-output compressor) — OPTIONAL, not installed by default
RTK is a Rust binary with **no project-local install path** and **no npm package** (the `npm i -g @rtk-ai/rtk` instruction floating around is wrong). To keep it local:
- Fetch a prebuilt Windows binary into `.tools/rtk/`: `scripts/install-rtk-local.ps1` (⚠️ downloads + runs third-party code — review before running).
- Then prefix heavy commands via wrappers: `scripts/rtk-grep.ps1`, `scripts/rtk-read.ps1`.
- If `.tools/rtk/rtk.exe` is absent, skip RTK silently.

---

## Environment notes

- OS: Windows 11, shell: **Windows PowerShell 5.1** (`powershell.exe`). Launchers are `.ps1`. `pwsh` (PowerShell Core) is not installed.
- Python venv: `.venv/` (CPython 3.12, created by `uv`). Activate: `.venv\Scripts\Activate.ps1`.
- Run venv tools directly without activating: `.venv\Scripts\<tool>.exe`.
