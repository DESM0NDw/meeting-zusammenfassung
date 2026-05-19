import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

EXAMPLES = [
    {
        "id": "sprint",
        "label": "Sprint Planning",
        "transcript": """Sprint Planning Meeting — Team Entwicklung
Datum: 15. Mai 2024, 09:00 Uhr
Teilnehmer: Sarah (PO), Max (Tech Lead), Julia (Dev), Tom (Dev), Lisa (QA)

Sarah: Guten Morgen alle! Heute planen wir Sprint 23. Das Ziel ist die Fertigstellung des Checkout-Flows.
Max: Ich hab die Story Points abgeschätzt. Der Checkout-Flow hat ca. 34 Punkte — das ist realistisch für zwei Wochen.
Julia: Ich würde gerne die Payment-Integration übernehmen. Das ist meine Stärke.
Tom: Dann mach ich den Warenkorb und die Bestellbestätigung.
Sarah: Perfekt. Lisa, kannst du die Testabdeckung auf mindestens 80% sicherstellen?
Lisa: Ja, aber ich brauche die Staging-Umgebung bis Mittwoch. Sonst verzögert sich alles.
Max: Ich kümmere mich darum. Ich spreche heute noch mit DevOps.
Sarah: Gut. Dann beschließen wir: Sprint-Ziel ist der vollständige Checkout-Flow. Review ist in 14 Tagen.
Max: Eine Sache noch — wir müssen die API-Rate-Limits mit dem Payment-Anbieter klären. Das könnte ein Blocker werden.
Sarah: Stimmt. Max, du übernimmst das bis Ende der Woche?
Max: Ja, mach ich.""",
    },
    {
        "id": "strategy",
        "label": "Q3-Strategie",
        "transcript": """Strategiemeeting Q3-Roadmap
Datum: 3. Juni 2024, 14:00 Uhr
Teilnehmer: Anna (CEO), Markus (CPO), Sandra (Head of Sales), David (CTO)

Anna: Wir müssen heute die Q3-Prioritäten festlegen. Umsatzziel ist 1,2 Millionen Euro.
Markus: Das Enterprise-Dashboard ist der wichtigste Feature-Block. Drei Großkunden warten darauf.
Sandra: Ohne das Dashboard verlieren wir mindestens zwei Deals. Wert ca. 400k.
David: Das Dashboard ist machbar in Q3, aber wir müssen das API-Refactoring verschieben.
Anna: Das Refactoring verschieben wir auf Q4. Enterprise-Dashboard hat oberste Priorität.
Markus: Dann brauchen wir zwei zusätzliche Entwickler. Können wir das Budget freigeben?
Anna: Ja. Ich genehmige zwei Senior-Devs für Q3. HR soll sofort mit der Suche anfangen.
Sandra: Für den Sales-Cycle brauche ich eine Demo-Umgebung bis 15. Juli.
David: Das schaffen wir. Ich plane die Demo-Env bis 10. Juli ein.
Anna: Zusammenfassung: Dashboard Q3 Priorität 1, Refactoring auf Q4, zwei neue Devs einstellen, Demo bis 10. Juli.""",
    },
    {
        "id": "retro",
        "label": "Team-Retrospektive",
        "transcript": """Retrospektive Sprint 22
Datum: 8. Mai 2024, 15:00 Uhr
Teilnehmer: Max (Tech Lead), Julia (Dev), Tom (Dev), Lisa (QA), Sarah (PO)

Max: Was lief gut? Julia, fang du an.
Julia: Die Kommunikation war diesmal viel besser. Daily Standups haben funktioniert.
Tom: Stimme ich zu. Aber die Code-Reviews haben zu lange gedauert. Manchmal 3 Tage Wartezeit.
Max: Das ist ein echtes Problem. Wir sollten eine SLA einführen — maximal 24 Stunden für Reviews.
Sarah: Gute Idee. Können wir das als Team-Regel festhalten?
Max: Ja. Ab jetzt: Code Reviews innerhalb von 24 Stunden. Tom, kannst du das in die Team-Doku eintragen?
Tom: Mach ich bis heute Abend.
Lisa: Die Test-Daten sind veraltet. Ich musste letzte Woche 2 Stunden damit verschwenden.
Julia: Ich könnte ein Script schreiben das die Testdaten automatisch refresht.
Lisa: Sehr hilfreich!
Max: Super, Julia übernimmt das. Ziel: bis nächsten Mittwoch fertig.
Sarah: Action Items klar — Tom dokumentiert Review-SLA, Julia baut Testdaten-Script.""",
    },
]

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


@app.get("/api/examples")
def get_examples():
    return [{"id": e["id"], "label": e["label"], "transcript": e["transcript"]} for e in EXAMPLES]


class SummarizeRequest(BaseModel):
    transcript: str


class TodoItem(BaseModel):
    text: str
    assignee: str


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
    {{"text": "<konkrete Aufgabe>", "assignee": "<Person oder Team>"}},
    {{"text": "<konkrete Aufgabe>", "assignee": "<Person oder Team>"}}
  ]
}}

Regeln:
- summary: prägnant, auf Deutsch, 2-3 Sätze
- decisions: nur wirklich getroffene Entscheidungen (keine Diskussionspunkte)
- todos: nur konkrete Aufgaben mit klarer Verantwortlichkeit, auf Deutsch
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
