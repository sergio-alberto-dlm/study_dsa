/** What the UI can see and do. It crosses Electron's process boundary, so everything here is plain data. */

export type ProblemSummary = { id: string; title: string };

export type OpenAttempt = {
  attemptId: number;
  problemId: string;
  title: string;
  statement: string;
  code: string;
  elapsedMs: number;
};

export type FailingCase = { input: string; actual: string; expected: string };

export type SubmissionResult =
  | { status: "passed" }
  | { status: "failed"; failingCase: FailingCase }
  | { status: "error"; message: string }
  | { status: "timeout" };

export type SubmitOutcome =
  | { result: SubmissionResult; attemptEnded: false }
  | { result: SubmissionResult; attemptEnded: true; durationMs: number };

export interface StudyApi {
  listProblems(): ProblemSummary[];
  /** Starts an Attempt, or resumes the Problem's unfinished one. */
  openProblem(problemId: string): OpenAttempt;
  submit(attemptId: number, code: string): Promise<SubmitOutcome>;
}
