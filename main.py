from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env (if local)
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request model
class PromptRequest(BaseModel):
    prompt: str

# Root route (for Render health check or browser test)
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}

# Main route to get response from OpenAI
@app.post("/chat")
async def chat(request: PromptRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change model if needed
            messages=[{"role": "user", "content": request.prompt}],
            temperature=0.7,
        )
        return {"response": response['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}
