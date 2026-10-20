# Code Hinter: VS Code extension

An AI tutor for students. It gives **hints, never solutions**, adapts to the student's level and
learning style, and tests them on every concept the professor teaches.

See the [main README](../README.md) for the full picture and screenshots.

## Commands (Command Palette → "Code Hinter")

| Command | Shortcut |
|---|---|
| Give me a hint | `Ctrl+Alt+H` (also 💡 in the status bar, editor title and right-click menu) |
| Ask the tutor a question | `Ctrl+Alt+Q` |
| Explain a concept | |
| Test me | `Ctrl+Alt+T` |
| My learning progress | |
| Set up my learning profile | |
| Ask my professor | |
| Evaluate Code · submit Code for comparison · Login · Logout · change exercise · Test api's | |

## Settings

- `codeHinter.serverUrl`: backend base URL (default `http://156.18.90.98:5000/api`; for a local
  backend use `http://127.0.0.1:5000/api`).

## Development

```sh
npm install
npm run compile        # webpack bundle in dist/, then F5 to run the extension
npm run lint
npm run test:unit      # API client + webview rendering, plain Node, no VS Code needed
npm test               # integration test inside VS Code (needs a display)
```
