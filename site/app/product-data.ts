import type { Product } from "./product-types";

const dailyRows = ["date,weight_kg,calories,protein_g"];
const startDate = Date.UTC(2026, 5, 19);
for (let index = 0; index < 30; index += 1) {
  const day = new Date(startDate + index * 86_400_000).toISOString().slice(0, 10);
  dailyRows.push(`${day},${(82 - index * 0.08).toFixed(2)},${2200 - (index % 3) * 50},${150 + (index % 4) * 5}`);
}
const workoutsFixture = `date,exercise,weight_kg,reps
2026-06-20,Squat,100,5
2026-07-17,Squat,105,5
2026-06-20,Bench Press,75,6
2026-07-17,Bench Press,77.5,6
2026-06-20,Deadlift,130,4
2026-07-17,Deadlift,137.5,4`;
const bodyFixture = `[
  {"date":"2026-06-19","body_fat_pct":23.4,"lean_mass_kg":62.8},
  {"date":"2026-07-18","body_fat_pct":21.8,"lean_mass_kg":63.0}
]`;

export const product: Product = {
  number: "09",
  name: "Body Recomposition Evidence Engine",
  eyebrow: "Training and body evidence together",
  tagline: "Distinguish useful fat loss from weight loss alone.",
  description: "Combine normalized HealthKit-style activity, strength markers, and body scans to explain whether a change reflects fat loss while performance is preserved.",
  accent: "#1b9aaa",
  inputLabel: "Thirty-day synthetic export",
  inputHint: "These exact normalized CSV and JSON records are evaluated by product.py.",
  inputValue: `Daily synthetic export:
${dailyRows.join("\n")}

Strong workout export:
${workoutsFixture}

Body scans:
${bodyFixture}`,
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
