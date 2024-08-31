from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routes.downloader import data_router
from routes.user import user_router
from kkdatad.database import engine, SessionLocal
import kkdatad.models as models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Include the financial data routes
app.include_router(data_router)
# Include the user registration routes
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)