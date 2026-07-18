import type { Product } from "./product-types";

export const product: Product = {
  number: "10",
  name: "Thesis Breaker Japan",
  eyebrow: "Investment theses under pressure",
  tagline: "Know when the evidence has broken your thesis.",
  description: "Write a Japanese equity thesis as testable claims, monitor the evidence that could invalidate it, and surface a review before conviction becomes inertia.",
  accent: "#d7263d",
  inputLabel: "Three-thesis portfolio fixture",
  inputHint: "The same three theses and normalized quarters are evaluated by product.py.",
  inputValue: "T-1 Overseas revenue ratio keeps rising; break after two consecutive declines.\nT-2 Operating margin stays above 12%.\nT-3 Free cash flow remains positive.\nEvidence: 2025-Q3 42/14.1/820; 2025-Q4 40/13.8/610; 2026-Q1 37/13.2/440.",
  actionLabel: "Reveal verified result",
  status: "REVIEW_PORTFOLIO",
  statusTone: "warn",
  metrics: [{ value: "3", label: "theses checked" }, { value: "1", label: "broken" }, { value: "3", label: "page citations" }],
  findings: [
    { title: "T-1 is broken", detail: "Overseas revenue ratio falls 42→40→37 across two consecutive periods.", badge: "BROKEN", tone: "bad" },
    { title: "T-2 remains intact", detail: "Latest operating margin is 13.2%, above the 12% floor.", badge: "INTACT", tone: "good" },
    { title: "T-3 remains intact", detail: "Latest free cash flow is 440, above the zero floor.", badge: "INTACT", tone: "good" },
  ],
  method: [
    { step: "01", title: "Specify", detail: "Turn each investment belief into a claim with a measurable break condition." },
    { step: "02", title: "Cite", detail: "Connect reported evidence to the exact document page used in the check." },
    { step: "03", title: "Challenge", detail: "Flag crossed triggers and show what evidence would confirm or reverse the result." },
  ],
  proof: ["Explicit break conditions", "Two-period trigger", "Document page citations"],
  note: "This is a synthetic demonstration and not investment advice. Verify all filings independently before acting.",
};
