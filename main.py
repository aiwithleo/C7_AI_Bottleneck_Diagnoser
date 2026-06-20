import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Deterministic: fixed taxonomy of bottlenecks + escape hatch per type
BOTTLENECKS = {
    "planning_loop": {
        "diagnosis": "You're not stuck on knowledge - you're stuck on starting. You keep going back to the LLM for a better plan instead of building the ugly first version of the last one, so you reset to zero every time.",
        "escape_hatch": "You're about to go learn one more thing before you build. Stop. Open an editor right now, not a chat window. The plan you have is enough."
    },
    "premature_scaling": {
        "diagnosis": "You're solving a scaling problem you don't have yet. RAG, databases, cost limits, rate limits - none of that matters before one working feature for one real user.",
        "escape_hatch": "You're about to research the architecture more. Don't. Build it broken for one person first - that's completely free on Groq's free tier."
    },
    "wont_ship": {
        "diagnosis": "You've built something real and you're polishing it instead of showing it. The next feature you're planning to add is not the thing between you and users - showing it is.",
        "escape_hatch": "You're about to add one more thing before showing anyone. Show one cold stranger today before you touch the code again."
    },
    "no_validated_problem": {
        "diagnosis": "You're building for an imagined user. You haven't yet talked to a real person who has this problem badly enough that they would change their behavior to fix it.",
        "escape_hatch": "You're about to build more features to make it more appealing. Flip it - one real conversation with a potential user before one more line of code."
    }
}

# Probabilistic: LLM classifies which bottleneck this person is in
CLASSIFY_PROMPT = """You are classifying someone's AI bottleneck into exactly one of these four categories:

- planning_loop: keeps learning, researching, or re-planning instead of building the smallest working version
- premature_scaling: worrying about cost, rate limits, architecture, or infrastructure before having one working feature for one user
- wont_ship: has built something real but keeps polishing, adding features, or finding reasons not to show it to anyone
- no_validated_problem: building without having talked to real people who actually have this problem

Person's description of where they're stuck:
\"\"\"{description}\"\"\"

Important: trust what they DID over what they SAY. Trust least the thing they assert most confidently.
Reply with ONLY the category name. One of: planning_loop, premature_scaling, wont_ship, no_validated_problem"""


class DiagnoseRequest(BaseModel):
    description: str


@app.post("/diagnose")
def diagnose(req: DiagnoseRequest):
    if not req.description.strip():
        return {"error": "Please describe where you're stuck."}

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": CLASSIFY_PROMPT.format(description=req.description)}],
        max_tokens=20,
        temperature=0
    )

    bottleneck = response.choices[0].message.content.strip().lower()

    if bottleneck not in BOTTLENECKS:
        bottleneck = "planning_loop"

    b = BOTTLENECKS[bottleneck]
    return {
        "bottleneck": bottleneck,
        "diagnosis": b["diagnosis"],
        "escape_hatch": b["escape_hatch"],
        "sentence": f"{b['diagnosis']} {b['escape_hatch']}"
    }


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Bottleneck Diagnostic API"}
