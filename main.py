import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
def root():
    return {"message": "Socratic Bot backend is live."}

@app.post("/chat")
async def socratic_guide(request: PromptRequest):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Socratic AI mentor. "
                    "Do not give direct answers. Instead, guide the user by asking thoughtful, open-ended questions. "
                    "Help them explore methods or steps to solve their problem."
                )
            },
            {"role": "user", "content": request.prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.85,
            max_tokens=500,
        )

        answer = response.choices[0].message.content
        return {"response": answer}

    except Exception as e:
        return {"error": str(e)}
