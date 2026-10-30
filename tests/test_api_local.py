"""API smoke tests in screening-only mode (no OPENAI_API_KEY)."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(monkeypatch_module):
    from api.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def monkeypatch_module():
    mp = pytest.MonkeyPatch()
    mp.delenv("OPENAI_API_KEY", raising=False)
    mp.setenv("LOG_TO_FILE", "false")
    yield mp
    mp.undo()


def test_health_reports_screening_only(client):
    h = client.get("/health").json()
    assert h["status"] == "healthy" and h["llm_mode"] == "disabled" and h["guardian_screening"]


def test_screen_endpoint(client):
    r = client.post("/screen", json=dict(amount=6200, merchant_category="cryptocurrency", hour=2, day_of_week=5,
                                         user_country="US", merchant_country="RO", payment_method="crypto",
                                         card_present=False))
    assert r.status_code == 200 and r.json()["recommendation"] == "escalate"
    assert client.post("/screen", json={"amount": -1}).status_code == 422


def test_options_and_samples(client):
    assert "cryptocurrency" in client.get("/screen/options").json()["merchant_category"]
    assert len(client.get("/screen/samples", params={"limit": 3}).json()) == 3


def test_investigation_unavailable_without_key(client):
    r = client.post("/investigate", json={"amount": 1000, "currency": "USD", "description": "x",
                                         "customer_name": "x", "account_type": "Business",
                                         "risk_rating": "Medium", "country_to": "US"})
    assert r.status_code == 503


def test_exchange_rate_works_offline(client):
    r = client.get("/exchange-rate", params={"from_currency": "EUR"})
    assert r.status_code == 200
