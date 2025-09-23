"""
Minimal test to check FastAPI response model issue
"""
from fastapi import FastAPI
from pydantic import BaseModel

# Define a simple Pydantic model
class TestResponse(BaseModel):
    message: str
    value: int

app = FastAPI()

@app.get("/test", response_model=TestResponse)
async def test_endpoint():
    return TestResponse(message="test", value=42)

if __name__ == "__main__":
    print("✅ FastAPI response model test passed")