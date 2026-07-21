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

export const TRADITIONS = [
  {
    kind: "i_ching",
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
    kind: "four_pillars",
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
    kind: "nine_star_ki",
    method: { en: "Nine Star Ki-inspired timing lens", ja: "九星気学に着想を得た時機の視点" },
    symbols: [
      { en: "Prepare", ja: "準備期" },
      { en: "Move", ja: "行動期" },
      { en: "Review", ja: "見直し期" },
    ],
    context: {
      en: "Nine Star Ki is often used to reflect on cycles and timing. This tool does not calculate an authoritative natal star; it borrows only a three-phase timing prompt to separate preparation, movement, and review.",
      ja: "九星気学は周期と時機を考える際に使われます。このツールは正式な本命星を算出せず、着想として借りた三つの段階で準備・行動・見直しを分けます。",
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
    kind: "sukuyo",
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
    kind: "astrology",
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
    kind: "tarot",
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
    kind: "numerology",
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
    kind: "runes",
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
    kind: "geomancy",
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
    kind: "lunar_cadence",
    method: { en: "Lunar-calendar-inspired cadence lens", ja: "月相・暦に着想を得た歩調の視点" },
    symbols: [
      { en: "Initiate", ja: "始める" },
      { en: "Build", ja: "育てる" },
      { en: "Review", ja: "見直す" },
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
  const todayIso = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");
  if (input.date > todayIso) throw new Error("birth-date-future");
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

function birthContextNarrative(profile, lang) {
  const timePrecision = TEXT[lang].precision[profile.timePrecision];
  const placePrecision = TEXT[lang].precision[profile.placePrecision];
  const avoidsPreciseChartClaims =
    profile.timePrecision !== "exact" || profile.placePrecision !== "exact";
  if (lang === "ja") {
    const precisionBoundary = avoidsPreciseChartClaims
      ? "時刻または場所に幅があるため、上昇星座・ハウス・地域ごとの天空配置のように正確さを必要とする判断には踏み込みません。分からない部分を埋めて断定するのではなく、『確認できている事実』と『まだ幅を残す解釈』を分けます。"
      : "時刻と場所は正確とされていますが、このツールは天文計算や専門的な命式計算を行いません。入力の細かさを理由に、未来や性格を断定しないという境界は変わりません。";
    return (
      `出生情報は結論を決める判定材料ではなく、人生の始点を一度固定して問いを眺めるための枠として使います。` +
      `生年月日からは${profile.sunSign}とライフパス${profile.lifePath}という再現可能な象徴だけを取り出します。` +
      `出生時刻は「${profile.time}」を${timePrecision}として、出生場所は「${profile.place}」を${placePrecision}として扱います。` +
      precisionBoundary
    );
  }
  const precisionBoundary = avoidsPreciseChartClaims
    ? "Because the time or place carries uncertainty, this reading does not make claims about an ascendant, houses, or a location-specific sky. It keeps known facts separate from interpretations that must remain provisional instead of filling the gaps with false precision."
    : "Although the time and place are marked exact, this tool does not perform astronomical or specialist chart calculations. More precise input does not change the boundary against treating a symbol as a factual verdict about personality or the future.";
  return (
    "Birth context is used as a frame for looking at the question from a fixed starting point, not as evidence that decides the answer. " +
    `The date contributes only two reproducible symbols: ${profile.sunSign} and Life Path ${profile.lifePath}. ` +
    `The recorded time, “${profile.time},” is treated as ${timePrecision}; the place, “${profile.place},” is treated as ${placePrecision}. ` +
    precisionBoundary
  );
}

function methodBoundaryNarrative(tradition, lang) {
  const boundaries = {
    i_ching: {
      en: "Use this hexagram as a way to inspect sequence: what must exist before movement can hold. It cannot tell you whether an external event will occur. Its value is narrower and more practical—it makes the missing first condition visible enough to test.",
      ja: "この卦は、動きが持続する前に何が必要かという順序を点検するために使います。外部の出来事が起こるかどうかは断定できません。価値があるのは、欠けている最初の条件を検証できる形で見えるようにする点です。",
    },
    four_pillars: {
      en: "This balance lens separates personal effort from the conditions carrying that effort. It does not calculate a Four Pillars chart. It asks a bounded question instead: is the present environment feeding the responsibility you want, or quietly making every step more expensive?",
      ja: "この均衡の視点は、本人の努力と、その努力を支える環境条件を分けて考えます。四柱推命の命式は算出しません。代わりに、現在の環境が望む責任を支えているか、それとも一歩ごとの負担を密かに増やしているかを問います。",
    },
    nine_star_ki: {
      en: "This timing lens is useful only if it changes the job of the current phase. Preparation gathers evidence, movement spends it, and review decides what the evidence changed. It does not identify an auspicious date; it prevents one phase from being mistaken for another.",
      ja: "この時機の視点は、現在の段階に与える役割が変わるときに役立ちます。準備は証拠を集め、行動は証拠を使い、見直しは何が変わったかを判断します。吉日を特定するのではなく、段階の取り違えを防ぎます。",
    },
    sukuyo: {
      en: "This relationship lens examines the orbit around the decision: who sharpens your evidence, who protects comfort, and who takes away ownership. It does not rank people as fortunate or harmful. It helps you assign each voice an appropriate role before asking for advice.",
      ja: "この関係の視点は、決断の周囲にいる人を、証拠を鋭くする人、安心を守る人、判断の主体性を奪う人という役割から見ます。人を吉凶で分類せず、助言を求める前に、それぞれの声をどこまで採用するかを整理します。",
    },
    astrology: {
      en: "This identity lens uses the Sun sign as a seasonal metaphor for visible intention, not as a complete personality profile. It earns its place only when the identity you name can be translated into behavior and exposed to evidence that could confirm or revise it.",
      ja: "この自己像の視点は、太陽星座を完全な性格診断ではなく、意図を外に見せるための季節的な比喩として使います。名付けた自己像を行動へ変え、確認または修正できる証拠にさらせる場合にだけ、この読みは意味を持ちます。",
    },
    tarot: {
      en: "This tarot image gives shape to a conflict that may be easier to feel than to name. It is not a supernatural draw and cannot certify the correct choice. Its job is to expose the feared loss on both sides so the more reversible downside becomes visible.",
      ja: "このタロット像は、感じていても言葉にしにくい葛藤へ形を与えます。超自然的なカード抽選ではなく、正解を保証するものでもありません。動く場合と動かない場合の恐れる損失を並べ、より修正可能な不利益を見えるようにします。",
    },
    numerology: {
      en: "The number is reproducible arithmetic, but its meaning remains a prompt. This lens is credible only where the proposed strength appears in your recorded choices and where you can also find a case in which that same strength became excessive or costly.",
      ja: "数字の計算は再現できますが、その意味はあくまで問いを作るための象徴です。示された強みが実際の選択記録に現れ、同時にその強みが過剰または負担になった例も見つけられる場合にだけ、この読みを採用します。",
    },
    runes: {
      en: "This rune lens looks for return from repeated effort rather than promising a harvest. It asks whether the signal is strong enough to continue, weak enough to change, or absent enough to stop. The decision rule must be written before another round of effort.",
      ja: "このルーンの視点は、実りを約束するのではなく、繰り返した努力から何が返ってきたかを見ます。継続できる信号か、変更すべき弱さか、停止すべき不在かを問い、次の努力を始める前に判断条件を書きます。",
    },
    geomancy: {
      en: "This geomantic figure is treated as a map of connections, not a verdict produced by the earth. It asks which two facts have been kept apart and what observation could join or separate them. The connection must survive a concrete test to matter.",
      ja: "このジオマンシーの形は、大地が与える判決ではなく、情報同士の接続図として扱います。別々に置かれていた二つの事実と、それらを結ぶか分ける観察を問い、具体的な検証に耐えた接続だけを残します。",
    },
    lunar_cadence: {
      en: "This cadence lens assigns a different task to starting, building, reviewing, and releasing. It does not calculate a lunar election or ideal date. It helps detect when you are trying to start during a review, or keep building what the evidence already asks you to release.",
      ja: "この歩調の視点は、開始・育成・見直し・手放しに異なる仕事を割り当てます。月の吉日や理想の日付は算出しません。見直すべき時に始めようとしていないか、手放す証拠があるのに育て続けていないかを見分けます。",
    },
  };
  return boundaries[tradition.kind][lang];
}

function interpretiveNarrative(tradition, symbol, question, leadingTheme, lang) {
  const hypothesis = themeHypothesis(leadingTheme, lang);
  if (lang === "ja") {
    return (
      `${tradition.insight.ja}\n\n` +
      `今回の「${symbol}」は、問い「${question}」への答えそのものではありません。` +
      `${tradition.method.ja}の言葉を借りて、いま見落としている条件を一つ浮かび上がらせるための仮説です。` +
      `${hypothesis} したがって、読むべきなのは「当たっているか」だけではなく、` +
      `この仮説を採用したときに、どの選択肢の危険・負担・可能性が以前より具体的に見えるかです。` +
      `違和感が残るなら、その違和感も反証として記録し、次の検証で読みを更新します。`
    );
  }
  return (
    `${tradition.insight.en}\n\n` +
    `“${symbol}” is not the answer to “${question}.” It is a working hypothesis, expressed through the language of ${tradition.method.en}, about a condition that may currently be easy to overlook. ` +
    `${hypothesis} The useful question is therefore not only whether the description feels accurate. Ask which risk, burden, or possibility becomes more specific when you temporarily adopt this lens. ` +
    "If part of the reading does not fit, preserve that friction as counter-evidence. The reading becomes more useful when reality is allowed to revise it."
  );
}

function evidenceNarrative(memory, comparisonMemory, localizedTheme, lang) {
  const sameMemory = memory.id === comparisonMemory.id;
  if (lang === "ja") {
    const comparison = sameMemory
      ? `参照できる記憶が一件のため、この解釈はまだ一つの出来事に依存しています。別の時期の記憶を追加し、同じ型が繰り返しているかを確かめる余地があります。`
      : `もう一つの記憶「${comparisonMemory.title}」には「${excerpt(comparisonMemory.text)}」とあります。二つを並べると、一度きりの気分ではなく、異なる場面で「${localizedTheme}」への向き合い方が繰り返されているかを確認できます。`;
    return (
      `記憶「${memory.title}」には「${excerpt(memory.text)}」とあります。` +
      `象徴の説明を先に信じるのではなく、この具体的な言葉を出発点にします。ここには、当時の自分が何を望み、何を危険と感じ、どこまでなら試せると考えたかが残っています。\n\n` +
      comparison +
      `\n\n腹落ちの根拠は、占術名の権威ではありません。自分が実際に残した言葉を二つ以上の場面で照合し、同じ選択の癖と例外の両方が見えることです。` +
      `この読みは「あなたはこういう人だ」と固定するためではなく、次の一手を小さくし、結果から修正できるようにするために使います。`
    );
  }
  const comparison = sameMemory
    ? "Only one memory is available, so this interpretation still depends on a single episode. Add a memory from another period before treating the pattern as repeated."
    : `A second memory, “${comparisonMemory.title},” says: “${excerpt(comparisonMemory.text)}” Placing the two side by side tests whether your way of handling ${localizedTheme} appears across different situations rather than only in one passing mood.`;
  return (
    `The memory “${memory.title}” says: “${excerpt(memory.text)}” The reading starts with these concrete words instead of asking you to believe the symbol first. They preserve what you wanted at the time, what you experienced as dangerous, and what kind of experiment still felt possible.\n\n` +
    comparison +
    "\n\nThe reason this may land is not the authority of a divination system. It is the ability to compare words you actually left behind, find both a repeated decision pattern and its exceptions, and turn that evidence into a smaller next move. " +
    "Use the lens to make the next test more observable and reversible, not to freeze yourself into a personality label."
  );
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
  if (Array.from(normalizedQuestion).length < 4) throw new Error("question");
  if (!Array.isArray(memories) || memories.length === 0) throw new Error("memories");
  if (!Array.isArray(themes)) throw new Error("themes");

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
    const comparisonMemory = memories[(seed + index * 7 + 1) % memories.length];
    let symbol;
    if (tradition.kind === "astrology") {
      symbol =
        lang === "ja"
          ? `${profile.sunSign}の太陽星座・${profile.timeBand}`
          : `${profile.sunSign} Sun · ${profile.timeBand}`;
    } else if (tradition.kind === "numerology") {
      symbol = lang === "ja" ? `ライフパス ${profile.lifePath}` : `Life Path ${profile.lifePath}`;
    }
    else symbol = tradition.symbols[(seed + index) % tradition.symbols.length][lang];
    const context = `${tradition.context[lang]}\n\n${methodBoundaryNarrative(tradition, lang)}`;
    const interpretation = interpretiveNarrative(
      tradition,
      symbol,
      normalizedQuestion,
      leadingTheme,
      lang,
    );
    const resonance = evidenceNarrative(memory, comparisonMemory, localizedTheme, lang);
    return {
      method: tradition.method[lang],
      symbol,
      context,
      interpretation,
      resonance,
      actions: tradition.actions[lang],
      memory,
      caveat: TEXT[lang].caveat,
    };
  });

  const evidenceTitles = memories.slice(0, 2).map((item) => `“${item.title}”`).join(" and ");
  const evidenceVerb = memories.length === 1 ? "repeats" : "repeat";
  const synthesis =
    lang === "ja"
      ? `${profile.sunSign}・ライフパス${profile.lifePath}という出生情報は、答えを決めるものではありません。` +
        `腹落ちの根拠は、選んだ記憶${memories.slice(0, 2).map((item) => `「${item.title}」`).join("と")}に同じ「${localizedTheme}」の型が現れていることです。` +
        `${themeHypothesis(leadingTheme, lang)} したがって、次に必要なのは確信を待つことではなく、後戻りできる小さな検証を作ることです。`
      : `Your ${profile.sunSign} Sun and Life Path ${profile.lifePath} do not decide the answer. ` +
        `The grounding evidence is that ${evidenceTitles} ${evidenceVerb} the same ${localizedTheme} pattern. ` +
        `${themeHypothesis(leadingTheme, lang)} The next step is therefore not to wait for certainty, but to build a small, reversible test.`;
  const groundedSynthesis = `${synthesis}\n\n${birthContextNarrative(profile, lang)}`;

  return {
    status: "REFLECTION_READY",
    lang,
    question: normalizedQuestion,
    birth: profile,
    memoryCount: memories.length,
    sourceCount: new Set(memories.map((item) => item.source)).size,
    themes,
    synthesis: groundedSynthesis,
    readings,
    nextStep:
      lang === "ja"
        ? "一つの占術から行動案を一つ選び、24時間以内に実行して7日後に証拠を見直します。"
        : "Choose one action from one lens within 24 hours, then review the evidence in seven days.",
    disclaimer:
      lang === "ja"
        ? "これは娯楽と構造化された内省です。医療・法律・投資・安全の判断には使用できません。"
        : "This is entertainment and structured reflection. Do not use it for medical, legal, financial, or safety decisions.",
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
      ? reading.themes.map((item) => `  - ${TEXT[lang].themes[item.theme] || item.theme}`)
      : [`  - ${TEXT[lang].fallbackTheme}`]),
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
    reading.nextStep,
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
    reading.disclaimer,
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
