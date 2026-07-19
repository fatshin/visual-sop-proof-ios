import type { Product } from "./product-types";

export const product: Product = {
  number: "04",
  name: "Meeting to Merge",
  eyebrow: "Spoken decisions to reviewable change",
  tagline: "Turn a meeting decision into scenario checks and a minimal diff.",
  description: "Extract a complete, uniquely identified requirement set from a transcript, map it to deterministic scenario checks, and prepare the smallest patch for human review.",
  accent: "#4e78ff",
  inputLabel: "Timestamped transcript",
  inputHint: "This exact transcript and broken source are evaluated by product.py.",
  inputValue: `Transcript:
[00:18] Maya: REQ-1 Checkout must reject a quantity below 1.
[00:44] Ken: REQ-2 Orders over $500 require manager approval.
[01:12] Maya: REQ-3 The receipt must show the order ID.
[01:48] Ken: REQ-4 Retry must not create a second charge.
[02:10] Maya: Approval means a non-empty manager token.

Broken source:
def checkout(quantity, total, manager_token="", order_id=""):
    approved = total >= 500
    charge()
    return {"ok": True, "order": ""}`,
  actionLabel: "Reveal verified result",
  status: "READY_FOR_HUMAN_APPLY",
  statusTone: "good",
  metrics: [{ value: "4", label: "requirements" }, { value: "4", label: "baseline failures" }, { value: "4", label: "scenario passes" }],
  findings: [
    { title: "Four requirements extracted", detail: "REQ-1 through REQ-4 retain their timestamps and speakers.", badge: "TRACEABLE", tone: "good" },
    { title: "Four deterministic scenario checks mapped", detail: "The fixture maps each unique requirement to a named baseline-fail / post-patch-pass scenario. It does not execute the proposed patch.", badge: "VERIFIED", tone: "warn" },
    { title: "Human apply gate preserved", detail: "The unified diff is proposed but never applied automatically.", badge: "REVIEW", tone: "good" },
  ],
  method: [
    { step: "01", title: "Extract", detail: "Identify explicit behaviors, boundaries, and owners with their timestamps." },
    { step: "02", title: "Check", detail: "Map each accepted requirement to one deterministic fixture scenario." },
    { step: "03", title: "Diff", detail: "Prepare only the lines needed to satisfy the tests and await review." },
  ],
  proof: ["Complete unique REQ set", "Structural source validation", "Human-controlled apply"],
  note: "The transcript and patch are synthetic. The public demo runs deterministic scenario checks, does not execute the patch, and never writes to a repository.",
};
