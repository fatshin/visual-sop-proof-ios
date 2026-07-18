import type { Product } from "./product-types";

export const product: Product = {
  number: "02",
  name: "Agent Autopsy",
  eyebrow: "Failure traces to regression tests",
  tagline: "Make every agent failure leave behind a test.",
  description: "Inspect a failed support-agent trace, isolate the causal mistake, propose the smallest patch, and turn the incident into a permanent regression check.",
  accent: "#f04f78",
  inputLabel: "Failed agent trace",
  inputHint: "The fixture contains context drift, duplicate side effects, and a policy-limit bypass.",
  inputValue: "Customer A asks about a delayed order. The agent switches to Customer B after a stale tool result, issues the refund twice after retrying, then approves $120 despite a $50 limit.",
  actionLabel: "Perform autopsy",
  status: "PATCH_READY",
  statusTone: "warn",
  metrics: [{ value: "3", label: "root causes" }, { value: "3", label: "regression tests" }, { value: "1", label: "minimal patch set" }],
  findings: [
    { title: "Customer context drift", detail: "A stale tool response changed the active customer without an identity guard.", badge: "ROOT CAUSE", tone: "bad" },
    { title: "Duplicate refund side effect", detail: "The retry path lacked an idempotency key and repeated a completed action.", badge: "REGRESSION", tone: "warn" },
    { title: "Refund limit bypass", detail: "The patch adds a hard approval boundary before the refund tool can execute.", badge: "PATCH", tone: "good" },
  ],
  method: [
    { step: "01", title: "Reconstruct", detail: "Order observations, decisions, tool calls, and side effects into one timeline." },
    { step: "02", title: "Localize", detail: "Distinguish the first causal error from later symptoms." },
    { step: "03", title: "Prevent", detail: "Emit a minimal patch and an assertion that fails on the original trace." },
  ],
  proof: ["Causal timeline", "One test per failure", "Minimal patch scope"],
  note: "This demo uses a synthetic trace and does not execute refunds or connect to customer systems.",
};
