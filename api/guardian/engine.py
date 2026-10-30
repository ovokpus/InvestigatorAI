"""GuardianAI real-time transaction screening, folded into InvestigatorAI.

Ported from GuardianAI's guardian-ai.ipynb (github.com/ovokpus/GuardianAI). Four agents:

- TransactionAgent: IsolationForest anomaly score on amount/hour/day, plus rule-based risk factors
- BehavioralAgent: fraud rate among the most similar historical transactions, plus time-of-day risk
- PatternAgent: known fraud templates (card testing, high value, night-time, cross-border, risky category)
- DecisionAgent: weighted score (0.3 / 0.4 / 0.3) against a threshold, with a plain-English explanation

Difference from the notebook: similar-transaction lookup uses scikit-learn NearestNeighbors over
one-hot + scaled features instead of SentenceTransformer embeddings in in-memory Qdrant. It gives
the same "fraud rate among the 10 nearest cases" signal, needs no model download or API key, and
runs in about a millisecond.
"""
from __future__ import annotations

import os
import time
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = Path(os.getenv("GUARDIAN_DATA_PATH", Path(__file__).resolve().parents[2] / "data/guardian/fraud_data.csv"))
FRAUD_THRESHOLD = float(os.getenv("GUARDIAN_FRAUD_THRESHOLD", "0.3"))
WEIGHTS = {"transaction": 0.3, "behavioral": 0.4, "pattern": 0.3}
HIGH_RISK_CATEGORIES = {"online_gaming", "cryptocurrency", "adult_entertainment"}
NUMERIC = ["amount", "hour", "day_of_week"]
CATEGORICAL = ["merchant_category", "user_country", "merchant_country", "payment_method", "card_present"]
FIELDS = NUMERIC + CATEGORICAL


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ("card_present", "is_fraud"):
        df[col] = df[col].astype(str).str.lower().eq("true")
    return df


class TransactionAgent:
    def __init__(self, df: pd.DataFrame):
        self.scaler = StandardScaler().fit(df[NUMERIC])
        self.forest = IsolationForest(contamination=0.1, random_state=42).fit(self.scaler.transform(df[NUMERIC]))

    def analyze(self, t: dict) -> dict:
        x = self.scaler.transform(pd.DataFrame([[t[c] for c in NUMERIC]], columns=NUMERIC))
        factors, score = [], 0.0
        if t["amount"] > 1000:
            factors.append("High amount transaction"); score += 0.3
        if t["merchant_category"] in ("online_gaming", "cryptocurrency"):
            factors.append("High-risk merchant category"); score += 0.4
        if t["user_country"] != t["merchant_country"]:
            factors.append("Cross-border transaction"); score += 0.2
        if not t["card_present"]:
            factors.append("Card not present"); score += 0.3
        return {"agent": "TransactionAgent", "anomaly_score": float(self.forest.decision_function(x)[0]),
                "is_anomaly": bool(self.forest.predict(x)[0] == -1), "risk_score": min(score, 1.0),
                "risk_factors": factors, "confidence": 0.8}


class BehavioralAgent:
    def __init__(self, df: pd.DataFrame, k: int = 10):
        self.df, self.k = df.reset_index(drop=True), k
        self.encoder = ColumnTransformer([
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]).fit(self.df[FIELDS])
        self.index = NearestNeighbors(n_neighbors=k + 1).fit(self.encoder.transform(self.df[FIELDS]))

    def similar(self, t: dict, k: int | None = None) -> list[dict]:
        k = k or self.k
        dist, idx = self.index.kneighbors(self.encoder.transform(pd.DataFrame([t])[FIELDS]), n_neighbors=k + 1)
        rows = [(d, i) for d, i in zip(dist[0], idx[0]) if self.df.at[i, "transaction_id"] != t.get("transaction_id")][:k]
        cols = ["transaction_id", *FIELDS, "is_fraud"]
        return [{**{c: _py(self.df.at[i, c]) for c in cols}, "distance": round(float(d), 4)} for d, i in rows]

    def analyze(self, t: dict) -> dict:
        sims = self.similar(t)
        p = sum(s["is_fraud"] for s in sims) / len(sims) if sims else 0.0
        risks, score = [], 0.0
        if p > 0.5:
            risks.append("High fraud rate in similar patterns"); score += 0.5
        if p > 0.7:
            risks.append("Very high fraud likelihood"); score += 0.3
        if t["hour"] < 6 or t["hour"] > 22:
            risks.append("Unusual transaction time"); score += 0.2
        return {"agent": "BehavioralAgent", "fraud_probability": p, "similar_patterns_count": len(sims),
                "behavioral_score": min(score, 1.0), "behavioral_risks": risks, "confidence": 0.85}


PATTERNS = {
    "card_testing": ("Small amounts to test card validity", lambda t: t["amount"] < 5.0 and not t["card_present"]),
    "high_value_fraud": ("Unusually high transaction amounts", lambda t: t["amount"] > 5000),
    "velocity_fraud": ("Night-time activity window (22:00-06:00)", lambda t: t["hour"] >= 22 or t["hour"] <= 6),
    "geographic_fraud": ("Transactions from unusual locations", lambda t: t["user_country"] != t["merchant_country"]),
    "category_fraud": ("High-risk merchant categories", lambda t: t["merchant_category"] in HIGH_RISK_CATEGORIES),
}


class PatternAgent:
    def analyze(self, t: dict) -> dict:
        matched = [{"name": n, "description": d} for n, (d, rule) in PATTERNS.items() if rule(t)]
        return {"agent": "PatternAgent", "matched_patterns": matched, "pattern_score": min(0.2 * len(matched), 1.0),
                "patterns_count": len(matched), "confidence": 0.9}


class DecisionAgent:
    def __init__(self, threshold: float = FRAUD_THRESHOLD):
        self.threshold = threshold

    def decide(self, t: dict, tx: dict, beh: dict, pat: dict) -> dict:
        score = (tx["risk_score"] * WEIGHTS["transaction"] + beh["behavioral_score"] * WEIGHTS["behavioral"]
                 + pat["pattern_score"] * WEIGHTS["pattern"])
        is_fraud = score > self.threshold
        lines = [f"Transaction ${t['amount']:,.2f} at {t['merchant_category']} classified as "
                 f"{'FRAUD' if is_fraud else 'LEGITIMATE'} (risk score {score:.2f}, threshold {self.threshold:.2f})."]
        lines.append(f"Transaction analysis: risk {tx['risk_score']:.2f}" + (f" ({', '.join(tx['risk_factors'])})" if tx["risk_factors"] else ""))
        lines.append(f"Behavioral analysis: {beh['fraud_probability']:.0%} of the {beh['similar_patterns_count']} most similar past transactions were fraud"
                     + (f" ({', '.join(beh['behavioral_risks'])})" if beh["behavioral_risks"] else ""))
        lines.append(f"Pattern matching: {pat['patterns_count']} pattern(s)" + (f": {', '.join(p['name'] for p in pat['matched_patterns'])}" if pat["matched_patterns"] else ""))
        return {"is_fraud": bool(is_fraud), "risk_score": round(float(score), 4),
                "confidence": round((tx["confidence"] + beh["confidence"] + pat["confidence"]) / 3, 3),
                "explanation": "\n".join(lines)}


class GuardianScreener:
    def __init__(self, df: pd.DataFrame | None = None, threshold: float = FRAUD_THRESHOLD):
        self.df = load_data() if df is None else df
        self.transaction = TransactionAgent(self.df)
        self.behavioral = BehavioralAgent(self.df)
        self.pattern = PatternAgent()
        self.decision = DecisionAgent(threshold)

    def screen(self, t: dict) -> dict:
        start = time.perf_counter()
        t = {**t, "transaction_id": t.get("transaction_id") or str(uuid.uuid4())}
        tx, beh, pat = self.transaction.analyze(t), self.behavioral.analyze(t), self.pattern.analyze(t)
        out = self.decision.decide(t, tx, beh, pat)
        return {"transaction_id": t["transaction_id"], **out, "recommendation": self.recommend(out),
                "agent_outputs": [tx, beh, pat], "processing_time_ms": round((time.perf_counter() - start) * 1000, 2),
                "timestamp": datetime.now().isoformat()}

    @staticmethod
    def recommend(out: dict) -> str:
        if out["is_fraud"]:
            return "escalate"  # hand off to the InvestigatorAI multi-agent investigation
        return "review" if out["risk_score"] > 0.2 else "approve"

    def evaluate(self, n: int | None = None) -> dict:
        df = self.df if n is None else self.df.sample(min(n, len(self.df)), random_state=42)
        t0 = time.perf_counter()
        preds = [self.screen(r)["is_fraud"] for r in df[["transaction_id", *FIELDS]].to_dict("records")]
        y, p = df.is_fraud.to_numpy(), np.array(preds)
        tp, fp = int((y & p).sum()), int((~y & p).sum())
        fn, tn = int((y & ~p).sum()), int((~y & ~p).sum())
        return {"samples": len(df), "threshold": self.decision.threshold,
                "accuracy": round((tp + tn) / len(df), 4),
                "precision": round(tp / (tp + fp), 4) if tp + fp else 0.0,
                "recall": round(tp / (tp + fn), 4) if tp + fn else 0.0,
                "false_positive_rate": round(fp / (fp + tn), 4) if fp + tn else 0.0,
                "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
                "avg_latency_ms": round((time.perf_counter() - t0) * 1000 / len(df), 2)}


def _py(v: Any) -> Any:
    return v.item() if hasattr(v, "item") else v


@lru_cache
def get_screener() -> GuardianScreener:
    return GuardianScreener()
