import type { Product } from "./product-types";

export const product: Product = {
  number: "02",
  name: "Agent Autopsy",
  eyebrow: "Failure traces to regression tests",
  tagline: "Make every agent failure leave behind a test.",
  description: "Inspect a failed support-agent trace, isolate the causal mistake, propose the smallest patch, and turn the incident into a permanent regression check.",
  accent: "#f04f78",
  inputLabel: "Failed agent trace",
  inputHint: "This exact five-event JSON trace is evaluated by product.py.",
  inputValue: `[
  {"seq":1,"type":"context","customer_id":"CUS-1042","verified":true},
  {"seq":2,"type":"tool","name":"lookup_customer","args":{"customer_id":"CUS-1042"}},
  {"seq":3,"type":"context","customer_id":"CUS-1402"},
  {"seq":4,"type":"tool","name":"issue_refund","args":{"customer_id":"CUS-1402","amount":750}},
  {"seq":5,"type":"tool","name":"issue_refund","args":{"customer_id":"CUS-1402","amount":750}}
]`,
  actionLabel: "Reveal verified result",
  status: "PATCH_READY",
  statusTone: "warn",
  metrics: [{ value: "5", label: "trace events" }, { value: "3", label: "root causes" }, { value: "3", label: "regression tests" }],
  findings: [
    { title: "Customer context drift", detail: "The trace changes from CUS-1042 to CUS-1402 before the refund.", badge: "HIGH", tone: "bad" },
    { title: "Duplicate refund side effect", detail: "issue_refund is called twice; the proposed patch would add a persisted idempotency key.", badge: "CRITICAL", tone: "warn" },
    { title: "$750 limit bypass", detail: "The amount exceeds the $500 autonomous limit without the required approval record.", badge: "CRITICAL", tone: "bad" },
  ],
  method: [
    { step: "01", title: "Reconstruct", detail: "Order observations, decisions, tool calls, and side effects into one timeline." },
    { step: "02", title: "Localize", detail: "Distinguish the first causal error from later symptoms." },
    { step: "03", title: "Prevent", detail: "Propose a minimal patch and an assertion that fails on the original trace; rerun remains NOT_RUN." },
  ],
  proof: ["Validated sequence", "One test per failure", "Proposed patch scope"],
  note: "This demo uses a synthetic trace and does not execute refunds or connect to customer systems.",
};
