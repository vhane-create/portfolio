"""Secure-by-default synthetic FP&A OpenAI API backend."""
import os, json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
app=FastAPI(title="FP&A Copilot Live API")
app.add_middleware(CORSMiddleware,allow_origins=[os.getenv("ALLOWED_ORIGIN","https://vhane-create.github.io")],allow_methods=["GET","POST"],allow_headers=["Content-Type"])
DATA=[("Operations",690000,710000),("Technology",260000,278000),("Sales",465000,485000),("Finance",275000,275000)]
class AskRequest(BaseModel):
    question:str=Field(min_length=4,max_length=500)
def facts():
    rows=[{"department":d,"budget":b,"actual":a,"variance":a-b,"variance_pct":round(100*(a-b)/b,3)} for d,b,a in DATA]
    budget=sum(r["budget"] for r in rows);actual=sum(r["actual"] for r in rows)
    return {"synthetic":True,"currency":"USD","rows":rows,"total_budget":budget,"total_actual":actual,"total_variance":actual-budget}
@app.get("/health")
def health():return {"status":"ok","model_configured":bool(os.getenv("OPENAI_API_KEY"))}
@app.get("/facts")
def get_facts():return facts()
@app.post("/ask")
async def ask(req:AskRequest):
    if not os.getenv("OPENAI_API_KEY"):raise HTTPException(503,"Model not configured")
    if not os.getenv("DEMO_ACCESS_TOKEN"):raise HTTPException(503,"Public access disabled pending authentication")
    # Token must be checked at the edge/reverse proxy; this service intentionally refuses public use until deployed with a trusted auth gateway.
    raise HTTPException(503,"Live inference disabled until authenticated gateway is configured")
