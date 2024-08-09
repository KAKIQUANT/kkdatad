from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import hashlib
import uuid
import clickhouse_connect
import datetime

app = FastAPI()

# Connect to ClickHouse
client = clickhouse_connect.get_client(host='localhost', port=8123, username='default', password='')

# Pydantic model for input validation
class UserRequest(BaseModel):
    username: str
    email: EmailStr

# Function to generate API key
def generate_api_key(username: str, email: str) -> str:
    salt = uuid.uuid4().hex
    key = hashlib.sha256(f"{username}{email}{salt}".encode()).hexdigest()
    return key

# Route to create and return API key
@app.post("/generate_api_key/")
async def create_api_key(user_request: UserRequest):
    # Check if user already exists
    query = "SELECT COUNT(*) FROM users WHERE username = %(username)s AND email = %(email)s"
    count = client.query(query, params={"username": user_request.username, "email": user_request.email})
    
    if count == 1:
        raise HTTPException(status_code=400, detail="User already exists")

    # Generate API key
    api_key = generate_api_key(user_request.username, user_request.email)

    # Insert user data into ClickHouse
    client.insert(
        "users",
        [{
            "username": user_request.username,
            "email": user_request.email,
            "api_key": api_key,
            "created_at": datetime.datetime.now()
        }]
    )

    return {"api_key": api_key}
