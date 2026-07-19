import type { Product } from "./product-types";

export const product: Product = {
  number: "01",
  name: "Agent Policy Compiler",
  eyebrow: "Policy to executable decisions",
  tagline: "Turn policy prose into a decision system you can audit.",
  description: "Compile one written policy into explicit allow, block, and approval-required outcomes—each linked back to its source.",
  accent: "#ff6b35",
  inputLabel: "Tested policy and scenario fixture",
  inputHint: "These exact five clauses and seven scenarios are checked by product.py.",
  inputValue: `Policy:
POL-01: External transmissions containing PII must be blocked.
POL-02: Refunds above $500 and production deletion require human approval.
POL-03: Support may use lookup_customer and draft_reply.
POL-04: Finance may use issue_refund and lookup_customer.
POL-05: Admin may use every registered tool.

Scenarios:
[
  {"id":"S1","role":"support","tool":"lookup_customer","external":false,"pii":false,"amount":0},
  {"id":"S2","role":"support","tool":"send_email","external":true,"pii":true,"amount":0},
  {"id":"S3","role":"finance","tool":"issue_refund","external":false,"pii":false,"amount":120},
  {"id":"S4","role":"finance","tool":"issue_refund","external":false,"pii":false,"amount":900},
  {"id":"S5","role":"support","tool":"issue_refund","external":false,"pii":false,"amount":50},
  {"id":"S6","role":"admin","tool":"delete_production","external":false,"pii":false,"amount":0},
  {"id":"S7","role":"admin","tool":"rotate_logs","external":false,"pii":false,"amount":0}
]`,
  actionLabel: "Reveal verified result",
  status: "COMPILED",
  statusTone: "good",
  metrics: [{ value: "7", label: "scenarios" }, { value: "3 / 2 / 2", label: "allow / block / approval" }, { value: "5", label: "source-linked rules" }],
  findings: [
    { title: "PII email blocked", detail: "S2 is blocked by POL-01 because it sends PII externally.", badge: "BLOCK", tone: "bad" },
    { title: "$900 refund requires approval", detail: "S4 crosses the $500 threshold in POL-02.", badge: "APPROVAL", tone: "warn" },
    { title: "Support refund blocked", detail: "S5 cites the exact POL-03 support allowlist sentence; no synthetic rule ID is emitted.", badge: "ROLE GATE", tone: "good" },
  ],
  method: [
    { step: "01", title: "Parse", detail: "Separate permissions, prohibitions, thresholds, and ambiguity clauses." },
    { step: "02", title: "Compile", detail: "Convert every clause into an explicit decision rule with a source citation." },
    { step: "03", title: "Challenge", detail: "Run $500 and $500.01 boundary cases plus ambiguity checks before an agent may use the policy." },
  ],
  proof: ["7-case evaluation", "Source-linked rules", "Fail-closed ambiguity"],
  note: "The public fixture is synthetic. Production policy ingestion would require owner approval and version control.",
};
