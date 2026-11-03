import { cpSync, mkdirSync, rmSync } from "node:fs";
import { build } from "esbuild";

rmSync("dist", { recursive: true, force: true });
mkdirSync("dist/renderer", { recursive: true });

await build({
  entryPoints: { main: "src/main/main.ts", preload: "src/main/preload.ts" },
  outdir: "dist",
  outExtension: { ".js": ".cjs" },
  bundle: true,
  platform: "node",
  format: "cjs",
  external: ["electron"],
});

await build({
  entryPoints: {
    renderer: "src/renderer/renderer.ts",
    "editor.worker": "node_modules/monaco-editor/esm/vs/editor/editor.worker.js",
  },
  outdir: "dist/renderer",
  bundle: true,
  format: "iife",
  loader: { ".ttf": "file" },
});

cpSync("src/renderer/index.html", "dist/renderer/index.html");
cpSync("src/renderer/styles.css", "dist/renderer/styles.css");
