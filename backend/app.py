# backend/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
import os

# Use the transformers pipeline for sentiment analysis
try:
    from transformers import pipeline
except Exception as e:
    pipeline = None

app = FastAPI(title="Sentiment Analyzer API")

MODEL_NAME = os.environ.get("HF_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")

# Lazy-loading pipeline to reduce startup errors in CI/builds that don't need it
nlp = None
def get_pipeline():
    global nlp
    if nlp is None:
        if pipeline is None:
            raise RuntimeError("transformers not installed")
        nlp = pipeline("sentiment-analysis", model=MODEL_NAME)
    return nlp

class SingleText(BaseModel):
    text: str

class BatchText(BaseModel):
    texts: List[str]

class SentimentResult(BaseModel):
    label: str
    score: float

@app.get("/")
def root():
    return {"ok": True, "name": "Sentiment Analyzer API"}

@app.post("/api/sentiment", response_model=Union[SentimentResult, List[SentimentResult]])
def analyze(payload: Union[SingleText, BatchText]):
    """
    Accepts either {"text": "..."} or {"texts": ["...","..."]} and returns sentiment(s).
    Response label is usually 'POSITIVE' or 'NEGATIVE' for the default model.
    """
    try:
        nlp_local = get_pipeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")

    if isinstance(payload, SingleText):
        out = nlp_local(payload.text)
        # pipeline returns list even for single string
        if len(out) == 0:
            raise HTTPException(status_code=500, detail="No prediction")
        first = out[0]
        return {"label": first.get("label"), "score": float(first.get("score"))}
    else:
        out = nlp_local(payload.texts)
        results = [{"label": o.get("label"), "score": float(o.get("score"))} for o in out]
        return results
