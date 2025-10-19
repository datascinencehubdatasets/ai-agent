from __future__ import annotations
from typing import Any, Dict, List, Optional
from dateutil import parser as dateparser
import re, math
from backend.memory.state import state

def _to_float_or_none(value):
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def _to_float_safe(value):
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

# Набор слотов и их "важность"
REQUIRED = ["goal_name", "target_amount", "currency", "deadline_date"]
OPTIONAL  = ["current_savings", "monthly_contribution", "expected_apr", "notes"]

DEFAULTS = {
    "current_savings": 0.0,
    "expected_apr": 0.0,          # годовая ожидаемая доходность, если не знаем — считаем без процента
    "monthly_contribution": None, # либо задаст пользователь, либо посчитаем
    "notes": ""
}

CURRENCY_ALIASES = {
    "₸": "KZT", "KZT": "KZT", "тг": "KZT", "тенге": "KZT",
    "$": "USD", "USD": "USD",
    "RUB": "RUB", "₽": "RUB", "руб": "RUB",
    "KGS": "KGS", "сом": "KGS"
}

def _norm_currency(s: Optional[str]) -> Optional[str]:
    if not s: return None
    s = s.strip().upper()
    return CURRENCY_ALIASES.get(s, s)
def _to_percent_decimal(x: Any) -> Optional[float]:
    """ '10%', '10', 0.1 -> 0.10 """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        v = float(x)
        return v/100.0 if v > 1.01 else v
    s = str(x).strip().replace(" ", "").replace(",", ".")
    s = s.rstrip("%")
    try:
        v = float(re.sub(r"[^0-9.]", "", s))
        return v/100.0 if v > 1.01 else v
    except Exception:
        return None
def _to_float_safe(x: Any) -> Optional[float]:
    if x is None: return None
    if isinstance(x, (int, float)): return float(x)
    s = str(x).lower().replace(" ", "")
    # 1.5м, 1.5млн, 200k, 200к, 200.000, 200,000
    mult = 1.0
    if "млн" in s or s.endswith("m") or s.endswith("м"):
        mult = 1_000_000.0
        s = re.sub(r"(млн|m|м)$", "", s)
    elif "тыс" in s or s.endswith("k") or s.endswith("к"):
        mult = 1_000.0
        s = re.sub(r"(тыс|k|к)$", "", s)
    s = s.replace(",", ".")
    try:
        return float(re.sub(r"[^0-9.]", "", s)) * mult
    except Exception:
        return None

def _parse_date_iso(s: Optional[str]) -> Optional[str]:
    if not s: return None
    try:
        dt = dateparser.parse(str(s), dayfirst=True, fuzzy=True)
        return dt.date().isoformat()
    except Exception:
        return None

def _months_between(today_iso: str, deadline_iso: str) -> int:
    from datetime import date
    t = date.fromisoformat(today_iso)
    d = date.fromisoformat(deadline_iso)
    months = (d.year - t.year) * 12 + (d.month - t.month)
    # округлим вверх, если есть остаток дней
    if d.day > t.day: months += 1
    return max(1, months)

def feasibility(slots: Dict[str, Any], today_iso: str) -> Dict[str, Any]:
    """Module-level feasibility function that delegates to GoalSlots.feasibility"""
    return GoalSlots.feasibility(slots, today_iso)

def _solve_monthly_contrib(FV: float, n_months: int, r_annual: float, current: float) -> float:
    """
    Находим ежемесячный платёж P, чтобы достичь FV за n месяцев.
    r_annual — ожидаемая годовая доходность (например, 0.1 = 10%).
    Формула: FV = current*(1+i)^n + P * [((1+i)^n - 1) / i], где i — месячная ставка.
    Если ставка 0 — просто (FV - current)/n.
    """
    current = max(0.0, current)
    if r_annual and r_annual > 0:
        i = r_annual / 12.0
        a = (1 + i) ** n_months
        denom = (a - 1.0) / i if i != 0 else float(n_months)
        need = max(0.0, FV - current * a)
        return need / denom if denom > 0 else need
    else:
        return max(0.0, (FV - current) / float(n_months))

class GoalSlots:
    """
    Слой управления слотами целей. Хранит/чистит/обновляет в SessionState.
    """
    KEY = "goal"

    @staticmethod
    def get(sid: str) -> Dict[str, Any]:
        st = state.get(sid)
        g = st.get(GoalSlots.KEY, {})
        # приведём к единому виду и применим дефолты
        out = {**DEFAULTS, **g}
        if out.get("currency"):
            out["currency"] = _norm_currency(out["currency"])
        return out
    
    @staticmethod
    def update(sid: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        if not patch:
            return GoalSlots.get(sid)

        up: Dict[str, Any] = {}

        if "goal_name" in patch:
            v = patch["goal_name"]
            if v is not None:
                up["goal_name"] = str(v).strip()

        if "target_amount" in patch:
            v = _to_float_safe(patch["target_amount"])
            if v is not None:
                up["target_amount"] = v

        if "currency" in patch:
            v = _norm_currency(patch["currency"])
            if v:
                up["currency"] = v

        if "deadline_date" in patch:
            v = _parse_date_iso(patch["deadline_date"])
            if v:
                up["deadline_date"] = v

        if "current_savings" in patch:
            v = _to_float_safe(patch["current_savings"])
            if v is not None:
                up["current_savings"] = v

        if "monthly_contribution" in patch:
            v = _to_float_safe(patch["monthly_contribution"])
            if v is not None:
                up["monthly_contribution"] = v

        if "expected_apr" in patch:
            v = _to_percent_decimal(patch["expected_apr"])
            if v is not None:
                up["expected_apr"] = max(0.0, min(v, 1.0))

        if "notes" in patch:
            v = patch["notes"]
            if v is not None:
                up["notes"] = str(v).strip()

        st = state.get(sid)
        cur = st.get(GoalSlots.KEY, {})
        cur.update(up)
        st[GoalSlots.KEY] = cur
        state.update(sid, st)
        return GoalSlots.get(sid)

    @staticmethod
    def feasibility(slots: Dict[str, Any], today_iso: str) -> Dict[str, Any]:
        miss = GoalSlots.missing(slots)
        if miss:
            return {"have_all_required": False, "months": None, "required_monthly": None, "meets_target": None, "reason": f"missing: {','.join(miss)}"}
        n = _months_between(today_iso, slots["deadline_date"])
        apr = float(slots.get("expected_apr") or 0.0)
        current = float(slots.get("current_savings") or 0.0)
        target = float(slots["target_amount"])
        req = _solve_monthly_contrib(FV=target, n_months=n, r_annual=apr, current=current)

        user_monthly = slots.get("monthly_contribution")
        meets = None
        if user_monthly is not None:
            try:
                meets = float(user_monthly) + 1e-9 >= req  # +эпсилон
            except Exception:
                meets = None
        return {
            "have_all_required": True,
            "months": n,
            "required_monthly": float(round(req, 2)),
            "meets_target": meets,
            "reason": None
        }

    @staticmethod
    def clear(sid: str):
        st = state.get(sid)
        st.pop(GoalSlots.KEY, None)
        state.update(sid, st)

    @staticmethod
    def missing(slots: Dict[str, Any]) -> List[str]:
        miss = [k for k in REQUIRED if not slots.get(k)]
        return miss

    @staticmethod
    def plan(sid: str, today_iso: str) -> Dict[str, Any]:
        s = GoalSlots.get(sid)
        miss = GoalSlots.missing(s)
        if miss:
            return {"ready": False, "missing": miss, "slots": s}

        n = _months_between(today_iso, s["deadline_date"])
        apr = float(s.get("expected_apr") or 0.0)
        monthly = s.get("monthly_contribution")
        if monthly is None:
            monthly = _solve_monthly_contrib(
                FV=float(s["target_amount"]),
                n_months=n,
                r_annual=apr,
                current=float(s.get("current_savings") or 0.0)
            )
        # Итоговая оценка прогноза
        return {
            "ready": True,
            "months": n,
            "required_monthly": round(monthly, 2),
            "currency": s.get("currency") or "KZT",
            "slots": s
        }
    
