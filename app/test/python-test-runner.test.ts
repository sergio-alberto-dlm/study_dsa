import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { createPythonTestRunner } from "../src/engine/python-test-runner";

const RUNNER_DIR = join(__dirname, "..", "..", "runner");
const DAILY_TEMPERATURES = join(RUNNER_DIR, "tests", "fixtures", "daily_temperatures");
const runner = createPythonTestRunner({ runnerDir: RUNNER_DIR, timeLimitSec: 1 });

describe("the Python Test Runner", () => {
  it("reports a correct solution as passed", async () => {
    const code = `
def daily_temperatures(temperatures):
    answer, waiting = [0] * len(temperatures), []
    for day, temperature in enumerate(temperatures):
        while waiting and temperatures[waiting[-1]] < temperature:
            colder = waiting.pop()
            answer[colder] = day - colder
        waiting.append(day)
    return answer
`;
    expect(await runner.run(DAILY_TEMPERATURES, code)).toEqual({ status: "passed" });
  });

  it("reports the first failing case", async () => {
    const code = "def daily_temperatures(t):\n    return [0] * len(t)\n";

    expect(await runner.run(DAILY_TEMPERATURES, code)).toEqual({
      status: "failed",
      failingCase: {
        input: "temperatures=[73, 74, 75, 71, 69, 72, 76, 73]",
        actual: "[0, 0, 0, 0, 0, 0, 0, 0]",
        expected: "[1, 1, 4, 2, 1, 1, 0, 0]",
      },
    });
  });

  it("reports code that isn't valid Python as an error", async () => {
    const result = await runner.run(DAILY_TEMPERATURES, "def broken(:\n");

    expect(result).toEqual({ status: "error", message: expect.stringContaining("SyntaxError") });
  });

  it("reports an infinite loop as a timeout", async () => {
    const code = "def daily_temperatures(t):\n    while True:\n        pass\n";

    expect(await runner.run(DAILY_TEMPERATURES, code)).toEqual({ status: "timeout" });
  });

  it("reports an error, rather than failing, when Python can't be started", async () => {
    const broken = createPythonTestRunner({ runnerDir: RUNNER_DIR, python: "/no/such/python" });

    const result = await broken.run(DAILY_TEMPERATURES, "");

    expect(result).toEqual({ status: "error", message: expect.stringContaining("/no/such/python") });
  });
});
