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
    allow_origins=["*"],  # Adjust in production for security
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
                    "Do NOT give direct answers or ask the user questions. "
                    "Instead, list specific methods or approaches relevant to the user's problem, "
                    "and walk them through each method step-by-step, explaining how to apply them. "
                    "Your goal is to help the user solve the problem by guiding them logically through the process."
                )
            },
            {"role": "user", "content": request.prompt}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=700,
        )

        answer = response.choices[0].message.content.strip()
        return {"response": answer}

    except Exception as e:
        return {"error": str(e)}
