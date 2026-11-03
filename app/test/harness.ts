import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach } from "vitest";
import { createStudyEngine, type StudyEngine } from "../src/engine/study-engine";
import type { TestRunner } from "../src/engine/test-runner";
import type { SubmissionResult } from "../src/shared/study-api";

const cleanups: Array<() => void> = [];

afterEach(() => {
  while (cleanups.length > 0) cleanups.pop()!();
});

export const MINUTE = 60_000;

export function fakeClock(startMs = Date.UTC(2026, 10, 2, 9, 0, 0)) {
  let nowMs = startMs;
  return {
    now: () => nowMs,
    advance: (ms: number) => {
      nowMs += ms;
    },
  };
}

/** Returns queued results in order, and "passed" once the queue is empty. */
export function fakeTestRunner() {
  const queued: SubmissionResult[] = [];
  let duringRun = () => {};
  const runner: TestRunner = {
    run: async () => {
      duringRun();
      return queued.shift() ?? { status: "passed" };
    },
  };
  return {
    ...runner,
    willReturn: (result: SubmissionResult) => queued.push(result),
    willRunFor: (passTime: () => void) => {
      duringRun = passTime;
    },
  };
}

export function tempDir(): string {
  const dir = mkdtempSync(join(tmpdir(), "dsa-engine-"));
  cleanups.push(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

export function writeProblem(bankDir: string, folder: string, id: string, title: string) {
  const dir = join(bankDir, folder);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "statement.md"), `Statement of ${title}`);
  writeFileSync(join(dir, "stub.py"), `def ${folder}():\n    pass\n`);
  writeFileSync(join(dir, "tests.py"), "");
  writeFileSync(
    join(dir, "problem.json"),
    JSON.stringify({
      id,
      title,
      topic: "Heaps",
      patterns: ["two heaps"],
      source: "Claude",
      hints: ["a", "b", "c"],
    }),
  );
  return dir;
}

/** An engine on a temporary database and Problem Bank, with a fake clock and Test Runner. */
export function engineFixture() {
  const root = tempDir();
  const problemBankDir = join(root, "problems");
  mkdirSync(problemBankDir);
  const databasePath = join(root, "history.db");
  const clock = fakeClock();
  const testRunner = fakeTestRunner();

  const open = (): StudyEngine => {
    const engine = createStudyEngine({ clock, testRunner, databasePath, problemBankDir });
    cleanups.push(() => engine.close());
    return engine;
  };

  return { problemBankDir, clock, testRunner, engine: open(), reopen: open };
}
