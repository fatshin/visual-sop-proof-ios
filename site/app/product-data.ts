import type { Product } from "./product-types";

export const product: Product = {
  number: "08",
  name: "Misconception Replay",
  eyebrow: "Correct answer, wrong reason",
  tagline: "Find the misconception hidden behind a correct answer.",
  description: "Compare a learner’s answer and explanation, distinguish knowledge from lucky guessing, and generate a targeted replay that corrects the underlying mental model.",
  accent: "#ff9f1c",
  inputLabel: "Learner response set",
  inputHint: "Twenty labeled cases include five correct answers supported by incorrect reasoning.",
  inputValue: "Question: Why does a metal spoon feel colder than a wooden spoon in the same room? Answer: The metal is colder. Explanation: Metal naturally stores cold while wood produces warmth.",
  actionLabel: "Analyze reasoning",
  status: "EVAL_PASS",
  statusTone: "good",
  metrics: [{ value: "20", label: "labeled cases" }, { value: "5", label: "hidden misconceptions" }, { value: "1.00", label: "fixture F1" }],
  findings: [
    { title: "Answer shape is misleading", detail: "The learner selected the expected option but attributed the result to stored cold.", badge: "MISCONCEPTION", tone: "bad" },
    { title: "Missing concept identified", detail: "Thermal conductivity—not temperature difference—explains the sensation.", badge: "CONCEPT", tone: "warn" },
    { title: "Replay targets the reason", detail: "The follow-up contrasts equal temperature with different heat-transfer rates.", badge: "REPLAY", tone: "good" },
  ],
  method: [
    { step: "01", title: "Separate", detail: "Score the final answer independently from the learner’s causal explanation." },
    { step: "02", title: "Diagnose", detail: "Map the explanation to a specific misconception, not a generic wrong label." },
    { step: "03", title: "Replay", detail: "Generate one contrastive example that tests the corrected mental model." },
  ],
  proof: ["Answer/reason split", "20-case labeled eval", "Targeted replay"],
  note: "The learner responses are synthetic. The fixture F1 measures only the included evaluation set.",
};
