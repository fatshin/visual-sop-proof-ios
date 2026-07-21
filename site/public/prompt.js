const PROMPTS = {
  en: `I want to export a compact set of personal memories for a private, symbolic reflection tool called Oracle Council.

Review only information about me that you can actually access from our conversation history or saved memory. Do not browse the web, invent facts, fill gaps, or claim access to information you cannot see. If there is not enough evidence, say so instead of guessing.

Return 12–20 Markdown bullet points. Output only the bullets, with no introduction or conclusion. Use this exact structure for every line:
- [category] First-person memory in 1–2 complete sentences. Evidence or example: a concrete choice, repeated behavior, stated preference, or turning point when available. Confidence: high / medium / low.

Choose only supported categories from: values, recurring decision pattern, motivation, source of friction, work style, learning style, relationship boundary, risk and money attitude, recovery pattern, turning point, current tension, preferred way to act, contradiction or exception.

Make the memories useful for reflection:
- Write in the first person, as statements I can review and correct.
- Prefer concrete patterns and examples over generic personality labels.
- Include contradictions, exceptions, and changes over time when the evidence supports them.
- Separate confirmed statements from reasonable but uncertain interpretations using the confidence label.
- Do not perform astrology, divination, diagnosis, or prediction. Do not tell me what will happen.

Privacy exclusions are mandatory. Do not include passwords, authentication tokens, API keys, contact details, email addresses, phone numbers, usernames, account or government ID numbers, financial account details, exact home or work addresses, precise live location, medical diagnoses, legal case details, private information about other people, or long verbatim excerpts. Do not include my birth date, birth time, or birth place; I will enter those separately.`,
  ja: `Oracle Councilという非公開の象徴的な内省ツールで使うために、私自身の記憶を簡潔に書き出してください。

会話履歴または保存されたメモリーのうち、あなたが実際に参照できる私の情報だけを確認してください。Web検索、事実の創作、空白の補完、見えていない情報を参照できるという主張は禁止します。根拠が足りない場合は推測せず、情報が足りないと判断してください。

Markdownの箇条書きを12〜20件だけ出力してください。前置きと結論は不要です。すべての行を次の形式にしてください。
- [分類] 私を主語にした完全な文を1〜2文で書きます。根拠または例: 確認できる選択、繰り返す行動、明言した好み、転機のいずれかを、存在する場合だけ書きます。確度: 高 / 中 / 低。

根拠がある分類だけを次から選んでください: 価値観、繰り返す決断の型、動機、摩擦の原因、仕事の進め方、学び方、関係の境界線、リスクとお金への態度、回復の型、転機、現在の葛藤、行動の起こし方、矛盾または例外。

内省に使える記憶にするため、次を守ってください。
- 私が確認して訂正できるように、一人称の文として書きます。
- 一般的な性格ラベルより、具体的な型と実例を優先します。
- 根拠がある場合は、矛盾、例外、時間による変化も含めます。
- 確認できた事実と不確かな解釈を、確度の表示で区別します。
- 占星術、占い、診断、未来予測は行いません。

プライバシー上の除外事項は必須です。パスワード、認証トークン、APIキー、連絡先、メールアドレス、電話番号、ユーザー名、口座番号、公的な識別番号、金融口座の詳細、自宅や勤務先の正確な住所、現在地、医療上の診断、法的案件の詳細、第三者の私的情報、長い原文引用は含めません。生年月日、出生時刻、出生場所も含めないでください。出生情報は私が別に入力します。`,
};

export function personalDataExportPrompt(lang = "en") {
  return PROMPTS[lang === "ja" ? "ja" : "en"];
}
