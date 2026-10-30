"""GuardianAI screening endpoints (no API keys required)."""
from functools import lru_cache
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from api.guardian.engine import FIELDS, HIGH_RISK_CATEGORIES, get_screener

guardian_router = APIRouter(prefix="/screen", tags=["guardian screening"])


class TransactionIn(BaseModel):
    amount: float = Field(..., gt=0, examples=[2450.0])
    merchant_category: str = Field(..., examples=["cryptocurrency"])
    hour: int = Field(..., ge=0, le=23, examples=[2])
    day_of_week: int = Field(..., ge=0, le=6, examples=[5])
    user_country: str = Field(..., examples=["US"])
    merchant_country: str = Field(..., examples=["RO"])
    payment_method: str = Field(..., examples=["credit_card"])
    card_present: bool = Field(..., examples=[False])


class ScreenOut(BaseModel):
    transaction_id: str
    is_fraud: bool
    risk_score: float
    confidence: float
    recommendation: Literal["approve", "review", "escalate"]
    explanation: str
    agent_outputs: list[dict]
    processing_time_ms: float
    timestamp: str


@guardian_router.post("", response_model=ScreenOut)
def screen(tx: TransactionIn) -> dict:
    """Score one transaction with the four GuardianAI agents."""
    return get_screener().screen(tx.model_dump())


@guardian_router.get("/options")
def options() -> dict:
    df = get_screener().df
    return {c: sorted(df[c].astype(str).unique().tolist()) for c in
            ("merchant_category", "user_country", "merchant_country", "payment_method")} | {
        "high_risk_categories": sorted(HIGH_RISK_CATEGORIES)}


@lru_cache
def _metrics(n: int) -> dict:
    return get_screener().evaluate(n)


@guardian_router.get("/metrics")
def metrics(samples: int = Query(1000, ge=50, le=5000)) -> dict:
    """Accuracy / precision / recall on the bundled synthetic dataset (in-sample; neighbours exclude the row itself)."""
    s = get_screener()
    return _metrics(samples) | {"dataset_size": len(s.df), "fraud_rate": round(float(s.df.is_fraud.mean()), 4)}


@guardian_router.get("/samples")
def samples(fraud: bool | None = None, limit: int = Query(6, le=50)) -> list[dict]:
    df = get_screener().df
    if fraud is not None:
        df = df[df.is_fraud == fraud]
    return df.sample(min(limit, len(df)), random_state=7)[["transaction_id", *FIELDS, "is_fraud"]].to_dict("records")


@guardian_router.get("/similar/{transaction_id}")
def similar(transaction_id: str, limit: int = Query(5, le=25)) -> list[dict]:
    s = get_screener()
    row = s.df[s.df.transaction_id == transaction_id]
    if row.empty:
        raise HTTPException(404, "transaction not found in the reference dataset")
    return s.behavioral.similar(row.iloc[0].to_dict(), k=limit)


@guardian_router.post("/similar")
def similar_to(tx: TransactionIn, limit: int = Query(5, le=25)) -> list[dict]:
    return get_screener().behavioral.similar(tx.model_dump(), k=limit)
