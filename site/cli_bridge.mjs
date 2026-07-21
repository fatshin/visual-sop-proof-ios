import { buildReadingMarkdown, createDeepReading } from "./public/reading.js";

let input = "";
for await (const chunk of process.stdin) input += chunk;
const payload = JSON.parse(input);
if (!["reading", "markdown"].includes(payload.operation)) {
  throw new Error("Unknown shared-engine operation");
}
const output =
  payload.operation === "markdown"
    ? buildReadingMarkdown(payload.reading)
    : createDeepReading(payload);
process.stdout.write(JSON.stringify(output));
