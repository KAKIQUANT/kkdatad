# app.py
from fastapi import FastAPI
from routes.financial_data import router as financial_data_router
from database import setup_database

app = FastAPI()

setup_database()  # Initialize the database

app.include_router(financial_data_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
