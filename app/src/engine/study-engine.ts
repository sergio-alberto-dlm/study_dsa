import type { StudyApi, SubmissionResult } from "../shared/study-api";
import { openHistory, type StoredAttempt, type SubmissionRecord } from "./history";
import { findProblem, loadProblems } from "./problem-bank";
import type { TestRunner } from "./test-runner";

export type AttemptRecord = {
  id: number;
  startedAt: number;
  endedAt: number | null;
  outcome: "passed" | null;
  durationMs: number | null;
  submissions: SubmissionRecord[];
};

export type ProblemDetails = { id: string; title: string; attempts: AttemptRecord[] };

export type StudyEngine = StudyApi & {
  getProblem(problemId: string): ProblemDetails;
  close(): void;
};

export type StudyEngineDeps = {
  clock: { now(): number };
  testRunner: TestRunner;
  databasePath: string;
  problemBankDir: string;
};

/** The one module holding the study rules. The UI reaches it only through StudyApi. */
export function createStudyEngine(deps: StudyEngineDeps): StudyEngine {
  const { clock, testRunner, problemBankDir } = deps;
  const history = openHistory(deps.databasePath);
  const attemptsBeingSubmitted = new Set<number>();

  const toRecord = (attempt: StoredAttempt): AttemptRecord => ({
    id: attempt.id,
    startedAt: attempt.startedAt,
    endedAt: attempt.endedAt,
    outcome: attempt.outcome,
    durationMs: attempt.endedAt === null ? null : attempt.endedAt - attempt.startedAt,
    submissions: history.submissionsOf(attempt.id),
  });

  /** Whatever goes wrong here is the Submission's result, so its code is still saved. */
  const runTests = async (problemId: string, code: string): Promise<SubmissionResult> => {
    try {
      return await testRunner.run(findProblem(problemBankDir, problemId).dir, code);
    } catch (error) {
      return { status: "error", message: error instanceof Error ? error.message : String(error) };
    }
  };

  return {
    listProblems: () => loadProblems(problemBankDir).map(({ id, title }) => ({ id, title })),

    openProblem(problemId) {
      const problem = findProblem(problemBankDir, problemId);
      const opened = { problemId, title: problem.title, statement: problem.statement };

      const unfinished = history.findUnfinishedAttempt(problemId);
      if (unfinished) {
        // An Attempt's time is wall-clock time from its start, so it keeps counting
        // while the app is closed.
        return {
          ...opened,
          attemptId: unfinished.id,
          code: history.submissionsOf(unfinished.id).at(-1)?.code ?? problem.stub,
          elapsedMs: clock.now() - unfinished.startedAt,
        };
      }

      return {
        ...opened,
        attemptId: history.startAttempt(problemId, clock.now()),
        code: problem.stub,
        elapsedMs: 0,
      };
    },

    async submit(attemptId, code) {
      const attempt = history.findAttempt(attemptId);
      if (!attempt) throw new Error(`No Attempt ${attemptId}`);
      if (attempt.endedAt !== null) throw new Error(`Attempt ${attemptId} has already ended`);
      if (attemptsBeingSubmitted.has(attemptId)) {
        throw new Error(`A Submission for Attempt ${attemptId} is still running`);
      }

      // The learner's time stops when they submit: how long the tests take isn't theirs.
      const submittedAt = clock.now();
      attemptsBeingSubmitted.add(attemptId);
      try {
        const result = await runTests(attempt.problemId, code);
        const passed = result.status === "passed";
        history.recordSubmission(attemptId, { submittedAt, code, result }, passed);
        return passed
          ? { result, attemptEnded: true, durationMs: submittedAt - attempt.startedAt }
          : { result, attemptEnded: false };
      } finally {
        attemptsBeingSubmitted.delete(attemptId);
      }
    },

    getProblem(problemId) {
      const { id, title } = findProblem(problemBankDir, problemId);
      return { id, title, attempts: history.attemptsOf(problemId).map(toRecord) };
    },

    close: () => history.close(),
  };
}
