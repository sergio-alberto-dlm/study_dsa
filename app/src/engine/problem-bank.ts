import { accessSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

export type Problem = { id: string; title: string; dir: string; statement: string; stub: string };

export function findProblem(bankDir: string, problemId: string): Problem {
  const problem = loadProblems(bankDir).find(({ id }) => id === problemId);
  if (!problem) throw new Error(`No Problem "${problemId}" in the bank`);
  return problem;
}

/** Reads the Problem folders. A broken folder is left out; it never stops the others loading. */
export function loadProblems(bankDir: string): Problem[] {
  return readdirSync(bankDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .flatMap((entry) => {
      const problem = readProblem(join(bankDir, entry.name));
      return problem ? [problem] : [];
    })
    .sort((a, b) => a.title.localeCompare(b.title));
}

function readProblem(dir: string): Problem | undefined {
  try {
    const { id, title } = JSON.parse(readFileSync(join(dir, "problem.json"), "utf8"));
    if (typeof id !== "string" || typeof title !== "string") return undefined;
    accessSync(join(dir, "tests.py"));
    return {
      id,
      title,
      dir,
      statement: readFileSync(join(dir, "statement.md"), "utf8"),
      stub: readFileSync(join(dir, "stub.py"), "utf8"),
    };
  } catch {
    return undefined;
  }
}
