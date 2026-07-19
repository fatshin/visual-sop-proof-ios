import type { Product } from "./product-types";

export const product: Product = {
  number: "03",
  name: "Public Notice Stress Test",
  eyebrow: "Evidence before publication",
  tagline: "Catch the sentence that should stop a public release.",
  description: "Compare a draft public notice with its evidence packet, mark direct contradictions and unsupported claims, and propose precise repairs before publication.",
  accent: "#e04431",
  inputLabel: "Draft notice and evidence",
  inputHint: "This exact notice and five-field source record are evaluated by product.py.",
  inputValue: `Draft notice:
Emergency Support Benefit
Apply by 2026-09-30 at 23:59.
Every resident aged 16 or older receives ¥70,000 automatically.
You must have lived in the city by 2026-05-01.
Questions: support@example.go.jp
Applications submitted after the deadline may still be accepted.

Authoritative source:
{"deadline":"2026-08-31","amount_yen":50000,"minimum_age":18,"residency_date":"2026-04-01","faq_contact":"benefits@example.go.jp"}`,
  actionLabel: "Reveal verified result",
  status: "BLOCKED_FOR_RELEASE",
  statusTone: "bad",
  metrics: [{ value: "5", label: "direct conflicts" }, { value: "1", label: "unsupported claim" }, { value: "6", label: "repairs proposed" }],
  findings: [
    { title: "Five source values conflict", detail: "Deadline, amount, age, residency date, and contact address disagree with the source.", badge: "5 CONFLICTS", tone: "bad" },
    { title: "Late-application promise is unsupported", detail: "No source field supports the added exception.", badge: "UNSUPPORTED", tone: "warn" },
    { title: "Six linked repair instructions", detail: "Each instruction names the exact source field; a communications owner still drafts and approves wording.", badge: "REPAIR", tone: "good" },
  ],
  method: [
    { step: "01", title: "Atomize", detail: "Break the notice into individually testable factual claims." },
    { step: "02", title: "Compare", detail: "Link each claim to evidence, a contradiction, or a missing source." },
    { step: "03", title: "Repair", detail: "Provide source-linked repair instructions without claiming that generated wording is publishable." },
  ],
  proof: ["Claim-level citations", "Release stop gate", "Uncertainty preserved"],
  note: "The incident and notice are synthetic. A communications owner must approve any real public release.",
};
