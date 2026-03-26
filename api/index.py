from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
def test():
    return {"status": "ok", "source": "index.py"}

@app.get("/")
@app.get("/api")
@app.get("/api/")
def read_root():
    return {"status": "ok", "message": "Simplest API"}

@app.post("/api/king")
@app.post("/king")
def run_king():
    return {"message": "King hit"}
