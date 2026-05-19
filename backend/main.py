import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=GROQ_API_KEY)


@app.get("/api/health")
def health():
    return {"status": "ok"}


MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB


@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Datei zu groß (max. 25 MB)")
    transcription = groq_client.audio.transcriptions.create(
        file=(file.filename, audio_bytes, file.content_type or "audio/mpeg"),
        model="whisper-large-v3-turbo",
        response_format="json",
    )
    return {"transcript": transcription.text}


class SummarizeRequest(BaseModel):
    transcript: str


class TodoItem(BaseModel):
    text: str
    assignee: str
    priority: str


class SummarizeResponse(BaseModel):
    summary: str
    decisions: list[str]
    todos: list[TodoItem]


@app.post("/api/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    prompt = f"""Analysiere das folgende Meeting-Transcript und antworte ausschließlich im angegebenen JSON-Format.

Meeting-Transcript:
{req.transcript}

Antworte mit diesem JSON (keine weiteren Erklärungen, nur JSON):
{{
  "summary": "<2-3 Sätze die das Meeting und seine wichtigsten Ergebnisse zusammenfassen>",
  "decisions": ["<getroffene Entscheidung 1>", "<getroffene Entscheidung 2>"],
  "todos": [
    {{"text": "<konkrete Aufgabe>", "assignee": "<Person oder Team>", "priority": "<Hoch|Mittel|Niedrig>"}},
    {{"text": "<konkrete Aufgabe>", "assignee": "<Person oder Team>", "priority": "<Hoch|Mittel|Niedrig>"}}
  ]
}}

Regeln:
- summary: prägnant, auf Deutsch, 2-3 Sätze
- decisions: nur wirklich getroffene Entscheidungen (keine Diskussionspunkte)
- todos: nur konkrete Aufgaben mit klarer Verantwortlichkeit, auf Deutsch
- priority: Hoch = zeitkritisch oder blockiert andere, Mittel = wichtig aber nicht dringend, Niedrig = nice-to-have
- Mindestens 2 decisions und 2 todos wenn vorhanden"""

    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2,
    )

    text = completion.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text.strip())
    return SummarizeResponse(**data)
