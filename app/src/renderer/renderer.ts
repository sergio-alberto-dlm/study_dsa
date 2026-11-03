import type { OpenAttempt, StudyApi, SubmissionResult } from "../shared/study-api";
import { createEditor } from "./editor";

/** The Study Engine, across the process boundary. Every call becomes asynchronous. */
const study = (window as unknown as { study: Promisified<StudyApi> }).study;

type Promisified<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R ? (...args: A) => Promise<Awaited<R>> : never;
};

const app = document.getElementById("app")!;

function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  props: Partial<HTMLElementTagNameMap[K]> = {},
  ...children: Array<Node | string>
): HTMLElementTagNameMap[K] {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

function formatTime(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

async function showProblemBank() {
  const problems = await study.listProblems();
  app.replaceChildren(
    el(
      "div",
      { className: "bank" },
      el("h1", {}, "Problem Bank"),
      problems.length === 0
        ? el("p", { className: "notice" }, "No Problems in the bank folder yet.")
        : el(
            "ul",
            {},
            ...problems.map(({ id, title }) =>
              el("li", {}, el("button", { onclick: () => void openProblem(id) }, title)),
            ),
          ),
    ),
  );
}

async function openProblem(problemId: string) {
  try {
    showAttempt(await study.openProblem(problemId));
  } catch (error) {
    app.querySelector(".bank")?.append(el("p", { className: "notice" }, String(error)));
  }
}

function showAttempt(attempt: OpenAttempt) {
  const timer = el("span", { className: "timer" });
  const result = el("div", { className: "result" });
  const editorHost = el("div", { className: "editor" });
  const submitButton = el("button", { className: "primary" }, "Submit");
  const backButton = el("button", {}, "Back to Problems");

  app.replaceChildren(
    el(
      "div",
      { className: "attempt" },
      el("header", {}, el("h1", {}, attempt.title), timer, submitButton, backButton),
      el(
        "div",
        { className: "workspace" },
        el("section", { className: "statement" }, attempt.statement),
        el("section", { className: "editor-pane" }, editorHost, result),
      ),
    ),
  );

  const editor = createEditor(editorHost, attempt.code);
  editor.focus();

  const shownAt = performance.now();
  const showElapsed = () => {
    timer.textContent = formatTime(attempt.elapsedMs + performance.now() - shownAt);
  };
  showElapsed();
  const ticking = setInterval(showElapsed, 250);

  const stopTimer = (finalMs?: number) => {
    clearInterval(ticking);
    if (finalMs !== undefined) timer.textContent = formatTime(finalMs);
  };

  backButton.onclick = () => {
    stopTimer();
    editor.dispose();
    void showProblemBank();
  };

  submitButton.onclick = async () => {
    submitButton.disabled = true;
    result.replaceChildren("Running tests…");
    try {
      const outcome = await study.submit(attempt.attemptId, editor.getValue());
      result.replaceChildren(...describeResult(outcome.result));
      if (outcome.attemptEnded) {
        stopTimer(outcome.durationMs);
        editor.updateOptions({ readOnly: true });
        return;
      }
      submitButton.disabled = false;
    } catch (error) {
      result.replaceChildren(String(error));
      submitButton.disabled = false;
    }
  };
}

function describeResult(result: SubmissionResult): Array<Node | string> {
  switch (result.status) {
    case "passed":
      return [el("strong", { className: "passed" }, "Passed")];
    case "timeout":
      return [
        el("strong", { className: "failed" }, "Timeout"),
        " — the code was stopped for running too long.",
      ];
    case "error":
      return [el("strong", { className: "failed" }, "Error"), el("pre", {}, result.message)];
    case "failed": {
      const { input, actual, expected } = result.failingCase;
      return [
        el("strong", { className: "failed" }, "Failed"),
        el(
          "dl",
          {},
          el("dt", {}, "Input"),
          el("dd", {}, input),
          el("dt", {}, "Your output"),
          el("dd", {}, actual),
          el("dt", {}, "Expected"),
          el("dd", {}, expected),
        ),
      ];
    }
  }
}

void showProblemBank();
