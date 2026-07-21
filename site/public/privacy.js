const SENSITIVE_PATTERN =
  /(\bpassword\b|\bpasswd\b|api[_ -]?key|apikey|\b(?:secret|token)\b\s*[:=]|authorization\s*:|bearer\s+|パスワード|暗証番号|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{16,}|\bAKIA[0-9A-Z]{16}\b|\bgh[pousr]_[A-Za-z0-9]{20,})/iu;

export function looksSensitive(text) {
  return SENSITIVE_PATTERN.test(String(text));
}
