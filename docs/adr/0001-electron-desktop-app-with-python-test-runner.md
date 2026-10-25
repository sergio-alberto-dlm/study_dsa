# Electron desktop app, with tests run by a separate Python process

The app is an Electron desktop app with a web UI and an embedded Monaco editor. Solutions are Python, and their tests run in a separate, time-limited Python subprocess rather than inside the app. We wanted an attractive interface and an interview-like editor, which a web stack gives most directly.

## Considered Options

- **Tauri**: smaller and faster, but it needs a Rust toolchain and current Xcode Command Line Tools to build, and those were out of date on the development machine (macOS 14).
- **Python + Qt (PySide)**: no web stack and no separate test process, but a polished look and a good code editor are much harder to get.
