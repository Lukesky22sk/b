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
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PromptRequest(BaseModel):
    prompt: str
    mode: str = "learning"  # default mode if not provided

@app.get("/")
def root():
    return {"message": "Socratic Bot backend is live."}

@app.post("/chat")
async def socratic_guide(request: PromptRequest):
    try:
        # Define system message based on mode
        if request.mode == "learning":
            system_content = (
                "You are a Socratic AI mentor. "
                "Do NOT give direct answers or ask the user questions. "
                "Instead, list specific methods or approaches relevant to the user's problem, "
                "and walk them through each method step-by-step, explaining how to apply them. "
                "Your goal is to help the user solve the problem by guiding them logically through the process."
            )
        elif request.mode == "answer":
            system_content = (
                "You are an AI assistant. Provide a clear and direct answer to the user's problem without explanations or follow-up questions."
            )
        else:
            return {"error": "Invalid mode. Choose 'learning' or 'answer'."}

        messages = [
            {"role": "system", "content": system_content},
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
