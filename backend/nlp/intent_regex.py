import re
from typing import Dict, List, Tuple

Rule = Tuple[str, str]

RU_RULES: List[Rule] = [
    (r"\b(цель|накоп(ить|ления)|коплю|план(?:ирую)?|бюджет)\b", "goal_planning"),
    (r"\b(расход(ы|ов)|транзакци|категор|анализ|статистик)\b", "analytics"),
    (r"\b(кредит|вклад|депозит|карта|продукт|ипотек)\b", "product_recommendation"),
    (r"\b(грустн|тревог|поддержк|настроени|стресс)\b", "wellness"),
    (r"\b(исламск(?:ое|ий) финанс|шариат|мурабаха|сукук)\b", "general_knowledge"),
]

EN_RULES: List[Rule] = [
    (r"\b(goal|plan|budget|save|saving)\b", "goal_planning"),
    (r"\b(expense|spend|transaction|analytics|category)\b", "analytics"),
    (r"\b(credit|loan|deposit|card|product|mortgage)\b", "product_recommendation"),
    (r"\b(sad|anxious|stress|support|wellness)\b", "wellness"),
    (r"\b(islamic finance|sharia|murabaha|sukuk)\b", "general_knowledge"),
]

def fallback_predict(text: str, language: str | None = None) -> Dict:
    t = (text or "").strip()
    if not t:
        return {"intent": "general_knowledge", "confidence": 0.1, "matched_rules": []}
    lang = language or ("ru" if re.search(r"[а-яА-ЯёЁ]", t) else "en")
    rules = RU_RULES if lang == "ru" else EN_RULES
    hits = [intent for (pat, intent) in rules if re.search(pat, t, re.IGNORECASE)]
    if not hits:
        return {"intent": "general_knowledge", "confidence": 0.3, "matched_rules": []}
    from collections import Counter
    cnt = Counter(hits)
    intent, votes = cnt.most_common(1)[0]
    conf = min(0.6 + 0.1 * (votes - 1), 0.95)
    return {"intent": intent, "confidence": conf, "matched_rules": hits}
