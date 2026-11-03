import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { engineFixture, MINUTE, writeProblem } from "./harness";

describe("listing the Problem Bank", () => {
  it("lists every Problem folder by title, without giving away its Topic or Patterns", () => {
    const { engine, problemBankDir } = engineFixture();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    writeProblem(problemBankDir, "lru_cache", "lru-cache", "LRU Cache");

    expect(engine.listProblems()).toEqual([
      { id: "lru-cache", title: "LRU Cache" },
      { id: "two-sum", title: "Two Sum" },
    ]);
  });

  it("leaves out broken Problem folders instead of crashing", () => {
    const { engine, problemBankDir } = engineFixture();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    mkdirSync(join(problemBankDir, "empty"));
    const badJson = writeProblem(problemBankDir, "bad_json", "bad-json", "Bad");
    writeFileSync(join(badJson, "problem.json"), "{ not json");
    writeFileSync(join(problemBankDir, "README.md"), "not a folder");

    expect(engine.listProblems()).toEqual([{ id: "two-sum", title: "Two Sum" }]);
  });
});

describe("a Problem folder missing a file", () => {
  it.each(["statement.md", "stub.py", "tests.py"])("is left out when %s is missing", (file) => {
    const { engine, problemBankDir } = engineFixture();
    const dir = writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    rmSync(join(dir, file));

    expect(engine.listProblems()).toEqual([]);
    expect(() => engine.openProblem("two-sum")).toThrow(/two-sum/);
  });
});

describe("opening a Problem", () => {
  it("starts an Attempt from the statement and the stub only, with the timer at zero", () => {
    const { engine, problemBankDir } = engineFixture();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");

    const attempt = engine.openProblem("two-sum");

    expect(attempt).toEqual({
      attemptId: expect.any(Number),
      problemId: "two-sum",
      title: "Two Sum",
      statement: "Statement of Two Sum",
      code: "def two_sum():\n    pass\n",
      elapsedMs: 0,
    });
  });

  it("refuses a Problem that isn't in the bank", () => {
    const { engine } = engineFixture();

    expect(() => engine.openProblem("nope")).toThrow(/nope/);
  });
});

describe("submitting code", () => {
  const FAILING_CASE = { input: "nums=[1]", actual: "None", expected: "[0]" };

  function openTwoSum() {
    const fixture = engineFixture();
    writeProblem(fixture.problemBankDir, "two_sum", "two-sum", "Two Sum");
    return { ...fixture, attempt: fixture.engine.openProblem("two-sum") };
  }

  it("reports the first failing case and leaves the Attempt open for another Submission", async () => {
    const { engine, attempt, testRunner } = openTwoSum();
    testRunner.willReturn({ status: "failed", failingCase: FAILING_CASE });

    const outcome = await engine.submit(attempt.attemptId, "wrong");

    expect(outcome).toEqual({
      result: { status: "failed", failingCase: FAILING_CASE },
      attemptEnded: false,
    });
  });

  it("reports errors and timeouts the same way, without ending the Attempt", async () => {
    const { engine, attempt, testRunner } = openTwoSum();
    testRunner.willReturn({ status: "error", message: "NameError: x" });
    testRunner.willReturn({ status: "timeout" });

    expect(await engine.submit(attempt.attemptId, "a")).toEqual({
      result: { status: "error", message: "NameError: x" },
      attemptEnded: false,
    });
    expect(await engine.submit(attempt.attemptId, "b")).toEqual({
      result: { status: "timeout" },
      attemptEnded: false,
    });
  });

  it("ends the Attempt at the first passing Submission, with its duration from the clock", async () => {
    const { engine, attempt, testRunner, clock } = openTwoSum();
    testRunner.willReturn({ status: "failed", failingCase: FAILING_CASE });
    clock.advance(4 * MINUTE);
    await engine.submit(attempt.attemptId, "wrong");
    clock.advance(3 * MINUTE);

    const outcome = await engine.submit(attempt.attemptId, "right");

    expect(outcome).toEqual({
      result: { status: "passed" },
      attemptEnded: true,
      durationMs: 7 * MINUTE,
    });
  });

  it("stops the Attempt's time when the learner submits, not when the tests finish", async () => {
    const { engine, attempt, testRunner, clock } = openTwoSum();
    testRunner.willRunFor(() => clock.advance(MINUTE));
    clock.advance(2 * MINUTE);

    const outcome = await engine.submit(attempt.attemptId, "right");

    expect(outcome).toMatchObject({ durationMs: 2 * MINUTE });
  });

  it("refuses a Submission to an Attempt that has already ended", async () => {
    const { engine, attempt } = openTwoSum();
    await engine.submit(attempt.attemptId, "right");

    await expect(engine.submit(attempt.attemptId, "again")).rejects.toThrow(/ended/);
  });

  it("refuses a second Submission while one is still running", async () => {
    const { engine, attempt } = openTwoSum();

    const first = engine.submit(attempt.attemptId, "right");
    await expect(engine.submit(attempt.attemptId, "double click")).rejects.toThrow(/running/);

    await expect(first).resolves.toMatchObject({ attemptEnded: true });
  });

  it("refuses a Submission to an unknown Attempt", async () => {
    const { engine } = engineFixture();

    await expect(engine.submit(999, "code")).rejects.toThrow(/999/);
  });

  it("saves the Submission as an error when its Problem folder has gone from the bank", async () => {
    const { engine, attempt, problemBankDir, reopen } = openTwoSum();
    rmSync(join(problemBankDir, "two_sum"), { recursive: true });

    const outcome = await engine.submit(attempt.attemptId, "my code");

    const result = { status: "error", message: expect.stringContaining("two-sum") };
    expect(outcome).toEqual({ result, attemptEnded: false });
    engine.close();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    const [saved] = reopen().getProblem("two-sum").attempts;
    expect(saved!.submissions).toEqual([
      { submittedAt: expect.any(Number), code: "my code", result },
    ]);
  });

  it("keeps every Submission's code and result after a restart", async () => {
    const { engine, attempt, testRunner, clock, reopen } = openTwoSum();
    testRunner.willReturn({ status: "failed", failingCase: FAILING_CASE });
    clock.advance(MINUTE);
    await engine.submit(attempt.attemptId, "wrong");
    clock.advance(MINUTE);
    await engine.submit(attempt.attemptId, "right");
    engine.close();

    const { attempts } = reopen().getProblem("two-sum");

    const startedAt = attempts[0]!.startedAt;
    expect(attempts).toEqual([
      {
        id: attempt.attemptId,
        startedAt,
        endedAt: startedAt + 2 * MINUTE,
        outcome: "passed",
        durationMs: 2 * MINUTE,
        submissions: [
          {
            submittedAt: startedAt + MINUTE,
            code: "wrong",
            result: { status: "failed", failingCase: FAILING_CASE },
          },
          { submittedAt: startedAt + 2 * MINUTE, code: "right", result: { status: "passed" } },
        ],
      },
    ]);
  });
});

describe("reopening a Problem", () => {
  it("resumes its unfinished Attempt with the time so far and the last submitted code", async () => {
    const { engine, problemBankDir, testRunner, clock, reopen } = engineFixture();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    const first = engine.openProblem("two-sum");
    testRunner.willReturn({ status: "timeout" });
    clock.advance(5 * MINUTE);
    await engine.submit(first.attemptId, "work in progress");
    engine.close();
    clock.advance(MINUTE);

    const resumed = reopen().openProblem("two-sum");

    expect(resumed).toMatchObject({
      attemptId: first.attemptId,
      code: "work in progress",
      elapsedMs: 6 * MINUTE,
    });
  });

  it("resumes from the stub when nothing has been submitted yet", () => {
    const { engine, problemBankDir, clock } = engineFixture();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    const first = engine.openProblem("two-sum");
    clock.advance(MINUTE);

    expect(engine.openProblem("two-sum")).toMatchObject({
      attemptId: first.attemptId,
      code: "def two_sum():\n    pass\n",
      elapsedMs: MINUTE,
    });
  });

  it("starts a new Attempt from the stub after the last one has ended", async () => {
    const { engine, problemBankDir } = engineFixture();
    writeProblem(problemBankDir, "two_sum", "two-sum", "Two Sum");
    const first = engine.openProblem("two-sum");
    await engine.submit(first.attemptId, "right");

    const second = engine.openProblem("two-sum");

    expect(second.attemptId).not.toBe(first.attemptId);
    expect(second).toMatchObject({ code: "def two_sum():\n    pass\n", elapsedMs: 0 });
  });
});
