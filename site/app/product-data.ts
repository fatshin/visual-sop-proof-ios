import type { Product } from "./product-types";

export const product: Product = {
  number: "09",
  name: "Body Recomposition Evidence Engine",
  eyebrow: "Training and body evidence together",
  tagline: "Distinguish useful fat loss from weight loss alone.",
  description: "Combine normalized HealthKit-style activity, strength markers, and body scans to explain whether a change reflects fat loss while performance is preserved.",
  accent: "#1b9aaa",
  inputLabel: "Thirty-day synthetic export",
  inputHint: "The same normalized CSV and JSON records are evaluated by product.py.",
  inputValue: "30-day synthetic HealthKit-style weight and nutrition CSV: 82.00→79.68 kg.\nStrong CSV: Bench Press 75×6→77.5×6; Deadlift 130×4→137.5×4; Squat 100×5→105×5.\nBody scans: 23.4%→21.8% body fat; 62.8→63.0 kg lean mass.",
  actionLabel: "Reveal verified result",
  status: "FAT_LOSS_WITH_STRENGTH_PRESERVED",
  statusTone: "good",
  metrics: [{ value: "−2.1kg", label: "EWMA weight change" }, { value: "−1.6pp", label: "body-fat change" }, { value: "+0.2kg", label: "lean-mass change" }],
  findings: [
    { title: "Three estimated 1RMs improve", detail: "Bench Press +3.3%, Deadlift +5.8%, and Squat +5.0% in the fixture.", badge: "PERFORMANCE", tone: "good" },
    { title: "Body-fat percentage declines", detail: "The two snapshots move from 23.4% to 21.8%.", badge: "BODY SCAN", tone: "good" },
    { title: "Raw observations remain local", detail: "The artifact records raw_health_data_sent_to_openai=false.", badge: "PRIVACY", tone: "warn" },
  ],
  method: [
    { step: "01", title: "Normalize", detail: "Align activity, workout, strength, and scan observations to one period." },
    { step: "02", title: "Triangulate", detail: "Require agreement between body change and preserved performance." },
    { step: "03", title: "Explain", detail: "Report the conclusion with uncertainty and the evidence that supports it." },
  ],
  proof: ["30-day synthetic data", "Three strength markers", "No raw health upload"],
  note: "This is not medical advice. The public demo uses synthetic normalized exports and sends no HealthKit data.",
};
