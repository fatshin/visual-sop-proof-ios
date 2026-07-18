import type { Product } from "./product-types";

export const product: Product = {
  number: "10",
  name: "Thesis Breaker Japan",
  eyebrow: "Investment theses under pressure",
  tagline: "Know when the evidence has broken your thesis.",
  description: "Write a Japanese equity thesis as testable claims, monitor the evidence that could invalidate it, and surface a review before conviction becomes inertia.",
  accent: "#d7263d",
  inputLabel: "Three-thesis portfolio fixture",
  inputHint: "The included evidence contains one two-period invalidation trigger.",
  inputValue: "Thesis A: domestic orders grow year over year; break after two consecutive declines. Thesis B: gross margin remains above 34%. Thesis C: net cash stays positive. Evidence pages: Q1 p.8, Q2 p.11, balance sheet p.4.",
  actionLabel: "Challenge theses",
  status: "REVIEW_PORTFOLIO",
  statusTone: "warn",
  metrics: [{ value: "3", label: "theses checked" }, { value: "1", label: "broken" }, { value: "3", label: "page citations" }],
  findings: [
    { title: "Thesis A is broken", detail: "Domestic orders declined in two consecutive reported periods, crossing the stated trigger.", badge: "BROKEN", tone: "bad" },
    { title: "Thesis B remains valid", detail: "Reported gross margin remains above the explicit 34% boundary.", badge: "VALID", tone: "good" },
    { title: "Thesis C needs monitoring", detail: "Net cash remains positive, but the buffer narrowed and merits the next-period check.", badge: "WATCH", tone: "warn" },
  ],
  method: [
    { step: "01", title: "Specify", detail: "Turn each investment belief into a claim with a measurable break condition." },
    { step: "02", title: "Cite", detail: "Connect reported evidence to the exact document page used in the check." },
    { step: "03", title: "Challenge", detail: "Flag crossed triggers and show what evidence would confirm or reverse the result." },
  ],
  proof: ["Explicit break conditions", "Two-period trigger", "Document page citations"],
  note: "This is a synthetic demonstration and not investment advice. Verify all filings independently before acting.",
};
