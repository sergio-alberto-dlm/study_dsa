import { contextBridge, ipcRenderer } from "electron";
import { STUDY_OPERATIONS } from "./ipc";

contextBridge.exposeInMainWorld(
  "study",
  Object.fromEntries(
    STUDY_OPERATIONS.map((operation) => [
      operation,
      (...args: unknown[]) => ipcRenderer.invoke(operation, ...args),
    ]),
  ),
);
