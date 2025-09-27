# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("ok") is True

def test_single_sentiment_schema(monkeypatch):
    # monkeypatch the pipeline to avoid heavy model load
    class Fake:
        def __call__(self, text):
            return [{"label": "POSITIVE", "score": 0.99}]
    monkeypatch.setattr('app.get_pipeline', lambda: Fake())
    r = client.post("/api/sentiment", json={"text": "I love this product"})
    assert r.status_code == 200
    data = r.json()
    assert "label" in data and "score" in data

def test_batch_sentiment_schema(monkeypatch):
    class Fake:
        def __call__(self, texts):
            return [{"label": "NEGATIVE", "score": 0.12} for _ in texts]
    monkeypatch.setattr('app.get_pipeline', lambda: Fake())
    r = client.post("/api/sentiment", json={"texts": ["bad","worse"]})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) == 2
