from fastapi import FastAPI

app = FastAPI(
    title="Electronic Dean's Office API (Hardened)",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"message": "Electronic Dean's Office API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
