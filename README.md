# Meeting-Zusammenfassung

AI-powered meeting summary demo. Paste a transcript or transcribe an audio recording — get a summary, key decisions, and prioritized to-dos.

**Live:** https://meeting-demo.autonomika.de

## How it works

1. User pastes a meeting transcript or uploads/drops an audio file
2. Audio is transcribed via [Groq](https://groq.com/) Whisper (`whisper-large-v3-turbo`)
3. Transcript is sent to Groq (`llama-3.1-8b-instant`) with a structured prompt
4. Returns: 2–3 sentence summary, list of decisions made, prioritized to-dos with assignees
5. To-dos are sorted by priority (Hoch → Mittel → Niedrig)

## Stack

| Layer | Tech |
|-------|------|
| Frontend | SvelteKit + adapter-static + Nginx |
| Backend | FastAPI + Python |
| Transcription | Groq Whisper API (`whisper-large-v3-turbo`) |
| LLM | Groq API (`llama-3.1-8b-instant`) |
| Deploy | Docker Compose on Hetzner Cloud |

## Demo Audio Examples

Three demo MP3 files are included under `frontend/static/audio/`:

- `sprint.mp3` — sprint review meeting
- `strategy.mp3` — strategy session
- `retro.mp3` — retrospective

Generated via `gTTS` (Google Text-to-Speech). Max audio file size: 25 MB (Groq Whisper limit).

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
export GROQ_API_KEY=your_key
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Deploy

```bash
docker compose build --no-cache
docker compose up -d
```

Requires the `1panel-network` Docker network and a `GROQ_API_KEY` in the backend environment.
