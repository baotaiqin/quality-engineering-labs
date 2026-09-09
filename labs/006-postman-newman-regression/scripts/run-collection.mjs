import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import newman from "newman";

import { close, createAuthServer, listen } from "../server/app.mjs";


const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failureMode = process.argv.includes("--failure");
const collectionName = failureMode
  ? "auth-regression.failure.postman_collection.json"
  : "auth-regression.postman_collection.json";
const collection = path.join(projectRoot, "postman", collectionName);
const environment = path.join(
  projectRoot,
  "postman",
  "local.postman_environment.json",
);
const reportsDir = path.join(projectRoot, "reports");

await mkdir(reportsDir, { recursive: true });

const server = createAuthServer();
const address = await listen(server, 0);
const baseUrl = `http://127.0.0.1:${address.port}`;

try {
  const summary = await new Promise((resolve, reject) => {
    newman.run(
      {
        collection,
        environment,
        envVar: [{ key: "baseUrl", value: baseUrl }],
        reporters: ["cli", "json", "junit"],
        reporter: {
          json: {
            export: path.join(reportsDir, failureMode ? "failure.json" : "run.json"),
          },
          junit: {
            export: path.join(reportsDir, failureMode ? "failure.xml" : "run.xml"),
          },
        },
        timeoutRequest: 1000,
      },
      (error, runSummary) => {
        if (error) {
          reject(error);
          return;
        }
        resolve(runSummary);
      },
    );
  });

  const failures = summary.run.failures.length;
  const result = {
    collection: failureMode ? "failure-case" : "auth-regression",
    iterations: summary.run.stats.iterations.total,
    requests: summary.run.stats.requests.total,
    assertions: summary.run.stats.assertions.total,
    failedAssertions: summary.run.stats.assertions.failed,
    durationMs: summary.run.timings.completed - summary.run.timings.started,
    failures: summary.run.failures.map((failure) => ({
      request: failure.source?.name ?? "unknown",
      assertion: failure.error?.test ?? "request error",
      message: failure.error?.message ?? "unknown error",
    })),
  };
  const summaryName = failureMode ? "failure-summary.json" : "summary.json";
  await writeFile(
    path.join(reportsDir, summaryName),
    `${JSON.stringify(result, null, 2)}\n`,
    "utf8",
  );
  process.exitCode = failures === 0 ? 0 : 1;
} finally {
  await close(server);
}
