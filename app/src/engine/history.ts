import { DatabaseSync } from "node:sqlite";
import type { SubmissionResult } from "../shared/study-api";

export type SubmissionRecord = { submittedAt: number; code: string; result: SubmissionResult };

export type StoredAttempt = {
  id: number;
  problemId: string;
  startedAt: number;
  endedAt: number | null;
  outcome: "passed" | null;
};

const SCHEMA = `
  CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY,
    problem_id TEXT NOT NULL,
    started_at INTEGER NOT NULL,
    ended_at INTEGER,
    outcome TEXT
  );
  CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY,
    attempt_id INTEGER NOT NULL REFERENCES attempts (id),
    submitted_at INTEGER NOT NULL,
    code TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT NOT NULL
  );
`;

const ATTEMPT_COLUMNS = `
  id, problem_id AS problemId, started_at AS startedAt, ended_at AS endedAt, outcome
`;

/** The history database. Times are stored as epoch milliseconds. */
export function openHistory(databasePath: string) {
  const db = new DatabaseSync(databasePath);
  db.exec(SCHEMA);

  const toSubmission = (row: unknown): SubmissionRecord => {
    const { submittedAt, code, result } = row as {
      submittedAt: number;
      code: string;
      result: string;
    };
    return { submittedAt, code, result: JSON.parse(result) as SubmissionResult };
  };

  return {
    startAttempt(problemId: string, startedAt: number): number {
      const { lastInsertRowid } = db
        .prepare("INSERT INTO attempts (problem_id, started_at) VALUES (?, ?)")
        .run(problemId, startedAt);
      return Number(lastInsertRowid);
    },

    findAttempt(attemptId: number): StoredAttempt | undefined {
      return db
        .prepare(`SELECT ${ATTEMPT_COLUMNS} FROM attempts WHERE id = ?`)
        .get(attemptId) as StoredAttempt | undefined;
    },

    findUnfinishedAttempt(problemId: string): StoredAttempt | undefined {
      return db
        .prepare(
          `SELECT ${ATTEMPT_COLUMNS} FROM attempts
           WHERE problem_id = ? AND ended_at IS NULL ORDER BY id DESC LIMIT 1`,
        )
        .get(problemId) as StoredAttempt | undefined;
    },

    attemptsOf(problemId: string): StoredAttempt[] {
      return db
        .prepare(`SELECT ${ATTEMPT_COLUMNS} FROM attempts WHERE problem_id = ? ORDER BY id`)
        .all(problemId) as StoredAttempt[];
    },

    submissionsOf(attemptId: number): SubmissionRecord[] {
      return db
        .prepare(
          `SELECT submitted_at AS submittedAt, code, result FROM submissions
           WHERE attempt_id = ? ORDER BY id`,
        )
        .all(attemptId)
        .map(toSubmission);
    },

    /** Saves the Submission and, if told to, ends its Attempt: both happen or neither does. */
    recordSubmission(attemptId: number, submission: SubmissionRecord, endsAttempt: boolean) {
      const { submittedAt, code, result } = submission;
      db.exec("BEGIN");
      try {
        db.prepare(
          `INSERT INTO submissions (attempt_id, submitted_at, code, status, result)
           VALUES (?, ?, ?, ?, ?)`,
        ).run(attemptId, submittedAt, code, result.status, JSON.stringify(result));
        if (endsAttempt) {
          db.prepare("UPDATE attempts SET ended_at = ?, outcome = 'passed' WHERE id = ?").run(
            submittedAt,
            attemptId,
          );
        }
        db.exec("COMMIT");
      } catch (error) {
        db.exec("ROLLBACK");
        throw error;
      }
    },

    close() {
      if (db.isOpen) db.close();
    },
  };
}
