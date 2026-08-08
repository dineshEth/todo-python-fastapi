from fastapi import FastAPI

app = FastAPI(title="Fastapi-todo")

@app.get("/")
def home():
    return {"message":"HOME"}

