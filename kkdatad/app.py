from fastapi import FastAPI
from routes.financial_data import router as financial_data_router
from database import setup_database

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Initialize the database
    await setup_database()

# Include the financial data routes
app.include_router(financial_data_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
