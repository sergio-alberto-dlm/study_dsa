# DSA Study app

The Electron desktop app. See `docs/adr/0001-electron-desktop-app-with-python-test-runner.md`.

```
cd app
npm install
npm start
```

`npm install` needs Node 22.12 or newer, because Electron's installer does. Submissions run on the system `python3`.

The app reads Problems from `problems/` (format: `runner/README.md`) and keeps its history in `history.db`, both at the repo root. The app creates `history.db` on first launch. Commit it, because the history is meant to live in git.

## Layout

- `src/engine`: the Study Engine, the one module holding the study rules. It takes a clock, a Test Runner and a storage location.
- `src/main`: the Electron main process and preload script. They expose the Engine's operations to the UI over IPC.
- `src/renderer`: the UI, with no domain rules. The Monaco bundle has only the core editor and the Python grammar, so it highlights syntax and has no language service.
- `src/shared/study-api.ts`: the operations and data that cross the process boundary.

## Attempt time

An Attempt's duration runs from when it starts to the Submission that passes. It's wall-clock time, so it keeps counting while the app is closed. Reopening a Problem resumes its unfinished Attempt from the last submitted code; edits that were never submitted aren't kept.

## Development

```
npm run typecheck
npm test
```

`npm test` runs under Electron's Node, the runtime the Engine uses in the app, which provides `node:sqlite`. The UI has no automated tests: check it by hand with `npm start`.
