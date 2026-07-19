import { looksSensitive } from "./privacy.js";

const sampleMemories = [
  {
    id: "sample-obsidian-1",
    source: "Obsidian",
    title: "転職について考えた日",
    text: "今の仕事を続ける安心と、新しい役割へ挑戦したい気持ちの間で迷っている。",
    path: "Daily/2026-07-12.md",
    selected: true,
  },
  {
    id: "sample-obsidian-2",
    source: "Obsidian",
    title: "半年後にしたいこと",
    text: "研究だけでなく、利用者へ届くプロダクトを自分の責任で育てたい。",
    path: "Career/半年後.md",
    selected: true,
  },
  {
    id: "sample-chatgpt-memory",
    source: "ChatGPT Memory",
    title: "Decision style",
    text: "大きな決断では、選択肢を比較できる表と撤退条件があると安心して進められる。",
    path: "",
    selected: true,
  },
  {
    id: "sample-chatgpt-chat",
    source: "ChatGPT conversation",
    title: "働き方の相談",
    text: "転職する前に、小さな社内プロジェクトで自分の仮説を試せないだろうか。",
    path: "conversations.json",
    selected: true,
  },
];

const traditions = [
  ["易経", "水雷屯", "動き出す前に、足場と助けを整える"],
  ["四柱推命", "調候", "強みを押し通すより、環境との釣り合いを取る"],
  ["九星気学", "坎宮", "見えない準備を重ね、焦って結論を急がない"],
  ["宿曜占星術", "栄親", "関係を断つ前に、育てられる縁を見分ける"],
  ["西洋占星術", "土星と水星", "考えを言葉と期限に変えて、現実に照らす"],
  ["タロット", "隠者", "外の正解より、過去の自分が残した手掛かりを読む"],
  ["数秘術", "7", "情報を集める時間と、決める時間を分ける"],
  ["ルーン", "Jera", "結果を急がず、積み重ねが実る周期を尊重する"],
  ["ジオマンシー", "Conjunctio", "一人で閉じず、異なる情報を接続する"],
  ["月相・暦", "上弦", "小さく試し、次の節目で見直す"],
];

const themeTerms = {
  仕事: ["仕事", "転職", "職場", "career", "job", "会社", "プロジェクト"],
  関係: ["関係", "恋愛", "家族", "友人", "partner", "relationship", "人間関係"],
  健康: ["健康", "体調", "食事", "睡眠", "運動", "health"],
  お金: ["お金", "投資", "支出", "収入", "money", "budget", "資産"],
  学び: ["学び", "勉強", "研究", "資格", "learn", "study"],
  変化: ["変化", "迷い", "決断", "選択", "change", "decision"],
};

const state = { memories: [], reading: null };
const MAX_MEMORIES = 500;
const byId = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function makeId(source, title, text) {
  let hash = 2166136261;
  const input = `${source}|${title}|${text}`;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `m-${(hash >>> 0).toString(16)}`;
}

function showToast(message) {
  const toast = byId("toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2400);
}

function addMemories(items) {
  const known = new Set(state.memories.map((item) => item.id));
  let added = 0;
  for (const item of items) {
    if (state.memories.length >= MAX_MEMORIES) break;
    const screenText = `${item.title}\n${item.path || ""}\n${item.text}`;
    if (!known.has(item.id) && item.text.trim().length >= 8 && !looksSensitive(screenText)) {
      state.memories.push({ ...item, selected: true });
      known.add(item.id);
      added += 1;
    }
  }
  renderMemories();
  return added;
}

function loadSamples() {
  const added = addMemories(sampleMemories.map((item) => ({ ...item })));
  byId("import").scrollIntoView({ behavior: "smooth", block: "start" });
  showToast(`${added}件のサンプル記憶を読み込みました`);
}

function renderMemories() {
  const list = byId("memory-list");
  const selected = state.memories.filter((item) => item.selected).length;
  byId("selected-count").textContent = selected;
  if (!state.memories.length) {
    list.className = "memory-list empty-state";
    list.innerHTML = "<p>まだ記憶は読み込まれていません。</p><button id=\"sample-inline\">4件のサンプルを読み込む</button>";
    byId("sample-inline").addEventListener("click", loadSamples);
    return;
  }
  list.className = "memory-list";
  list.innerHTML = state.memories
    .map(
      (item, index) => `
        <label class="memory-item ${item.selected ? "" : "off"}">
          <span class="source">${escapeHtml(item.source)}${item.path ? ` · ${escapeHtml(item.path)}` : ""}</span>
          <h4>${escapeHtml(item.title)}</h4>
          <p>${escapeHtml(item.text.slice(0, 180))}</p>
          <input type="checkbox" data-memory-index="${index}" ${item.selected ? "checked" : ""} aria-label="${escapeHtml(item.title)}を使用">
        </label>`,
    )
    .join("");
  list.querySelectorAll("input[data-memory-index]").forEach((input) => {
    input.addEventListener("change", (event) => {
      state.memories[Number(event.target.dataset.memoryIndex)].selected = event.target.checked;
      renderMemories();
    });
  });
}

function cleanMarkdown(text) {
  const frontmatter = text.match(/^---\s*\n([\s\S]*?)\n---\s*(?:\n|$)/u);
  if (frontmatter && /^[A-Za-z0-9_-]+\s*:/mu.test(frontmatter[1])) {
    text = text.slice(frontmatter[0].length);
  }
  return text
    .replace(/^#\s+.+\n?/mu, "")
    .replace(/^#{1,6}\s+/gmu, "")
    .replace(/!?\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/gu, "$1")
    .replace(/!\[([^\]]*)\]\([^)]+\)/gu, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/gu, "$1")
    .replace(/\s+/gu, " ")
    .trim();
}

async function readObsidianFiles(fileList) {
  const files = [...fileList]
    .filter((file) => file.name.toLowerCase().endsWith(".md"))
    .filter((file) => !(file.webkitRelativePath || file.name).split("/").some((part) => part.startsWith(".")))
    .slice(0, 500);
  const items = [];
  for (const file of files) {
    if (file.size > 1_000_000) continue;
    const raw = await file.text();
    const title = raw.match(/^#\s+(.+)$/mu)?.[1]?.trim() || file.name.replace(/\.md$/iu, "");
    const text = cleanMarkdown(raw).slice(0, 800);
    const path = file.webkitRelativePath || file.name;
    items.push({ id: makeId("Obsidian", title, text), source: "Obsidian", title, text, path });
  }
  const added = addMemories(items);
  showToast(`${added}件のObsidianノートを読み込みました`);
}

function conversationRecords(data, fileName) {
  const conversations = Array.isArray(data) ? data : data.conversations || [data];
  const items = [];
  for (const conversation of conversations.slice(0, 500)) {
    if (!conversation || typeof conversation !== "object" || !conversation.mapping) continue;
    const userParts = [];
    for (const node of Object.values(conversation.mapping)) {
      const message = node?.message;
      if (message?.author?.role !== "user") continue;
      for (const part of message?.content?.parts || []) {
        if (typeof part === "string" && part.trim()) userParts.push(part);
      }
    }
    const text = userParts.join(" ").replace(/\s+/gu, " ").trim().slice(0, 800);
    if (!text) continue;
    const title = conversation.title || "Untitled conversation";
    items.push({
      id: makeId("ChatGPT conversation", title, text),
      source: "ChatGPT conversation",
      title,
      text,
      path: fileName,
    });
  }
  return items;
}

async function readChatGptFile(file) {
  if (!file) return;
  if (file.size > 25_000_000) {
    showToast("25 MBを超えるファイルは読み込めません");
    return;
  }
  try {
    const data = JSON.parse(await file.text());
    const items = conversationRecords(data, file.name);
    const added = addMemories(items);
    showToast(`${added}件のChatGPT会話からユーザー発言を読み込みました`);
  } catch {
    showToast("ChatGPT JSONを読み込めませんでした");
  }
}

function addMemorySummary() {
  const lines = byId("memory-summary").value
    .split("\n")
    .map((line) => line.replace(/^\s*(?:[-*•]|\d+[.)])\s*/u, "").trim())
    .filter((line) => line.length >= 8)
    .filter((line) => !looksSensitive(line));
  const items = lines.map((text, index) => ({
    id: makeId("ChatGPT Memory", `Memory ${index + 1}`, text),
    source: "ChatGPT Memory",
    title: `Memory ${index + 1}`,
    text: text.slice(0, 800),
    path: "",
  }));
  const added = addMemories(items);
  byId("memory-summary").value = "";
  byId("memory-input").classList.add("hidden");
  showToast(`${added}件のMemory summaryを追加しました`);
}

function detectThemes(memories) {
  const text = memories.map((item) => item.text.toLowerCase()).join(" ");
  return Object.entries(themeTerms)
    .map(([theme, terms]) => ({
      theme,
      mentions: terms.reduce((sum, term) => sum + text.split(term.toLowerCase()).length - 1, 0),
    }))
    .filter((item) => item.mentions > 0)
    .sort((a, b) => b.mentions - a.mentions || a.theme.localeCompare(b.theme));
}

function seedFor(text) {
  let result = 0;
  for (let index = 0; index < text.length; index += 1) {
    result = (result * 31 + text.charCodeAt(index)) >>> 0;
  }
  return result;
}

function createReading() {
  const question = byId("question").value.replace(/\s+/gu, " ").trim();
  const memories = state.memories.filter((item) => item.selected);
  if (question.length < 4) {
    showToast("問いを4文字以上で入力してください");
    return;
  }
  if (!memories.length) {
    showToast("占いに使う記憶を1件以上選んでください");
    byId("import").scrollIntoView({ behavior: "smooth" });
    return;
  }
  const themes = detectThemes(memories);
  const seed = seedFor(`${question}|${memories.map((item) => item.id).join("|")}`);
  const readings = traditions.map(([method, symbol, guidance], index) => {
    const memory = memories[(seed + index * 7) % memories.length];
    return { method, symbol, guidance, memory };
  });
  const leading = themes.slice(0, 3).map((item) => item.theme);
  const synthesis =
    `選んだ記憶には「${leading.length ? leading.join("・") : "変化"}」が繰り返し現れています。` +
    "象徴は結論を断定せず、過去の自分が残した手掛かりを別の角度から照らします。";
  state.reading = { question, memories, themes, readings, synthesis };
  renderReading();
}

function renderReading() {
  const { themes, readings, synthesis } = state.reading;
  byId("synthesis").textContent = synthesis;
  byId("theme-row").innerHTML = (themes.length ? themes.slice(0, 5) : [{ theme: "変化", mentions: 1 }])
    .map((item) => `<span>${escapeHtml(item.theme)} · ${item.mentions}</span>`)
    .join("");
  byId("reading-grid").innerHTML = readings
    .map(
      (item, index) => `
        <article class="reading-card">
          <span class="reading-number">${String(index + 1).padStart(2, "0")} / 10</span>
          <h3>${escapeHtml(item.method)}</h3>
          <p class="symbol">${escapeHtml(item.symbol)}</p>
          <p>${escapeHtml(item.guidance)}。</p>
          <p class="memory-link">記憶「${escapeHtml(item.memory.title)}」と照合</p>
        </article>`,
    )
    .join("");
  const result = byId("result");
  result.classList.remove("hidden");
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildMarkdown() {
  const { question, memories, themes, readings, synthesis } = state.reading;
  const lines = [
    "---",
    "type: oracle-council-reading",
    "status: REFLECTION_READY",
    `memory_count: ${memories.length}`,
    "themes:",
    ...(themes.length ? themes.slice(0, 5).map((item) => `  - ${item.theme}`) : ["  - 変化"]),
    "review_after_days: 7",
    "---",
    "",
    "# Oracle Council リーディング",
    "",
    "## 今回の問い",
    "",
    question,
    "",
    "## 記憶から見えたテーマ",
    "",
    synthesis,
    "",
    "## 10の占術による読み",
    "",
  ];
  readings.forEach((item) => {
    lines.push(
      `### ${item.method} — ${item.symbol}`,
      "",
      `${item.guidance}。`,
      "",
      `参照した記憶: [[Oracle Memory/${item.memory.title}]]`,
      "",
    );
  });
  lines.push("## 使用した記憶", "");
  memories.forEach((item) => lines.push(`- ${item.source}: ${item.title}${item.path ? ` — \`${item.path}\`` : ""}`));
  lines.push(
    "",
    "## 次の一歩",
    "",
    "24時間以内に確認できる事実を一つ調べ、7日後にこの読みを振り返ります。",
    "",
    "## 注意",
    "",
    "この結果は娯楽と内省のためのものです。医療、法律、投資、安全に関する判断には使用しません。",
    "",
    "## 7日後の振り返り",
    "",
    "- 実際に確認した事実:",
    "- 取った行動:",
    "- 今読むと違って見える部分:",
    "",
  );
  return lines.join("\n");
}

function downloadNote() {
  if (!state.reading) return;
  const blob = new Blob([buildMarkdown()], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `Oracle-Council-${new Date().toISOString().slice(0, 10)}.md`;
  link.click();
  URL.revokeObjectURL(url);
  showToast("Obsidian用Markdownを保存しました");
}

byId("start-demo").addEventListener("click", loadSamples);
byId("toggle-memory").addEventListener("click", () => byId("memory-input").classList.toggle("hidden"));
byId("add-summary").addEventListener("click", addMemorySummary);
byId("obsidian-files").addEventListener("change", (event) => readObsidianFiles(event.target.files));
byId("obsidian-folder").addEventListener("change", (event) => readObsidianFiles(event.target.files));
byId("chatgpt-file").addEventListener("change", (event) => readChatGptFile(event.target.files[0]));
byId("create-reading").addEventListener("click", createReading);
byId("download-note").addEventListener("click", downloadNote);
renderMemories();
