import sys
import os
from typing import List, Dict, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add current directory to path to find algorithms
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from algorithms import king, chaining, analysis

app = FastAPI(title="Machine Layout Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatrixRequest(BaseModel):
    matrix: List[List[int]]

class FlowAnalysisRequest(BaseModel):
    matrix: List[List[int]]
    groups: Dict[int, int]
    routing: Optional[List[List[int]]] = None

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    return {"status": "ok", "message": "Machine Layout API is live"}

@app.post("/king")
@app.post("/api/king")
def run_king(req: MatrixRequest):
    return king.king_method(req.matrix)

@app.post("/chaining")
@app.post("/api/chaining")
def run_chaining(req: MatrixRequest):
    return chaining.chaining_method(req.matrix)

@app.post("/analyze")
@app.post("/api/analyze")
def run_analyze(req: FlowAnalysisRequest):
    return analysis.analyze(req.matrix, req.groups, req.routing)
