
from fastapi import FastAPI

app = FastAPI(title="BikeStop")

@app.get("/")
def home():
    return {"status": "BikeStop app caricata correttamente"}
