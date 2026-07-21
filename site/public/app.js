import { looksSensitive } from "./privacy.js";
import { personalDataExportPrompt } from "./prompt.js";
import {
  buildReadingMarkdown,
  createDeepReading,
  readingText,
  TRADITIONS,
  validateBirthInput,
} from "./reading.js";

const copy = {
  en: {
    heroEyebrow: "TEN TRADITIONS. YOUR BIRTH CONTEXT. YOUR MEMORY.",
    heroTitle: "Before asking the future,<br><em>read your own evidence.</em>",
    heroLead:
      "Connect birth context with selected Obsidian notes and ChatGPT memories. Every reading explains why it may fit and offers three concrete actions.",
    startSample: "Start with a sample",
    enterContext: "Enter my context",
    birthEyebrow: "REQUIRED BIRTH CONTEXT",
    birthHeading: "Give the symbols<br>a real point of reference.",
    birthIntro:
      "Date, time, and place are required. Approximate or unknown information is accepted when you label its precision.",
    birthDate: "Birth date",
    birthTime: "Birth time",
    timePrecision: "Time precision",
    birthPlace: "Birth place",
    placePrecision: "Place precision",
    exact: "Exact",
    approximate: "Approximate",
    unknown: "Unknown",
    birthTimePlaceholder: "14:30 / morning / unknown",
    birthPlacePlaceholder: "Tokyo / Kanto area / unknown",
    birthNote:
      "These values stay in this browser session only. A downloaded note will include the birth details you entered, so review it before sharing. This demo does not calculate a full natal chart, BaZi chart, or lunar mansion.",
    memoryEyebrow: "MEMORY EVIDENCE",
    memoryHeading: "You decide which memories<br>the reading may use.",
    memoryIntro: "Files are processed inside this browser. A deselected memory cannot appear in the result.",
    obsidianTitle: "Vault notes",
    obsidianBody: "Choose Markdown files or a vault folder. Hidden configuration folders are excluded.",
    chooseMarkdown: "Choose Markdown",
    chooseVault: "Choose vault folder",
    chatgptTitle: "Conversations and Memory summary",
    chatgptBody: "Use an extracted conversations.json or paste the Memory summary from settings.",
    chooseJson: "Choose JSON",
    pasteMemory: "Paste Memory summary",
    exportPrompt: "Create a personal-data export prompt",
    promptEyebrow: "SAFE EXPORT PROMPT",
    promptTitle: "Ask ChatGPT to summarize usable personal context.",
    promptIntro: "Paste this prompt into ChatGPT or another assistant, review its output, then paste only the memories you approve below.",
    promptAriaLabel: "Personal-data export prompt",
    copyPrompt: "Copy prompt",
    promptCopied: "Personal-data export prompt copied",
    promptCopyError: "Copy was blocked. Select the prompt and copy it manually.",
    memorySummaryLabel: "ChatGPT Memory summary",
    memorySummaryPlaceholder:
      "• I feel safer when a big decision has comparison criteria\n• I review important choices after one week",
    addMemory: "Add as memories",
    consentEyebrow: "CONSENT BEFORE INTERPRETATION",
    importedMemories: "Imported memories",
    questionEyebrow: "YOUR QUESTION",
    questionLabel: "What do you need to understand now?",
    highRiskWarning: "Do not use this for medical, legal, financial, or safety decisions.",
    createReading: "Create ten grounded readings",
    resultEyebrow: "THE COUNCIL HAS SPOKEN",
    resultHeading: "Where birth context,<br>memory, and action meet.",
    nextEyebrow: "A GROUNDED NEXT STEP",
    nextHeading: "Return the reading to action.",
    nextBody: "Choose one action from one lens within 24 hours, then review the evidence in seven days.",
    saveObsidian: "Save an Obsidian note",
    disclaimer:
      "This is entertainment and structured reflection, not a factual prediction or a substitute for professional judgment.",
    noMemories: "No memories have been imported yet.",
    sampleInline: "Load four sample memories",
    useMemory: "Use",
    contextLabel: "What this lens sees",
    resonanceLabel: "Why this may land",
    actionLabel: "Three ways to act",
    sampleLoaded: (count) => `${count} sample memories loaded`,
    obsidianLoaded: (count) => `${count} Obsidian notes loaded`,
    chatgptLoaded: (count) => `${count} user-memory records loaded from ChatGPT conversations`,
    summaryLoaded: (count) => `${count} Memory summary records added`,
    tooLarge: "Files larger than 25 MB cannot be imported",
    invalidJson: "The ChatGPT JSON could not be read",
    questionError: "Enter a question with at least four characters",
    memoryError: "Select at least one memory",
    birthDateError: "Enter a valid birth date that is not in the future",
    birthTimeError: "Enter a birth time, an approximate time, or “unknown”",
    birthPlaceError: "Enter a birth place, an approximate area, or “unknown”",
    birthPrecisionError: "Choose exact, approximate, or unknown for both precision fields",
    readingError: "The reading could not be created. Review the inputs and try again.",
    noteSaved: "Obsidian Markdown saved",
    defaultQuestion: "What evidence should I create before moving into my next role?",
  },
  ja: {
    heroEyebrow: "10の占術。出生情報。あなた自身の記憶。",
    heroTitle: "未来を占う前に、<br><em>自分の根拠</em>を読む。",
    heroLead:
      "出生情報と、選んだObsidianノート・ChatGPTの記憶を接続します。各占術は、なぜ腹落ちするのかと具体的な行動3案まで示します。",
    startSample: "サンプルで始める",
    enterContext: "出生情報を入れる",
    birthEyebrow: "必須の出生情報",
    birthHeading: "象徴に、現実の<br>基準点を与える。",
    birthIntro:
      "生年月日・出生時刻・出生場所は必須です。精度を明示すれば、おおよそや不明でも入力できます。",
    birthDate: "生年月日",
    birthTime: "出生時刻",
    timePrecision: "時刻の精度",
    birthPlace: "出生場所",
    placePrecision: "場所の精度",
    exact: "正確",
    approximate: "おおよそ",
    unknown: "不明",
    birthTimePlaceholder: "14:30 / 朝ごろ / 不明",
    birthPlacePlaceholder: "東京都 / 関東地方 / 不明",
    birthNote:
      "値はこのブラウザセッション内だけで使います。保存するノートには入力した出生情報が含まれるため、共有前に確認してください。完全な出生図・命式・宿を算出するものではありません。",
    memoryEyebrow: "記憶による根拠",
    memoryHeading: "占いに使う記憶を、<br>あなたが決める。",
    memoryIntro: "ファイルはブラウザ内で処理されます。選択を外した記憶は結果に使用しません。",
    obsidianTitle: "Vaultのノート",
    obsidianBody: "MarkdownファイルまたはVaultフォルダを選びます。隠し設定フォルダは除外します。",
    chooseMarkdown: "Markdownを選ぶ",
    chooseVault: "Vaultフォルダを選ぶ",
    chatgptTitle: "会話とMemory summary",
    chatgptBody: "展開したconversations.json、または設定からコピーしたMemory summaryを使います。",
    chooseJson: "JSONを選ぶ",
    pasteMemory: "Memory summaryを貼る",
    exportPrompt: "パーソナルデータ書き出しプロンプトを作る",
    promptEyebrow: "安全な書き出しプロンプト",
    promptTitle: "ChatGPTに、占いへ使える自分の文脈を整理させる。",
    promptIntro: "このプロンプトをChatGPTなどへ貼り、出力を自分で確認してから、使用を許可する記憶だけを下へ貼り付けてください。",
    promptAriaLabel: "パーソナルデータ書き出しプロンプト",
    copyPrompt: "プロンプトをコピー",
    promptCopied: "書き出しプロンプトをコピーしました",
    promptCopyError: "自動コピーできませんでした。プロンプトを選択して手動でコピーしてください。",
    memorySummaryLabel: "ChatGPTのMemory summary",
    memorySummaryPlaceholder:
      "・大きな決断では比較基準があると安心する\n・重要な選択は一週間後に振り返る",
    addMemory: "記憶として追加する",
    consentEyebrow: "解釈前の同意",
    importedMemories: "取り込んだ記憶",
    questionEyebrow: "今回の問い",
    questionLabel: "今、何を読み解きたいですか。",
    highRiskWarning: "医療・法律・投資・安全の判断には使用できません。",
    createReading: "10の占術で深く読み解く",
    resultEyebrow: "10の視点による回答",
    resultHeading: "出生情報・記憶・行動が<br>重なる場所。",
    nextEyebrow: "現実に戻す一歩",
    nextHeading: "占いを、行動に戻す。",
    nextBody: "一つの占術から行動案を一つ選び、24時間以内に実行して7日後に証拠を見直します。",
    saveObsidian: "Obsidianノートを保存",
    disclaimer:
      "これは娯楽と構造化された内省です。未来の事実を予測したり、専門家の判断に代わったりするものではありません。",
    noMemories: "まだ記憶は読み込まれていません。",
    sampleInline: "4件のサンプル記憶を読み込む",
    useMemory: "使用",
    contextLabel: "この占術が見るもの",
    resonanceLabel: "なぜ腹落ちするのか",
    actionLabel: "行動に移す3案",
    sampleLoaded: (count) => `${count}件のサンプル記憶を読み込みました`,
    obsidianLoaded: (count) => `${count}件のObsidianノートを読み込みました`,
    chatgptLoaded: (count) => `${count}件のChatGPT会話からユーザー発言を読み込みました`,
    summaryLoaded: (count) => `${count}件のMemory summaryを追加しました`,
    tooLarge: "25 MBを超えるファイルは読み込めません",
    invalidJson: "ChatGPT JSONを読み込めませんでした",
    questionError: "問いを4文字以上で入力してください",
    memoryError: "占いに使う記憶を1件以上選んでください",
    birthDateError: "未来日ではない正しい生年月日を入力してください",
    birthTimeError: "出生時刻・おおよその時間帯・「不明」のいずれかを入力してください",
    birthPlaceError: "出生場所・おおよその地域・「不明」のいずれかを入力してください",
    birthPrecisionError: "時刻と場所の精度を「正確・おおよそ・不明」から選んでください",
    readingError: "リーディングを作成できませんでした。入力内容を確認して、もう一度お試しください。",
    noteSaved: "Obsidian用Markdownを保存しました",
    defaultQuestion: "次の役割へ進む前に、どのような証拠を作るべきですか。",
  },
};

const traditionNames = {
  en: TRADITIONS.map((tradition) => tradition.method.en),
  ja: TRADITIONS.map((tradition) => tradition.method.ja),
};

const sampleMemories = [
  {
    id: "sample-obsidian-1",
    source: "Obsidian",
    title: { en: "The day I considered changing roles", ja: "転職について考えた日" },
    text: {
      en: "I feel torn between the safety of continuing my current work and the desire to take responsibility for a new role.",
      ja: "今の仕事を続ける安心と、新しい役割へ挑戦したい気持ちの間で迷っている。",
    },
    path: "Daily/2026-07-12.md",
  },
  {
    id: "sample-obsidian-2",
    source: "Obsidian",
    title: { en: "What I want six months from now", ja: "半年後にしたいこと" },
    text: {
      en: "I want to do more than research. I want to own and grow a product that reaches real users.",
      ja: "研究だけでなく、利用者へ届くプロダクトを自分の責任で育てたい。",
    },
    path: "Career/six-months.md",
  },
  {
    id: "sample-chatgpt-memory",
    source: "ChatGPT Memory",
    title: { en: "Decision style", ja: "決断の仕方" },
    text: {
      en: "I move with more confidence when a major decision has comparison criteria and a clear exit condition.",
      ja: "大きな決断では、選択肢を比較できる表と撤退条件があると安心して進められる。",
    },
    path: "",
  },
  {
    id: "sample-chatgpt-chat",
    source: "ChatGPT conversation",
    title: { en: "A conversation about how I work", ja: "働き方の相談" },
    text: {
      en: "Before changing jobs, could I test my hypothesis through a small internal project?",
      ja: "転職する前に、小さな社内プロジェクトで自分の仮説を試せないだろうか。",
    },
    path: "conversations.json",
  },
];

const themeTerms = {
  仕事: ["仕事", "転職", "職場", "career", "job", "role", "work", "product", "会社", "プロジェクト"],
  関係: ["関係", "恋愛", "家族", "友人", "partner", "relationship", "人間関係"],
  健康: ["健康", "体調", "食事", "睡眠", "運動", "health", "recovery"],
  お金: ["お金", "投資", "支出", "収入", "money", "budget", "資産"],
  学び: ["学び", "勉強", "研究", "資格", "learn", "study", "research"],
  変化: ["変化", "迷い", "決断", "選択", "change", "decision", "move"],
};

const state = {
  lang: safeStoredLanguage(),
  memories: [],
  reading: null,
};
const MAX_MEMORIES = 500;
const byId = (id) => document.getElementById(id);

function safeStoredLanguage() {
  try {
    const stored = localStorage.getItem("oracle-council-language");
    return stored === "ja" ? "ja" : "en";
  } catch {
    return "en";
  }
}

function localized(value) {
  return typeof value === "object" && value !== null ? value[state.lang] : value;
}

function displayMemory(item) {
  return { ...item, title: localized(item.title), text: localized(item.text) };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderProse(value) {
  return String(value)
    .split(/\n{2,}/u)
    .map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`)
    .join("");
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
  window.setTimeout(() => toast.classList.remove("show"), 2600);
}

function setLanguage(lang, { replaceQuestion = true } = {}) {
  state.lang = lang === "ja" ? "ja" : "en";
  document.documentElement.lang = state.lang;
  document.title =
    state.lang === "ja"
      ? "Oracle Council — 自分の根拠から次の行動を選ぶ"
      : "Oracle Council — Ground symbols in your own history";
  try {
    localStorage.setItem("oracle-council-language", state.lang);
  } catch {
    // Language persistence is optional; no personal data is stored.
  }
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = copy[state.lang][element.dataset.i18n];
    if (typeof value === "string") element.textContent = value;
  });
  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    const value = copy[state.lang][element.dataset.i18nHtml];
    if (typeof value === "string") element.innerHTML = value;
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = copy[state.lang][element.dataset.i18nPlaceholder];
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", copy[state.lang][element.dataset.i18nAriaLabel]);
  });
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.lang === state.lang));
  });
  document.querySelectorAll("[data-tradition]").forEach((element) => {
    element.textContent = traditionNames[state.lang][Number(element.dataset.tradition)];
  });
  if (replaceQuestion && !state.reading) byId("question").value = copy[state.lang].defaultQuestion;
  if (!byId("prompt-output").classList.contains("hidden")) {
    byId("personal-data-prompt").value = personalDataExportPrompt(state.lang);
  }
  renderMemories();
  if (state.reading) createReading();
}

function addMemories(items) {
  const known = new Set(state.memories.map((item) => item.id));
  let added = 0;
  for (const item of items) {
    if (state.memories.length >= MAX_MEMORIES) break;
    const screenText = `${localized(item.title)}\n${item.path || ""}\n${localized(item.text)}`;
    if (!known.has(item.id) && String(localized(item.text)).trim().length >= 8 && !looksSensitive(screenText)) {
      state.memories.push({ ...item, selected: true });
      known.add(item.id);
      added += 1;
    }
  }
  renderMemories();
  return added;
}

function loadSamples() {
  byId("birth-date").value = "1990-04-18";
  byId("birth-time").value = state.lang === "ja" ? "朝8時ごろ" : "around 08:00";
  byId("birth-time-precision").value = "approximate";
  byId("birth-place").value = state.lang === "ja" ? "東京都" : "Tokyo, Japan";
  byId("birth-place-precision").value = "exact";
  byId("question").value = copy[state.lang].defaultQuestion;
  const added = addMemories(sampleMemories.map((item) => ({ ...item })));
  byId("birth").scrollIntoView({ behavior: "smooth", block: "start" });
  showToast(copy[state.lang].sampleLoaded(added));
}

function renderMemories() {
  const list = byId("memory-list");
  const selected = state.memories.filter((item) => item.selected).length;
  byId("selected-count").textContent = selected;
  if (!state.memories.length) {
    list.className = "memory-list empty-state";
    list.innerHTML = `<p>${escapeHtml(copy[state.lang].noMemories)}</p><button id="sample-inline">${escapeHtml(
      copy[state.lang].sampleInline,
    )}</button>`;
    byId("sample-inline").addEventListener("click", loadSamples);
    return;
  }
  list.className = "memory-list";
  list.innerHTML = state.memories
    .map((rawItem, index) => {
      const item = displayMemory(rawItem);
      return `
        <label class="memory-item ${rawItem.selected ? "" : "off"}">
          <span class="source">${escapeHtml(item.source)}${item.path ? ` · ${escapeHtml(item.path)}` : ""}</span>
          <h4>${escapeHtml(item.title)}</h4>
          <p>${escapeHtml(item.text.slice(0, 180))}</p>
          <input type="checkbox" data-memory-index="${index}" ${rawItem.selected ? "checked" : ""}
            aria-label="${escapeHtml(`${copy[state.lang].useMemory}: ${item.title}`)}">
        </label>`;
    })
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
    .slice(0, MAX_MEMORIES);
  const items = [];
  for (const file of files) {
    if (file.size > 1_000_000) continue;
    const raw = await file.text();
    const title = raw.match(/^#\s+(.+)$/mu)?.[1]?.trim() || file.name.replace(/\.md$/iu, "");
    const text = cleanMarkdown(raw).slice(0, 800);
    const path = file.webkitRelativePath || file.name;
    items.push({ id: makeId("Obsidian", title, text), source: "Obsidian", title, text, path });
  }
  showToast(copy[state.lang].obsidianLoaded(addMemories(items)));
}

function conversationRecords(data, fileName) {
  const conversations = Array.isArray(data) ? data : data.conversations || [data];
  const items = [];
  for (const conversation of conversations.slice(0, MAX_MEMORIES)) {
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
    showToast(copy[state.lang].tooLarge);
    return;
  }
  try {
    const data = JSON.parse(await file.text());
    showToast(copy[state.lang].chatgptLoaded(addMemories(conversationRecords(data, file.name))));
  } catch {
    showToast(copy[state.lang].invalidJson);
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
  showToast(copy[state.lang].summaryLoaded(added));
}

function showExportPrompt() {
  byId("personal-data-prompt").value = personalDataExportPrompt(state.lang);
  byId("prompt-output").classList.remove("hidden");
  byId("prompt-output").scrollIntoView({ behavior: "smooth", block: "center" });
}

async function copyExportPrompt() {
  const prompt = byId("personal-data-prompt").value;
  try {
    await navigator.clipboard.writeText(prompt);
    showToast(copy[state.lang].promptCopied);
  } catch {
    byId("personal-data-prompt").focus();
    byId("personal-data-prompt").select();
    showToast(copy[state.lang].promptCopyError);
  }
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

function birthValues() {
  return {
    date: byId("birth-date").value,
    time: byId("birth-time").value,
    place: byId("birth-place").value,
    timePrecision: byId("birth-time-precision").value,
    placePrecision: byId("birth-place-precision").value,
  };
}

function validateUiBirth(birth) {
  try {
    validateBirthInput(birth);
    return true;
  } catch (error) {
    if (String(error.message).startsWith("birth-date")) showToast(copy[state.lang].birthDateError);
    else if (error.message === "birth-time") showToast(copy[state.lang].birthTimeError);
    else if (error.message === "birth-place") showToast(copy[state.lang].birthPlaceError);
    else showToast(copy[state.lang].birthPrecisionError);
    byId("birth").scrollIntoView({ behavior: "smooth", block: "start" });
    return false;
  }
}

function createReading() {
  const question = byId("question").value.replace(/\s+/gu, " ").trim();
  const memories = state.memories.filter((item) => item.selected).map(displayMemory);
  const birth = birthValues();
  if (!validateUiBirth(birth)) return;
  if (Array.from(question).length < 4) {
    showToast(copy[state.lang].questionError);
    return;
  }
  if (!memories.length) {
    showToast(copy[state.lang].memoryError);
    byId("import").scrollIntoView({ behavior: "smooth" });
    return;
  }
  const themes = detectThemes(memories);
  try {
    state.reading = createDeepReading({ question, memories, themes, birth, lang: state.lang });
  } catch {
    showToast(copy[state.lang].readingError);
    return;
  }
  renderReading();
}

function renderReading() {
  const { birth, themes, readings, synthesis } = state.reading;
  byId("birth-summary").textContent = `${readingText[state.lang].profilePrefix}: ${birth.display}`;
  byId("synthesis").textContent = synthesis;
  byId("theme-row").innerHTML = (themes.length ? themes.slice(0, 5) : [{ theme: "変化", mentions: 1 }])
    .map(
      (item) =>
        `<span>${escapeHtml(readingText[state.lang].themes[item.theme] || item.theme)} · ${item.mentions}</span>`,
    )
    .join("");
  byId("reading-grid").innerHTML = readings
    .map(
      (item, index) => `
        <article class="reading-card">
          <span class="reading-number">${String(index + 1).padStart(2, "0")} / 10</span>
          <h3>${escapeHtml(item.method)}</h3>
          <p class="symbol">${escapeHtml(item.symbol)}</p>
          <section class="reading-block">
            <h4>${escapeHtml(copy[state.lang].contextLabel)}</h4>
            ${renderProse(item.context)}
            ${renderProse(item.interpretation)}
          </section>
          <section class="reading-block resonance">
            <h4>${escapeHtml(copy[state.lang].resonanceLabel)}</h4>
            ${renderProse(item.resonance)}
          </section>
          <section class="reading-block actions">
            <h4>${escapeHtml(copy[state.lang].actionLabel)}</h4>
            <ol>${item.actions.map((action) => `<li>${escapeHtml(action)}</li>`).join("")}</ol>
          </section>
          <p class="method-caveat">${escapeHtml(item.caveat)}</p>
        </article>`,
    )
    .join("");
  const result = byId("result");
  result.classList.remove("hidden");
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function downloadNote() {
  if (!state.reading) return;
  const blob = new Blob([buildReadingMarkdown(state.reading)], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `Oracle-Council-${new Date().toISOString().slice(0, 10)}.md`;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 30_000);
  showToast(copy[state.lang].noteSaved);
}

document.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.lang, { replaceQuestion: false }));
});
byId("start-demo").addEventListener("click", loadSamples);
byId("toggle-memory").addEventListener("click", () => byId("memory-input").classList.toggle("hidden"));
byId("show-export-prompt").addEventListener("click", showExportPrompt);
byId("copy-export-prompt").addEventListener("click", copyExportPrompt);
byId("add-summary").addEventListener("click", addMemorySummary);
byId("obsidian-files").addEventListener("change", (event) => readObsidianFiles(event.target.files));
byId("obsidian-folder").addEventListener("change", (event) => readObsidianFiles(event.target.files));
byId("chatgpt-file").addEventListener("change", (event) => readChatGptFile(event.target.files[0]));
byId("create-reading").addEventListener("click", createReading);
byId("download-note").addEventListener("click", downloadNote);
const localToday = new Date();
byId("birth-date").max = [
  localToday.getFullYear(),
  String(localToday.getMonth() + 1).padStart(2, "0"),
  String(localToday.getDate()).padStart(2, "0"),
].join("-");
setLanguage(state.lang, { replaceQuestion: true });
