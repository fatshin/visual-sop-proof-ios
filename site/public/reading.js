const TEXT = {
  en: {
    themes: {
      仕事: "work",
      関係: "relationships",
      健康: "health",
      お金: "money",
      学び: "learning",
      変化: "change",
    },
    precision: { exact: "exact", approximate: "approximate", unknown: "unknown" },
    fallbackTheme: "change",
    profilePrefix: "Date-based profile",
    memoryLabel: "Memory evidence",
    contextLabel: "What this lens sees",
    resonanceLabel: "Why this may land",
    actionLabel: "Three ways to act",
    caveat:
      "This is a date-based symbolic reflection, not a calculated natal chart, BaZi chart, lunar mansion, or factual prediction.",
  },
  ja: {
    themes: {
      仕事: "仕事",
      関係: "関係",
      健康: "健康",
      お金: "お金",
      学び: "学び",
      変化: "変化",
    },
    precision: { exact: "正確", approximate: "おおよそ", unknown: "不明" },
    fallbackTheme: "変化",
    profilePrefix: "生年月日ベースのプロフィール",
    memoryLabel: "記憶による根拠",
    contextLabel: "この占術が見るもの",
    resonanceLabel: "なぜ腹落ちするのか",
    actionLabel: "行動に移す3案",
    caveat:
      "これは生年月日を用いた象徴的な内省であり、完全な出生図・命式・宿・未来の事実を算出したものではありません。",
  },
};

const SIGNS = [
  [1, 20, "Aquarius", "水瓶座"],
  [2, 19, "Pisces", "魚座"],
  [3, 21, "Aries", "牡羊座"],
  [4, 20, "Taurus", "牡牛座"],
  [5, 21, "Gemini", "双子座"],
  [6, 22, "Cancer", "蟹座"],
  [7, 23, "Leo", "獅子座"],
  [8, 23, "Virgo", "乙女座"],
  [9, 23, "Libra", "天秤座"],
  [10, 24, "Scorpio", "蠍座"],
  [11, 23, "Sagittarius", "射手座"],
  [12, 22, "Capricorn", "山羊座"],
];

const TRADITIONS = [
  {
    method: { en: "I Ching", ja: "易経" },
    symbols: [
      { en: "Difficulty at the Beginning", ja: "水雷屯" },
      { en: "The Well", ja: "水風井" },
      { en: "Gradual Progress", ja: "風山漸" },
    ],
    context: {
      en: "The I Ching asks whether the conditions for movement are mature. It is less interested in a yes/no answer than in what must be stabilized before the next move.",
      ja: "易経は、動く条件が熟しているかを見ます。単純な吉凶よりも、次に進む前に何を安定させる必要があるかを問い直します。",
    },
    insight: {
      en: "Your question points forward, but your memory points to the need for a foothold. The useful reading is not “wait.” It is “name the unstable condition, then make one move that reduces it.”",
      ja: "問いは前進を求めていますが、記憶は足場を必要としています。ここでの読みは「待て」ではなく、「不安定な条件を一つ特定し、それを減らす一手を打つ」です。",
    },
    actions: {
      en: [
        "Write down the one condition that would make this decision unsafe or irreversible.",
        "Ask one experienced person what usually fails in the first 30 days.",
        "Run a 48-hour test that produces evidence without committing to the full decision.",
      ],
      ja: [
        "この決断が危険または後戻り不能になる条件を一つ書き出します。",
        "経験者一人に「最初の30日で何が失敗しやすいか」を聞きます。",
        "本決定をせずに証拠だけ得られる48時間の試行を行います。",
      ],
    },
  },
  {
    method: { en: "Four Pillars-inspired balance lens", ja: "四柱推命に着想を得た均衡の視点" },
    symbols: [
      { en: "Climate before force", ja: "調候を先に見る" },
      { en: "Support before output", ja: "出力より扶助" },
      { en: "Balance of pressure and recovery", ja: "圧力と回復の均衡" },
    ],
    context: {
      en: "A complete Four Pillars chart requires calendar conversion and specialist interpretation. This limited lens uses the birth inputs only to ask whether your environment supports the effort your goal demands.",
      ja: "完全な四柱推命には暦変換と専門的な命式解釈が必要です。この限定的な視点では、出生情報を手掛かりに、目標が求める努力を環境が支えられるかを考えます。",
    },
    insight: {
      en: "The friction in your notes may not be a character flaw. It may be a mismatch between the responsibility you want and the conditions in which you are trying to carry it.",
      ja: "記憶にある停滞は、性格の弱さではないかもしれません。望む責任の大きさと、それを担おうとしている環境条件が合っていない可能性があります。",
    },
    actions: {
      en: [
        "Separate the goal from its current environment: list what must stay and what can change.",
        "Remove one recurring drain on time, attention, or recovery for seven days.",
        "Define the minimum support you need before accepting more responsibility.",
      ],
      ja: [
        "目標と現在の環境を分け、残す条件と変えられる条件を書きます。",
        "時間・注意・回復を奪う反復要因を一つ、7日間だけ外します。",
        "責任を増やす前に必要な最低限の支援条件を定義します。",
      ],
    },
  },
  {
    method: { en: "Nine Star Ki-inspired timing lens", ja: "九星気学に着想を得た時機の視点" },
    symbols: [
      { en: "Prepare", ja: "準備期" },
      { en: "Move", ja: "行動期" },
      { en: "Review", ja: "見直し期" },
    ],
    context: {
      en: "Nine Star Ki is often used to reflect on cycles and timing. This tool does not calculate an authoritative natal star; it uses a nine-step cycle to separate preparation, movement, and review.",
      ja: "九星気学は周期と時機を考える際に使われます。このツールは正式な本命星を算出せず、9段階の周期を使って準備・行動・見直しを分けます。",
    },
    insight: {
      en: "Your uncertainty becomes easier to hold when the decision is not treated as one irreversible moment. Give each phase a different job.",
      ja: "決断を一度きりの後戻りできない瞬間として扱わなければ、不確実さは抱えやすくなります。段階ごとに役割を分けることが鍵です。",
    },
    actions: {
      en: [
        "Label today as preparation, movement, or review—and refuse tasks from the other two phases.",
        "Choose one observable result for a nine-day experiment.",
        "Put the review date on your calendar before starting the experiment.",
      ],
      ja: [
        "今日を準備・行動・見直しのいずれかに決め、他の段階の仕事を混ぜません。",
        "9日間の実験で確認する観測可能な結果を一つ決めます。",
        "実験を始める前に見直し日を予定表へ入れます。",
      ],
    },
  },
  {
    method: { en: "Sukuyō-inspired relationship lens", ja: "宿曜に着想を得た関係の視点" },
    symbols: [
      { en: "Supportive orbit", ja: "栄親のような支援関係" },
      { en: "Productive friction", ja: "安壊のような摩擦" },
      { en: "Mutual distance", ja: "友衰のような距離" },
    ],
    context: {
      en: "Traditional Sukuyō depends on a lunar-mansion calculation. This reflection does not claim that calculation; it uses the tradition’s relational question: who expands your agency, and who makes you abandon your own evidence?",
      ja: "伝統的な宿曜には宿の計算が必要です。この内省では宿を算出したとは主張せず、「誰が自分の行動力を広げ、誰の前で自分の根拠を手放すのか」という関係の問いを使います。",
    },
    insight: {
      en: "The next step may depend less on private certainty and more on choosing the right witness—someone who can challenge the plan without taking ownership away from you.",
      ja: "次の一歩に必要なのは、内心の確信よりも適切な立会人かもしれません。計画を批判できても、あなたから主体性を奪わない人です。",
    },
    actions: {
      en: [
        "Name one supporter, one useful critic, and one relationship that clouds the decision.",
        "Ask the useful critic to challenge a single assumption, not the whole dream.",
        "State one boundary that keeps final ownership of the choice with you.",
      ],
      ja: [
        "支援者、有益な批判者、判断を曇らせる関係を一人ずつ挙げます。",
        "有益な批判者には夢全体ではなく、仮定を一つだけ反証してもらいます。",
        "最終判断の主体を自分に残す境界線を一つ言葉にします。",
      ],
    },
  },
  {
    method: { en: "Western astrology-inspired identity lens", ja: "西洋占星術に着想を得た自己像の視点" },
    symbols: [],
    context: {
      en: "The birth date identifies a Sun-sign season. Birth time and place are retained as context, but this tool does not calculate houses, an ascendant, or a full natal chart.",
      ja: "生年月日から太陽星座の季節を確認します。出生時刻と出生場所も文脈として保持しますが、ハウス・アセンダント・完全な出生図は算出しません。",
    },
    insight: {
      en: "The useful tension is between the identity you want to inhabit and the evidence you currently have. Identity becomes credible when it is expressed through one visible behavior.",
      ja: "役立つ緊張は、なりたい自己像と現在持っている証拠の間にあります。自己像は、目に見える一つの行動として表したときに現実味を持ちます。",
    },
    actions: {
      en: [
        "Complete the sentence: “I am becoming someone who…” without naming a job title.",
        "Choose one behavior that would make that sentence visible this week.",
        "Ask what evidence would make you revise—not defend—that identity.",
      ],
      ja: [
        "肩書きを使わず「私は○○する人になりつつある」を完成させます。",
        "その文章を今週目に見える形にする行動を一つ選びます。",
        "その自己像を守るのではなく修正するために必要な証拠を決めます。",
      ],
    },
  },
  {
    method: { en: "Tarot", ja: "タロット" },
    symbols: [
      { en: "The Hermit", ja: "隠者" },
      { en: "Two of Wands", ja: "ワンドの2" },
      { en: "Justice", ja: "正義" },
    ],
    context: {
      en: "Tarot turns an abstract decision into a scene with tension, desire, and consequence. The card is selected deterministically from your inputs; it is a prompt, not a supernatural draw.",
      ja: "タロットは抽象的な決断を、緊張・欲求・結果のある場面へ変換します。カードは入力から決定的に選ばれる内省用の問いであり、超自然的な抽選ではありません。",
    },
    insight: {
      en: "The hidden question beneath your stated question is likely about what you fear losing if you act—and what you fear becoming if you do not.",
      ja: "表面の問いの下には、「動いたら何を失うのが怖いか」と「動かなければ何になってしまうのが怖いか」という問いがありそうです。",
    },
    actions: {
      en: [
        "Write the loss you fear if you act, then the cost you accept if you do nothing.",
        "Find one piece of evidence for and one against each fear.",
        "Choose the option whose downside can be noticed and corrected earliest.",
      ],
      ja: [
        "動いた場合に恐れる損失と、何もしない場合に受け入れる代償を書きます。",
        "それぞれの恐れを支持する証拠と反証を一つずつ探します。",
        "悪化を最も早く発見し修正できる選択肢を選びます。",
      ],
    },
  },
  {
    method: { en: "Numerology", ja: "数秘術" },
    symbols: [],
    context: {
      en: "Numerology reduces the birth-date digits to a Life Path number. The arithmetic is reproducible; the meaning is symbolic and should be tested against your actual memories.",
      ja: "数秘術では生年月日の数字をライフパス数へ還元します。計算は再現できますが、意味は象徴的であり、実際の記憶と照合して使います。",
    },
    insight: {
      en: "The number is useful only if it names a pattern already present in your history. Your selected memory is the evidence; the number is merely a compact question about that evidence.",
      ja: "数字が役立つのは、すでに自分の履歴にあるパターンを言い当てる場合だけです。選んだ記憶が根拠であり、数字はその根拠を考えるための短い問いにすぎません。",
    },
    actions: {
      en: [
        "List the last three times this same pattern helped you.",
        "List one time the same strength became an excess or avoidance.",
        "Choose one action that uses the strength while adding a clear limit.",
      ],
      ja: [
        "同じパターンが役立った過去の出来事を3つ挙げます。",
        "同じ強みが過剰または回避になった出来事を一つ挙げます。",
        "強みを使いながら明確な上限を設ける行動を一つ選びます。",
      ],
    },
  },
  {
    method: { en: "Runes", ja: "ルーン" },
    symbols: [
      { en: "Jera — harvest", ja: "Jera — 収穫" },
      { en: "Raidho — right movement", ja: "Raidho — 正しい移動" },
      { en: "Algiz — protection", ja: "Algiz — 保護" },
    ],
    context: {
      en: "Runes compress a situation into a material image—harvest, journey, protection. The image asks what has already been planted, what is moving, and what must be protected.",
      ja: "ルーンは状況を、収穫・旅・保護のような物質的な像へ圧縮します。その像から、すでに蒔いたもの、動いているもの、守るべきものを考えます。",
    },
    insight: {
      en: "You may not need another idea. You may need to notice which existing effort is already producing a weak but repeatable signal.",
      ja: "新しいアイデアが必要なのではなく、既存の努力のうち、弱くても繰り返し現れる兆候を見つける必要があるのかもしれません。",
    },
    actions: {
      en: [
        "Name the effort you have already repeated at least three times.",
        "Stop adding new inputs for seven days and measure what that effort returns.",
        "Set a harvest rule: continue, change, or stop based on one observable result.",
      ],
      ja: [
        "すでに3回以上繰り返している努力を一つ挙げます。",
        "7日間は新しい入力を増やさず、その努力から返ってくる結果を測ります。",
        "一つの観測結果に基づき、継続・変更・停止を決める収穫条件を設定します。",
      ],
    },
  },
  {
    method: { en: "Geomancy", ja: "ジオマンシー" },
    symbols: [
      { en: "Conjunctio — connection", ja: "Conjunctio — 接続" },
      { en: "Via — the way", ja: "Via — 道" },
      { en: "Fortuna Minor — earned momentum", ja: "Fortuna Minor — 得た勢い" },
    ],
    context: {
      en: "Geomancy asks how separate signs combine into a pattern. Here it is used to connect memory evidence that you may have been treating as unrelated.",
      ja: "ジオマンシーは、別々の兆候がどのように一つの型を作るかを考えます。ここでは、無関係だと思っていた記憶の証拠を接続するために使います。",
    },
    insight: {
      en: "The answer may be distributed across several small facts rather than hidden in one decisive feeling. Connection is the work.",
      ja: "答えは一つの決定的な感情に隠れているのではなく、複数の小さな事実に分散している可能性があります。事実をつなぐこと自体が作業です。",
    },
    actions: {
      en: [
        "Place two memories that seem unrelated side by side and name the shared constraint.",
        "Collect one external fact that could connect or separate them.",
        "Build a three-column table: evidence, interpretation, next test.",
      ],
      ja: [
        "無関係に見える記憶を二つ並べ、共通する制約を一つ挙げます。",
        "二つを結び付ける、または分ける外部事実を一つ集めます。",
        "証拠・解釈・次の検証という3列の表を作ります。",
      ],
    },
  },
  {
    method: { en: "Lunar-calendar-inspired cadence lens", ja: "月相・暦に着想を得た歩調の視点" },
    symbols: [
      { en: "Initiate", ja: "始める" },
      { en: "Build", ja: "育てる" },
      { en: "Release", ja: "手放す" },
    ],
    context: {
      en: "A true lunar reading requires astronomical calculation. This tool does not claim a birth Moon phase; it uses the calendar idea that starting, building, reviewing, and releasing are different kinds of work.",
      ja: "本来の月相判断には天文計算が必要です。このツールは出生時の月相を算出したとは主張せず、開始・育成・見直し・手放しを別の仕事として扱う暦の考え方を使います。",
    },
    insight: {
      en: "Your next action should match the phase of the evidence. A weak signal needs nurturing; a repeated contradiction needs release, not more optimism.",
      ja: "次の行動は証拠の段階に合わせる必要があります。弱い兆候には育成が必要ですが、繰り返す矛盾には楽観ではなく手放す判断が必要です。",
    },
    actions: {
      en: [
        "Decide whether this is a start, build, review, or release decision.",
        "Take the smallest phase-appropriate action within 24 hours.",
        "Schedule a seven-day review with an explicit continue/change/stop rule.",
      ],
      ja: [
        "これは開始・育成・見直し・手放しのどの決断かを決めます。",
        "24時間以内に、その段階に合う最小の行動を取ります。",
        "継続・変更・停止の条件を明記し、7日後の見直しを予定します。",
      ],
    },
  },
];

function validIsoDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/u.test(value)) return null;
  const [year, month, day] = value.split("-").map(Number);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  if (
    parsed.getUTCFullYear() !== year ||
    parsed.getUTCMonth() !== month - 1 ||
    parsed.getUTCDate() !== day
  ) {
    return null;
  }
  return parsed;
}

function reducedNumber(value) {
  let total = String(value)
    .replace(/\D/gu, "")
    .split("")
    .reduce((sum, digit) => sum + Number(digit), 0);
  while (total > 9 && ![11, 22, 33].includes(total)) {
    total = String(total)
      .split("")
      .reduce((sum, digit) => sum + Number(digit), 0);
  }
  return total;
}

function sunSign(date, lang) {
  const month = date.getUTCMonth() + 1;
  const day = date.getUTCDate();
  const current = SIGNS[month - 1];
  const sign = day >= current[1] ? current : SIGNS[(month + 10) % 12];
  return lang === "ja" ? sign[3] : sign[2];
}

function timeBand(value, lang) {
  const match = String(value).match(/\b([01]?\d|2[0-3]):[0-5]\d\b/u);
  if (!match) return value;
  const hour = Number(match[1]);
  if (lang === "ja") {
    if (hour < 5) return "深夜";
    if (hour < 9) return "朝";
    if (hour < 12) return "午前";
    if (hour < 17) return "午後";
    if (hour < 21) return "夕方";
    return "夜";
  }
  if (hour < 5) return "late night";
  if (hour < 9) return "morning";
  if (hour < 12) return "late morning";
  if (hour < 17) return "afternoon";
  if (hour < 21) return "evening";
  return "night";
}

export function validateBirthInput(input, today = new Date()) {
  const date = validIsoDate(String(input.date || ""));
  if (!date) throw new Error("birth-date");
  const todayUtc = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
  if (date > todayUtc) throw new Error("birth-date-future");
  if (!String(input.time || "").trim()) throw new Error("birth-time");
  if (!String(input.place || "").trim()) throw new Error("birth-place");
  if (!["exact", "approximate", "unknown"].includes(input.timePrecision)) {
    throw new Error("birth-time-precision");
  }
  if (!["exact", "approximate", "unknown"].includes(input.placePrecision)) {
    throw new Error("birth-place-precision");
  }
  return date;
}

export function buildBirthProfile(input, lang = "en", today = new Date()) {
  const date = validateBirthInput(input, today);
  const locale = lang === "ja" ? "ja-JP" : "en-US";
  const timePrecision = TEXT[lang].precision[input.timePrecision];
  const placePrecision = TEXT[lang].precision[input.placePrecision];
  return {
    date: input.date,
    time: String(input.time).trim(),
    place: String(input.place).trim(),
    timePrecision: input.timePrecision,
    placePrecision: input.placePrecision,
    weekday: new Intl.DateTimeFormat(locale, { weekday: "long", timeZone: "UTC" }).format(date),
    sunSign: sunSign(date, lang),
    lifePath: reducedNumber(input.date),
    timeBand: timeBand(input.time, lang),
    display:
      lang === "ja"
        ? `${input.date}（${new Intl.DateTimeFormat(locale, { weekday: "long", timeZone: "UTC" }).format(date)}）・` +
          `${timeBand(input.time, lang)}［${timePrecision}］・${input.place}［${placePrecision}］`
        : `${input.date} (${new Intl.DateTimeFormat(locale, { weekday: "long", timeZone: "UTC" }).format(date)}) · ` +
          `${timeBand(input.time, lang)} [${timePrecision}] · ${input.place} [${placePrecision}]`,
  };
}

function seedFor(text) {
  let result = 0;
  for (let index = 0; index < text.length; index += 1) {
    result = (result * 31 + text.charCodeAt(index)) >>> 0;
  }
  return result;
}

function excerpt(text, limit = 150) {
  const cleaned = String(text).replace(/\s+/gu, " ").trim();
  return cleaned.length > limit ? `${cleaned.slice(0, limit - 1)}…` : cleaned;
}

function themeHypothesis(theme, lang) {
  const hypotheses = {
    仕事: {
      en: "This is not only a job decision. Your memories suggest that you are deciding where you can own an outcome without losing the ability to test and revise.",
      ja: "これは単なる仕事選びではありません。記憶から見えるのは、結果への責任を持ちながら、検証と修正の余地も失わない場所を選ぼうとしているということです。",
    },
    関係: {
      en: "The recurring issue is not simply closeness or distance. It is whether the relationship lets you keep your own evidence and voice.",
      ja: "繰り返している問題は、近いか遠いかだけではありません。その関係の中で、自分の根拠と発言権を保てるかどうかです。",
    },
    健康: {
      en: "The pattern is not a lack of willpower. Your memories suggest a system whose demands exceed the recovery built into it.",
      ja: "見えているのは意志の弱さではありません。仕組みが要求する負荷に対して、回復が組み込まれていない可能性です。",
    },
    お金: {
      en: "The real question is not only how much you may gain. It is how quickly you can notice, limit, and reverse a loss.",
      ja: "本当の問いは、どれだけ得られるかだけではありません。損失をどれだけ早く発見し、限定し、引き返せるかです。",
    },
    学び: {
      en: "You may not need more information. You may need a situation in which the information must produce a visible result.",
      ja: "必要なのは追加情報ではなく、情報を目に見える結果へ変えざるを得ない状況かもしれません。",
    },
    変化: {
      en: "The pattern is not fear of change itself. It is resistance to irreversible change without enough evidence.",
      ja: "見えているのは変化そのものへの恐れではありません。十分な証拠がないまま、後戻りできない変化を選ぶことへの抵抗です。",
    },
  };
  return hypotheses[theme]?.[lang] || hypotheses.変化[lang];
}

export function createDeepReading({
  question,
  memories,
  themes,
  birth,
  lang = "en",
}) {
  if (!["en", "ja"].includes(lang)) throw new Error("language");
  const normalizedQuestion = String(question).replace(/\s+/gu, " ").trim();
  if (normalizedQuestion.length < 4) throw new Error("question");
  if (!Array.isArray(memories) || memories.length === 0) throw new Error("memories");

  const profile = buildBirthProfile(birth, lang);
  const leadingTheme = themes[0]?.theme || "変化";
  const localizedTheme = TEXT[lang].themes[leadingTheme] || TEXT[lang].fallbackTheme;
  const seed = seedFor(
    `${normalizedQuestion}|${birth.date}|${birth.time}|${birth.place}|${memories
      .map((item) => item.id)
      .join("|")}`,
  );

  const readings = TRADITIONS.map((tradition, index) => {
    const memory = memories[(seed + index * 7) % memories.length];
    let symbol;
    if (index === 4) symbol = `${profile.sunSign} Sun · ${profile.timeBand}`;
    else if (index === 6) symbol = `Life Path ${profile.lifePath}`;
    else symbol = tradition.symbols[(seed + index * 3) % tradition.symbols.length][lang];
    const resonance =
      lang === "ja"
        ? `記憶「${memory.title}」には「${excerpt(memory.text)}」とあります。これは「${localizedTheme}」が抽象的な性格診断ではなく、実際の選択履歴に現れている根拠です。`
        : `The memory “${memory.title}” says: “${excerpt(memory.text)}” This makes ${localizedTheme} more than a personality label; it is visible in your own decision history.`;
    return {
      method: tradition.method[lang],
      symbol,
      context: tradition.context[lang],
      interpretation: tradition.insight[lang],
      resonance,
      actions: tradition.actions[lang],
      memory,
      caveat: TEXT[lang].caveat,
    };
  });

  const evidenceTitles = memories.slice(0, 2).map((item) => `“${item.title}”`).join(" and ");
  const synthesis =
    lang === "ja"
      ? `${profile.sunSign}・ライフパス${profile.lifePath}という出生情報は、答えを決めるものではありません。` +
        `腹落ちの根拠は、選んだ記憶${memories.slice(0, 2).map((item) => `「${item.title}」`).join("と")}に同じ「${localizedTheme}」の型が現れていることです。` +
        `${themeHypothesis(leadingTheme, lang)} したがって、次に必要なのは確信を待つことではなく、後戻りできる小さな検証を作ることです。`
      : `Your ${profile.sunSign} Sun and Life Path ${profile.lifePath} do not decide the answer. ` +
        `The grounding evidence is that ${evidenceTitles} repeat the same ${localizedTheme} pattern. ` +
        `${themeHypothesis(leadingTheme, lang)} The next step is therefore not to wait for certainty, but to build a small, reversible test.`;

  return {
    status: "REFLECTION_READY",
    lang,
    question: normalizedQuestion,
    birth: profile,
    memoryCount: memories.length,
    themes,
    synthesis,
    readings,
  };
}

export function buildReadingMarkdown(reading) {
  const lang = reading.lang;
  const isJa = lang === "ja";
  const lines = [
    "---",
    "type: oracle-council-reading",
    `language: ${lang}`,
    `birth_date: ${reading.birth.date}`,
    `birth_time_precision: ${reading.birth.timePrecision}`,
    `birth_place_precision: ${reading.birth.placePrecision}`,
    `status: ${reading.status}`,
    `memory_count: ${reading.memoryCount}`,
    "themes:",
    ...(reading.themes.length
      ? reading.themes.map((item) => `  - ${item.theme}`)
      : ["  - 変化"]),
    "review_after_days: 7",
    "---",
    "",
    isJa ? "# Oracle Council リーディング" : "# Oracle Council Reading",
    "",
    isJa ? "## 出生情報" : "## Birth context",
    "",
    reading.birth.display,
    "",
    isJa
      ? "保存するノートには入力した出生情報が含まれます。共有前に内容を確認してください。"
      : "This saved note contains the birth details you entered. Review it before sharing.",
    "",
    isJa ? "## 今回の問い" : "## Question",
    "",
    reading.question,
    "",
    isJa ? "## 腹落ちする統合解釈" : "## Grounded synthesis",
    "",
    reading.synthesis,
    "",
    isJa ? "## 10の占術による読み" : "## Ten symbolic readings",
    "",
  ];
  for (const item of reading.readings) {
    lines.push(
      `### ${item.method} — ${item.symbol}`,
      "",
      `**${TEXT[lang].contextLabel}**`,
      "",
      item.context,
      "",
      item.interpretation,
      "",
      `**${TEXT[lang].resonanceLabel}**`,
      "",
      item.resonance,
      "",
      `**${TEXT[lang].actionLabel}**`,
      "",
      ...item.actions.map((action, index) => `${index + 1}. ${action}`),
      "",
      `_${item.caveat}_`,
      "",
    );
  }
  const memories = [
    ...new Map(reading.readings.map((item) => [item.memory.id, item.memory])).values(),
  ];
  lines.push(
    isJa ? "## 次の一歩" : "## Next step",
    "",
    isJa
      ? "一つの占術から行動案を一つ選び、24時間以内に実行して7日後に証拠を見直します。"
      : "Choose one action from one lens within 24 hours, then review the evidence in seven days.",
    "",
    isJa ? "## 使用した記憶" : "## Memories used",
    "",
    ...memories.map(
      (memory) =>
        `- ${memory.source}: ${memory.title}${memory.path ? ` — \`${memory.path}\`` : ""}`,
    ),
    "",
    isJa ? "## 注意" : "## Notice",
    "",
    isJa
      ? "これは娯楽と構造化された内省です。医療・法律・投資・安全の判断には使用できません。"
      : "This is entertainment and structured reflection. Do not use it for medical, legal, financial, or safety decisions.",
    "",
    isJa ? "## 7日後の振り返り" : "## Seven-day review",
    "",
    isJa ? "- 実際に確認した事実:" : "- Fact checked:",
    isJa ? "- 実行した案:" : "- Action taken:",
    isJa ? "- 継続・変更・停止:" : "- Continue, change, or stop:",
    "",
  );
  return lines.join("\n");
}

export const readingText = TEXT;
