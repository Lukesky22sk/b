from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_data = {}

class AnswerRequest(BaseModel):
    user: str
    answer: str

@app.post("/api/answers")
def post_answer(data: AnswerRequest):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Socratic AI mentor. Do not give answers. "
                    "Only respond with thoughtful, open-ended questions that challenge the user's assumptions, "
                    "encourage deeper thinking, or help clarify the issue they are exploring."
                )
            },
            {"role": "user", "content": data.answer}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.85,
        )

        question = response.choices[0].message.content

        user_data[data.user] = {
            "question": question,
            "guidance": "Reflect on this and consider alternative viewpoints."
        }

        return user_data[data.user]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {str(e)}")
