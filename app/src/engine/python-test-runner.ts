import { spawn } from "node:child_process";
import { resolve } from "node:path";
import type { SubmissionResult } from "../shared/study-api";
import type { TestRunner } from "./test-runner";

type Options = {
  /** The folder holding the dsa_runner package. */
  runnerDir: string;
  python?: string;
  timeLimitSec?: number;
};

/** Runs Submissions through `python -m dsa_runner`. It never rejects: any failure is an `error` result. */
export function createPythonTestRunner(options: Options): TestRunner {
  const { runnerDir, python = "python3", timeLimitSec } = options;
  const limitArgs = timeLimitSec === undefined ? [] : ["--time-limit", String(timeLimitSec)];

  return {
    run: (problemDir, code) =>
      new Promise((done) => {
        const child = spawn(python, ["-m", "dsa_runner", resolve(problemDir), ...limitArgs], {
          cwd: runnerDir,
          stdio: ["pipe", "pipe", "pipe"],
        });
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", (chunk) => (stdout += chunk));
        child.stderr.on("data", (chunk) => (stderr += chunk));
        child.on("error", (error) => {
          done({ status: "error", message: `Could not start ${python}: ${error.message}` });
        });
        child.on("close", () => done(parseReport(stdout, stderr)));
        child.stdin.on("error", () => {}); // Python exiting early is reported by "close".
        child.stdin.end(code);
      }),
  };
}

function parseReport(stdout: string, stderr: string): SubmissionResult {
  let report;
  try {
    report = JSON.parse(stdout);
  } catch {
    return { status: "error", message: `The Test Runner gave no result: ${stderr.trim()}` };
  }
  switch (report.status) {
    case "passed":
      return { status: "passed" };
    case "failed":
      return { status: "failed", failingCase: report.failing_case };
    case "timeout":
      return { status: "timeout" };
    default:
      return { status: "error", message: report.message ?? "Unknown error" };
  }
}
