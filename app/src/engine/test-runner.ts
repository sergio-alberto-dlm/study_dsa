import type { SubmissionResult } from "../shared/study-api";

export interface TestRunner {
  run(problemDir: string, code: string): Promise<SubmissionResult>;
}
