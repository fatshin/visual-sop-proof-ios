import type { Product } from "./product-types";

const benchmark = {
  "gpt-5.6": { extract: [96, 2.1], reason: [95, 3.2], draft: [93, 2.4] },
  terra: { extract: [92, 1.0], reason: [91, 1.5], draft: [92, 1.1] },
  luna: { extract: [90, 0.4], reason: [84, 0.7], draft: [89, 0.5] },
} as const;
const tasks = ["extract", "reason", "draft"] as const;
const csvRows = ["case_id,task,model,quality,cost"];
for (let index = 0; index < 20; index += 1) {
  const task = tasks[index % tasks.length];
  for (const [model, values] of Object.entries(benchmark)) {
    const [quality, cost] = values[task];
    csvRows.push(`C${String(index + 1).padStart(2, "0")},${task},${model},${quality + (index % 2)},${cost.toFixed(2)}`);
  }
}

export const product: Product = {
  number: "06",
  name: "CostRoute Lab",
  eyebrow: "Quality-constrained model routing",
  tagline: "Find the cheapest route that still clears the quality floor.",
  description: "Evaluate candidate model routes across a fixed task set, reject any route below the quality threshold, and explain the lowest-cost passing combination.",
  accent: "#14a37f",
  inputLabel: "Routing experiment",
  inputHint: "This exact 3-model × 20-case CSV is evaluated by product.py.",
  inputValue: `Quality floor: 91

Evaluation results:
${csvRows.join("\n")}`,
  actionLabel: "Reveal verified result",
  status: "ROUTE_FOUND",
  statusTone: "good",
  metrics: [{ value: "20", label: "fixture cases" }, { value: "91.5", label: "macro-average quality" }, { value: "3.0", label: "normalized three-task bundle cost" }, { value: "61.0%", label: "fixture cost reduction" }],
  findings: [
    { title: "Quality floor cleared", detail: "The selected fixture route has a 91.5 macro-average across the three task-level aggregates derived from twenty cases.", badge: "PASS", tone: "good" },
    { title: "Lowest-cost passing route", detail: "draft→terra, extract→luna, reason→terra costs 3.0 normalized units for one three-task bundle.", badge: "ROUTE", tone: "good" },
    { title: "Baseline remains visible", detail: "The GPT-5.6-only fixture has a 95.17 macro-average and costs 7.7 normalized bundle units.", badge: "BASELINE", tone: "warn" },
  ],
  method: [
    { step: "01", title: "Fix the eval", detail: "Hold cases, scoring, and the quality floor constant across candidates." },
    { step: "02", title: "Enumerate", detail: "Search complete routing combinations instead of hand-picking a winner." },
    { step: "03", title: "Select", detail: "Choose the lowest measured cost among routes that pass every constraint." },
  ],
  proof: ["Complete per-case model coverage", "91-point macro-average floor", "Exhaustive route search"],
  note: "Costs and scores are a reproducible synthetic benchmark, not a universal model-price claim.",
};
