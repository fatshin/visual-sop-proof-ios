import type { Product } from "./product-types";

const problemsFixture = [
  { problem: "1/2 + 1/3", answer: "5/6", reasoning: "The common denominator is 6, so 3/6 + 2/6 = 5/6.", replayProblem: "1/2 + 1/2", replayAnswer: "1", replayReasoning: "Both halves make one whole." },
  { problem: "2/3 + 1/4", answer: "11/12", reasoning: "The common denominator is 12, so 8/12 + 3/12 = 11/12.", replayProblem: "2/3 + 1/3", replayAnswer: "1", replayReasoning: "Three thirds make one whole." },
  { problem: "3/4 + 1/6", answer: "11/12", reasoning: "The common denominator is 12, so 9/12 + 2/12 = 11/12.", replayProblem: "3/4 + 1/4", replayAnswer: "1", replayReasoning: "Four fourths make one whole." },
  { problem: "1/5 + 1/2", answer: "7/10", reasoning: "The common denominator is 10, so 2/10 + 5/10 = 7/10.", replayProblem: "1/5 + 4/5", replayAnswer: "1", replayReasoning: "Five fifths make one whole." },
  { problem: "2/5 + 1/3", answer: "11/15", reasoning: "The common denominator is 15, so 6/15 + 5/15 = 11/15.", replayProblem: "2/5 + 3/5", replayAnswer: "1", replayReasoning: "Five fifths make one whole." },
];

const casesFixture = problemsFixture.flatMap((example, problemIndex) =>
  Array.from({ length: 4 }, (_, repetition) => ({
    id: `M${String(problemIndex * 4 + repetition + 1).padStart(2, "0")}`,
    problem: example.problem,
    answer: example.answer,
    reasoning: repetition === 0
      ? `I added both numerators and both denominators, then changed it to ${example.answer}.`
      : example.reasoning,
    label: repetition === 0 ? "ADD_BOTH_PARTS" : "CORRECT",
    replay_problem: example.replayProblem,
    replay_answer: example.replayAnswer,
    replay_reasoning: example.replayReasoning,
  })),
);

export const product: Product = {
  number: "08",
  name: "Misconception Replay",
  eyebrow: "Correct answer, wrong reason",
  tagline: "Find the misconception hidden behind a correct answer.",
  description: "Compare a learner’s answer and explanation, diagnose the rule behind a lucky answer, then verify a pre-authored synthetic replay response on a different problem.",
  accent: "#ff9f1c",
  inputLabel: "Learner response set",
  inputHint: "These exact twenty labeled fraction cases are evaluated by product.py.",
  inputValue: JSON.stringify(casesFixture, null, 2),
  actionLabel: "Reveal verified result",
  status: "EVAL_PASS",
  statusTone: "good",
  metrics: [{ value: "20", label: "labeled cases" }, { value: "5", label: "hidden misconceptions" }, { value: "5/5", label: "replays resolved" }],
  findings: [
    { title: "Correct answers, incorrect rule", detail: "Five varied problems hide the same add-both-parts misconception behind a correct final answer.", badge: "MISCONCEPTION", tone: "bad" },
    { title: "Fixed-set F1 is 1.00", detail: "All five ADD_BOTH_PARTS labels are recovered in the twenty-case fixture.", badge: "EVAL", tone: "good" },
    { title: "Pre-authored replay responses pass verification", detail: "The synthetic fixture already contains five responses to different fraction problems. The evaluator verifies each answer and its actual fraction transformation before producing RESOLVED.", badge: "REPLAY", tone: "good" },
  ],
  method: [
    { step: "01", title: "Separate", detail: "Score the final answer independently from the learner’s causal explanation." },
    { step: "02", title: "Diagnose", detail: "Map the explanation to a specific misconception, not a generic wrong label." },
    { step: "03", title: "Replay", detail: "Verify the fixture’s pre-authored response to a different contrastive problem; mark RESOLVED only when both answer and reasoning are correct." },
  ],
  proof: ["Exact ground-truth recovery", "Mathematically different replays", "Reasoning-checked outcomes"],
  note: "The learner and replay responses are pre-authored synthetic fixtures, not live student attempts or generated tutoring. The F1 score measures only this fixed evaluation set.",
};
