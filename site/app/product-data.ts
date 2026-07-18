import type { Product } from "./product-types";

export const product: Product = {
  number: "03",
  name: "Public Notice Stress Test",
  eyebrow: "Evidence before publication",
  tagline: "Catch the sentence that should stop a public release.",
  description: "Compare a draft public notice with its evidence packet, mark direct contradictions and unsupported claims, and propose precise repairs before publication.",
  accent: "#e04431",
  inputLabel: "Draft notice and evidence",
  inputHint: "The fixture includes direct conflicts and one unsupported statement.",
  inputValue: "Draft: Service was fully restored at 10:00. No customer data was exposed. All users received a notice. Evidence: recovery completed at 10:42; exposure scope remains under investigation; notices reached 82% of users.",
  actionLabel: "Stress-test notice",
  status: "BLOCKED_FOR_RELEASE",
  statusTone: "bad",
  metrics: [{ value: "5", label: "direct conflicts" }, { value: "1", label: "unsupported claim" }, { value: "6", label: "repairs proposed" }],
  findings: [
    { title: "Restoration time conflicts", detail: "The draft says 10:00 while the incident record shows completion at 10:42.", badge: "CONFLICT", tone: "bad" },
    { title: "Exposure claim exceeds evidence", detail: "Investigation is still open, so “no data exposed” is not supportable.", badge: "UNSUPPORTED", tone: "warn" },
    { title: "Notification reach overstated", detail: "Replace “all users” with the measured 82% and explain follow-up delivery.", badge: "REPAIR", tone: "good" },
  ],
  method: [
    { step: "01", title: "Atomize", detail: "Break the notice into individually testable factual claims." },
    { step: "02", title: "Compare", detail: "Link each claim to evidence, a contradiction, or a missing source." },
    { step: "03", title: "Repair", detail: "Provide publishable wording without erasing uncertainty." },
  ],
  proof: ["Claim-level citations", "Release stop gate", "Uncertainty preserved"],
  note: "The incident and notice are synthetic. A communications owner must approve any real public release.",
};
