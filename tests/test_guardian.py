import pandas as pd
import pytest

from api.guardian.engine import GuardianScreener, PatternAgent, load_data

SAFE = dict(amount=42.0, merchant_category="grocery", hour=14, day_of_week=2, user_country="US",
            merchant_country="US", payment_method="debit_card", card_present=True)
RISKY = dict(amount=6200.0, merchant_category="cryptocurrency", hour=2, day_of_week=5, user_country="US",
             merchant_country="RO", payment_method="crypto", card_present=False)


@pytest.fixture(scope="module")
def screener():
    return GuardianScreener(load_data().sample(1500, random_state=0))


def test_safe_transaction_is_approved(screener):
    r = screener.screen(SAFE)
    assert not r["is_fraud"] and r["recommendation"] == "approve"
    assert {o["agent"] for o in r["agent_outputs"]} == {"TransactionAgent", "BehavioralAgent", "PatternAgent"}


def test_risky_transaction_is_escalated(screener):
    r = screener.screen(RISKY)
    assert r["is_fraud"] and r["recommendation"] == "escalate" and r["risk_score"] > 0.3
    assert "FRAUD" in r["explanation"]


def test_patterns():
    names = {p["name"] for p in PatternAgent().analyze(RISKY)["matched_patterns"]}
    assert names == {"high_value_fraud", "velocity_fraud", "geographic_fraud", "category_fraud"}
    card_test = {**SAFE, "amount": 1.5, "card_present": False}
    assert "card_testing" in {p["name"] for p in PatternAgent().analyze(card_test)["matched_patterns"]}


def test_similar_excludes_self(screener):
    row = screener.df.iloc[0].to_dict()
    sims = screener.behavioral.similar(row, k=5)
    assert len(sims) == 5 and row["transaction_id"] not in {s["transaction_id"] for s in sims}


def test_evaluate_shape(screener):
    m = screener.evaluate(200)
    assert m["samples"] == 200 and 0 <= m["accuracy"] <= 1
    assert sum(m["confusion"].values()) == 200
