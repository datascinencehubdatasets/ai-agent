from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import date
from openai import OpenAI
import httpx, json

from backend.utils.settings import settings
from backend.rag.retriever import Retriever
from backend.agents.goal_slots import GoalSlots, feasibility
from backend.memory.state import state

EXTRACT_SYSTEM = """You extract goal-setting slots from user messages for a financial assistant.
Return STRICT JSON with the following fields (null if not present):
{
  "goal_name": string | null,
  "target_amount": number | null,
  "currency": string | null,
  "deadline_date": string | null,     // ISO YYYY-MM-DD (parse 'к июлю 2026', 'через 12 мес')
  "current_savings": number | null,
  "monthly_contribution": number | null,
  "expected_apr": number | null,      // decimal (0.10 means 10% APR)
  "notes": string | null
}
Do not add extra keys or text. If uncertain – leave null."""

# Приоритетные вопросы для обязательных слотов
CLARIFY_RU = {
  "goal_name": "Как называется цель (например, отпуск, ремонт, подушка безопасности)?",
  "target_amount": "Какая целевая сумма? (укажите число и валюту, например: 1 500 000 ₸)",
  "currency": "В какой валюте откладываем? (например: KZT, USD)",
  "deadline_date": "К какому сроку хотите достичь цели? (дата или фраза вроде «к июлю 2026»)"
}

RAG_Q_SYSTEM = """You are a helpful assistant for clarifying questions in savings goal setup.
Use ONLY the provided CONTEXT to propose 1-3 SHORT clarifying questions that help choose suitable bank products or approaches.
Do NOT provide solutions or recommendations; ask questions only (concise, practical)."""

PLAN_SYSTEM = """You are a savings planning assistant. Use ONLY provided slots and optional CONTEXT.
If 'confirm' is not given, do not produce a plan yet. Ask for confirmation if needed.
Keep answers concise and practical."""

class GoalAgent:
    name = "goal_planning"

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            max_retries=2,
            http_client=httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS),
        )
        self.model = settings.INTENT_MODEL
        self.retriever = Retriever()


    def _extract_slots(self, user_text: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": EXTRACT_SYSTEM},
            {"role": "user", "content": user_text}
        ]
        resp = self.client.chat.completions.create(
            model=self.model, temperature=0,
            response_format={"type":"json_object"},
            messages=messages
        )
        raw = resp.choices[0].message.content
        data = json.loads(raw)

        data = {k: (None if (v in ("", "null", "None")) else v) for k, v in data.items()}
        return data

    def _kb_questions(self, topic_hint: str) -> List[str]:
        """
        Тянем 1-3 коротких уточняющих вопроса на основе KB.
        Не выдаём советы — только вопросы, помогающие сузить выбор продукта/подхода.
        """
        hits = self.retriever.retrieve(topic_hint)
        ctx = self.retriever.format_context(hits, max_chars=1400)
        if not ctx:
            return []

        prompt = [
            {"role":"system","content": RAG_Q_SYSTEM},
            {"role":"system","content": f"CONTEXT:\n{ctx}"},
            {"role":"user","content":"Сформулируй 1-3 уточняющих вопроса (коротко, по делу), без советов."}
        ]
        try:
            r = self.client.chat.completions.create(model=self.model, temperature=0.2, messages=prompt)
            text = (r.choices[0].message.content or "").strip()

            qs = [ln.strip("-• ").strip() for ln in text.split("\n") if ln.strip()]

            qs = qs[:3]

            qs = [q for q in qs if not q.lower().startswith(("откройте","начните","настройте","рекомендую","возьмите","рассмотрите"))]
            return qs[:3]
        except Exception:
            return []

    def _format_slots_summary(self, s: Dict[str,Any], months: Optional[int], required_monthly: Optional[float]) -> str:
        curr = s.get("currency") or "KZT"
        lines = []
        if s.get("goal_name"): lines.append(f"Цель: {s['goal_name']}")
        if s.get("target_amount") is not None: lines.append(f"Целевая сумма: {s['target_amount']:,.0f} {curr}".replace(",", " "))
        if s.get("current_savings") is not None: lines.append(f"Текущие накопления: {s['current_savings']:,.0f} {curr}".replace(",", " "))
        if s.get("monthly_contribution") is not None: lines.append(f"Ваш ежемесячный взнос: {s['monthly_contribution']:,.0f} {curr}".replace(",", " "))
        if s.get("expected_apr") is not None: lines.append(f"Ожидаемая доходность: {float(s['expected_apr'])*100:.1f}% годовых")
        if s.get("deadline_date"): lines.append(f"Срок: до {s['deadline_date']}" + (f" (~{months} мес)" if months else ""))
        if required_monthly is not None: lines.append(f"Требуемый ежемесячный взнос: ≈ {required_monthly:,.0f} {curr}".replace(",", " "))
        return "\n".join(lines)


    def run(self, query: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        sid = (context or {}).get("session_id", "default")
        st = state.get(sid)
        goal = st.get("goal", {})
        phase = goal.get("phase") or "collect"

        extracted = self._extract_slots(query)
        slots = GoalSlots.update(sid, extracted)

        today_iso = date.today().isoformat()
        feas = feasibility(slots, today_iso)
        miss = GoalSlots.missing(slots)


        if phase == "collect":
            if miss:
                questions: List[str] = [CLARIFY_RU[m] for m in miss if m in CLARIFY_RU]

                topic_hint = f"накопление {slots.get('goal_name','')} {slots.get('currency') or ''}"
                kb_qs = self._kb_questions(topic_hint)
                questions += kb_qs

                goal.update({"phase":"collect","last_questions":questions})
                st["goal"] = goal
                state.update(sid, st)
                return {
                    "answer": "Чтобы продолжить, уточните, пожалуйста:\n- " + "\n- ".join(questions),
                    "slots": slots,
                    "phase": "collect",
                    "missing": miss
                }


            goal.update({"phase":"confirm"})
            st["goal"] = goal
            state.update(sid, st)

            reqm = feas.get("required_monthly")
            summary = self._format_slots_summary(slots, feas.get("months"), reqm)
            q = "Подтверждаете расчёт по этим параметрам?" if slots.get("monthly_contribution") is not None else "Хотите рассчитать план на основе этих параметров?"
            return {
                "answer": f"Промежуточная сводка:\n{summary}\n\n{q} (да/нет)",
                "slots": slots,
                "phase": "confirm",
                "missing": []
            }


        if phase == "confirm":

            txt = query.lower()
            if any(w in txt for w in ["да", "ок", "подтверждаю", "согласен", "поехали", "рассчитать"]):
                goal["user_accepts_required_monthly"] = True
            elif any(w in txt for w in ["нет", "не", "стоп", "отмена"]):
                goal["user_accepts_required_monthly"] = False

            st["goal"] = goal; state.update(sid, st)

            reqm = feas.get("required_monthly")
            meets = feas.get("meets_target")
            summary = self._format_slots_summary(slots, feas.get("months"), reqm)

            if slots.get("monthly_contribution") is not None and meets is not None:
                if meets is False:

                    qopts = [
                        f"Ваш текущий взнос ниже требуемого (≈ {reqm:,.0f}). Можем увеличить взнос, продлить срок или снизить целевую сумму. Какой вариант предпочитаете?".replace(",", " "),
                    ]
                
                    kb_qs = self._kb_questions(f"накопления увеличение взноса сроки продукты {slots.get('currency') or ''}")
                    qopts += kb_qs
                    return {
                        "answer": f"Промежуточная сводка:\n{summary}\n\n" + "\n".join(qopts),
                        "slots": slots,
                        "phase": "confirm",
                        "feasibility": feas
                    }

            if goal.get("user_accepts_required_monthly") is True:
                goal["phase"] = "plan"; st["goal"] = goal; state.update(sid, st)
            else:

                ask = "Подтверждаете расчёт плана?" if slots.get("monthly_contribution") is not None else "Рассчитать план по этим параметрам?"
                return {
                    "answer": f"Промежуточная сводка:\n{summary}\n\n{ask} (да/нет)",
                    "slots": slots,
                    "phase": "confirm",
                    "feasibility": feas
                }

        if phase in ("plan",) or state.get(sid).get("goal", {}).get("phase") == "plan":
            reqm = feas.get("required_monthly")
            months = feas.get("months")
            curr = slots.get("currency") or "KZT"

            kb_qs = self._kb_questions(f"накопления шаги контроль прогресс автоматизация перевода {curr}")
            kb_tail = ("\nДоп. вопросы для уточнения:\n- " + "\n- ".join(kb_qs)) if kb_qs else ""

            plan_text = (
                f"План до цели (~{months} мес):\n"
                f"1) Откладывать ≈ {reqm:,.0f} {curr} ежемесячно (или подтвердите свой взнос).\n"
                f"2) Зафиксировать дату контроля 1 раз в месяц.\n"
                f"3) При отклонении >10% — пересмотреть сумму/срок.\n"
                f"4) Автоматизировать перевод после зарплаты.\n"
            ).replace(",", " ")

            return {
                "answer": plan_text + kb_tail,
                "slots": slots,
                "phase": "plan",
                "feasibility": feas
            }

        return {
            "answer": "Давайте уточним параметры цели. Сформулируйте: цель, сумму, валюту и срок.",
            "slots": slots,
            "phase": "collect",
            "missing": GoalSlots.missing(slots)
        }
