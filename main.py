import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/questions")
async def get_question(user: str):
    return {
        "question": "What do you think is the best way to approach solving this problem?",
        "guidance": "Consider breaking it down into smaller parts. What do you already know about this type of problem?"
    }

@app.post("/api/answers")
async def post_answer(request: Request):
    body = await request.json()
    user_answer = body.get("answer", "")
    user_id = body.get("user", "anonymous")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Socratic tutor. Never give direct answers. "
                        "Instead, guide the student by asking questions, suggesting methods, and prompting them to think critically. "
                        "Be warm, supportive, and intellectually engaging. The goal is to help the student reach the solution themselves."
                    )
                },
                {"role": "user", "content": user_answer}
            ],
            temperature=0.85,
        )

        socratic_reply = response.choices[0].message.content.strip()

        return {
            "question": socratic_reply,
            "guidance": "Keep exploring the idea. Think about what concepts or methods could help you move forward."
        }

    except Exception as e:
        return {
            "question": "Something went wrong processing your response.",
            "guidance": str(e)
        }
