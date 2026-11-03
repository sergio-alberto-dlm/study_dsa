import { join } from "node:path";
import { app, BrowserWindow, ipcMain } from "electron";
import { createPythonTestRunner } from "../engine/python-test-runner";
import { createStudyEngine } from "../engine/study-engine";
import { STUDY_OPERATIONS } from "./ipc";

const REPO_ROOT = join(__dirname, "..", "..");

app.whenReady().then(() => {
  const engine = createStudyEngine({
    clock: { now: () => Date.now() },
    testRunner: createPythonTestRunner({ runnerDir: join(REPO_ROOT, "runner") }),
    databasePath: join(REPO_ROOT, "history.db"),
    problemBankDir: join(REPO_ROOT, "problems"),
  });
  app.on("will-quit", () => engine.close());

  for (const operation of STUDY_OPERATIONS) {
    ipcMain.handle(operation, (_event, ...args) =>
      (engine[operation] as (...a: unknown[]) => unknown)(...args),
    );
  }

  const window = new BrowserWindow({
    width: 1280,
    height: 820,
    title: "DSA Study",
    webPreferences: {
      preload: join(__dirname, "preload.cjs"),
      contextIsolation: true,
      sandbox: true,
    },
  });
  window.loadFile(join(__dirname, "renderer", "index.html"));
});

app.on("window-all-closed", () => app.quit());
