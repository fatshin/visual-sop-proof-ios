import type { Product } from "./product-types";

export const product: Product = {
  number: "05",
  name: "Decision Invalidation Ledger",
  eyebrow: "Decisions that know when they expire",
  tagline: "Detect when new evidence invalidates an old decision.",
  description: "Record decisions with the assumptions that support them, then compare new evidence and show which decisions remain valid, are at risk, or must be reopened.",
  accent: "#8c5cff",
  inputLabel: "Decision ledger update",
  inputHint: "These exact decisions and evidence records are evaluated by product.py.",
  inputValue: `Decisions:
[
  {"id":"D-1","decision":"Use Model A","owner":"Maya","reason":"Best measured quality-cost tradeoff","decided_at":"2026-06-10","invalidate_when":"quality < 80","review_when":"cost > 200000"},
  {"id":"D-2","decision":"Keep vendor B","owner":"Ken","reason":"Uptime remains above the service floor","decided_at":"2026-05-22","invalidate_when":"uptime < 99.5","review_when":"incidents > 2"},
  {"id":"D-3","decision":"Launch workflow C","owner":"Ari","reason":"Pilot completion cleared the launch floor","decided_at":"2026-07-01","invalidate_when":"completion < 90","review_when":"complaints > 5"}
]

Evidence:
{
  "D-1":{"quality":77,"cost":180000,"source":"eval-2026-07-18.csv"},
  "D-2":{"uptime":99.8,"incidents":1,"source":"status-q2.json"},
  "D-3":{"completion":93,"complaints":7,"source":"launch-week.csv"}
}`,
  actionLabel: "Reveal verified result",
  status: "ACTION_REQUIRED",
  statusTone: "warn",
  metrics: [{ value: "1", label: "valid" }, { value: "1", label: "at risk" }, { value: "1", label: "invalidated" }, { value: "0", label: "needs evidence" }],
  findings: [
    { title: "D-1 is invalidated", detail: "quality=77 is below the explicit floor of 80.", badge: "INVALIDATED", tone: "bad" },
    { title: "D-2 remains valid", detail: "uptime=99.8 remains above the 99.5 invalidation boundary.", badge: "VALID", tone: "good" },
    { title: "D-3 is at risk", detail: "complaints=7 crosses the review trigger of 5.", badge: "AT RISK", tone: "warn" },
  ],
  method: [
    { step: "01", title: "Register", detail: "Store the decision, owner, reason, decision date, assumptions, evidence, and review trigger." },
    { step: "02", title: "Compare", detail: "Match new facts to the assumptions they can weaken or replace." },
    { step: "03", title: "Reopen", detail: "Emit an owner-linked status transition with the exact evidence that crossed the trigger." },
  ],
  proof: ["Explicit assumptions", "Fail-closed evidence state", "Owner-linked status events"],
  note: "The ledger fixture is synthetic. A missing value, condition, source, owner, reason, or decision date produces NEEDS_EVIDENCE; missing or duplicate IDs produce INVALID_INPUT.",
};
