from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Knowledge Graph Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Knowledge Graph API running"}

@app.post("/upload")
async def upload():
    return {"status": "stub"}

@app.post("/query")
async def query(question: str):
    return {"answer": "stub"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)