import type { Product } from "./product-types";

export const product: Product = {
  number: "01",
  name: "Agent Policy Compiler",
  eyebrow: "Policy to executable decisions",
  tagline: "Turn policy prose into a decision system you can audit.",
  description: "Compile one written policy into explicit allow, block, and approval-required outcomes—each linked back to its source.",
  accent: "#ff6b35",
  inputLabel: "Policy fixture",
  inputHint: "Seven realistic requests are evaluated against the included policy.",
  inputValue: "Refunds up to $50 may be issued by support. Refunds above $50 require manager approval. Never refund gift cards. If the account identity is ambiguous, stop and request verification.",
  actionLabel: "Compile and evaluate",
  status: "COMPILED",
  statusTone: "good",
  metrics: [{ value: "7", label: "scenarios" }, { value: "3", label: "allowed" }, { value: "0", label: "uncited decisions" }],
  findings: [
    { title: "Gift-card refund blocked", detail: "The prohibition is direct and cites the matching source sentence.", badge: "BLOCK", tone: "bad" },
    { title: "$80 refund escalated", detail: "The amount exceeds the agent limit, so manager approval is required.", badge: "APPROVAL", tone: "warn" },
    { title: "Ambiguous identity stopped", detail: "The compiler refuses to guess when the customer cannot be verified.", badge: "SAFE STOP", tone: "good" },
  ],
  method: [
    { step: "01", title: "Parse", detail: "Separate permissions, prohibitions, thresholds, and ambiguity clauses." },
    { step: "02", title: "Compile", detail: "Convert every clause into an explicit decision rule with a source citation." },
    { step: "03", title: "Challenge", detail: "Run boundary and ambiguity cases before an agent may use the policy." },
  ],
  proof: ["7-case evaluation", "Source-linked rules", "Fail-closed ambiguity"],
  note: "The public fixture is synthetic. Production policy ingestion would require owner approval and version control.",
};
