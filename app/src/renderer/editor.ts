import * as monaco from "monaco-editor/editor/editor.api.js";
import "monaco-editor/languages/definitions/python/register.js";

(self as unknown as { MonacoEnvironment: monaco.Environment }).MonacoEnvironment = {
  getWorkerUrl: () => "editor.worker.js",
};

/**
 * An interview-like editor: syntax highlighting and nothing else. Only the core editor and the
 * Python grammar are bundled, so no language service exists; the options turn off what's left.
 */
export function createEditor(container: HTMLElement, code: string) {
  return monaco.editor.create(container, {
    value: code,
    language: "python",
    theme: "vs-dark",
    automaticLayout: true,
    fontSize: 14,
    tabSize: 4,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    quickSuggestions: false,
    suggestOnTriggerCharacters: false,
    wordBasedSuggestions: "off",
    acceptSuggestionOnEnter: "off",
    tabCompletion: "off",
    snippetSuggestions: "none",
    parameterHints: { enabled: false },
    inlineSuggest: { enabled: false },
    hover: { enabled: "off" },
    lightbulb: { enabled: monaco.editor.ShowLightbulbIconMode.Off },
    renderValidationDecorations: "off",
    occurrencesHighlight: "off",
    links: false,
    contextmenu: false,
  });
}
