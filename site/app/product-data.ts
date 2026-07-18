import type { Product } from "./product-types";

export const product: Product = {
  number: "09",
  name: "Body Recomposition Evidence Engine",
  eyebrow: "Training and body evidence together",
  tagline: "Distinguish useful fat loss from weight loss alone.",
  description: "Combine normalized HealthKit-style activity, strength markers, and body scans to explain whether a change reflects fat loss while performance is preserved.",
  accent: "#1b9aaa",
  inputLabel: "Thirty-day synthetic export",
  inputHint: "The public fixture includes activity trends, three strength markers, and two scans.",
  inputValue: "30-day activity export: training sessions 14, average steps +8%. Strength: squat +2.5%, press 0%, row +1.8%. Scan: weight −1.9 kg, estimated fat mass −1.6 kg, lean mass within measurement tolerance.",
  actionLabel: "Evaluate recomposition",
  status: "FAT_LOSS_WITH_STRENGTH_PRESERVED",
  statusTone: "good",
  metrics: [{ value: "−1.6kg", label: "estimated fat mass" }, { value: "3/3", label: "strength preserved" }, { value: "30", label: "days analyzed" }],
  findings: [
    { title: "Strength is preserved", detail: "All three tracked markers are stable or improving across the period.", badge: "PERFORMANCE", tone: "good" },
    { title: "Scan direction supports fat loss", detail: "Estimated fat-mass change explains most of the measured weight change.", badge: "BODY SCAN", tone: "good" },
    { title: "Measurement uncertainty retained", detail: "Lean-mass variation stays inside the fixture’s stated scan tolerance.", badge: "CAUTION", tone: "warn" },
  ],
  method: [
    { step: "01", title: "Normalize", detail: "Align activity, workout, strength, and scan observations to one period." },
    { step: "02", title: "Triangulate", detail: "Require agreement between body change and preserved performance." },
    { step: "03", title: "Explain", detail: "Report the conclusion with uncertainty and the evidence that supports it." },
  ],
  proof: ["30-day synthetic data", "Three strength markers", "No raw health upload"],
  note: "This is not medical advice. The public demo uses synthetic normalized exports and sends no HealthKit data.",
};
