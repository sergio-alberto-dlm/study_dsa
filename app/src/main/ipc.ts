import type { StudyApi } from "../shared/study-api";

/** Every Study Engine operation the UI may call. Each is one IPC channel. */
export const STUDY_OPERATIONS = [
  "listProblems",
  "openProblem",
  "submit",
] as const satisfies ReadonlyArray<keyof StudyApi>;
