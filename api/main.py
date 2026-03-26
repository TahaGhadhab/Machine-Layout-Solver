from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import MatrixRequest, FlowAnalysisRequest
from algorithms import king, chaining, analysis

app = FastAPI(title="Machine Layout Solver API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    return {"status": "ok"}

@app.post("/api/king")
def run_king(req: MatrixRequest):
    return king.king_method(req.matrix)

@app.post("/api/chaining")
def run_chaining(req: MatrixRequest):
    return chaining.chaining_method(req.matrix)

@app.post("/api/analyze")
def run_analyze(req: FlowAnalysisRequest):
    return analysis.analyze(req.matrix, req.groups, req.routing)
