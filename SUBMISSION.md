BOTTLENECK DIAGNOSTIC SUBMISSION

Name: Anirudh Singh Banirot
Public Github Repo link: https://github.com/aiwithleo/C7_AI_Bottleneck_Diagnoser
Deploy link (frontend): https://aijourneyleo-c7-ai-bottleneck-diagnoser.hf.space
Deploy link (API): https://c7-ai-bottleneck-diagnoser.onrender.com

---

## MOVE 1: BE THE TOOL YOURSELF

### Person 1 — Sameer

**Raw record:**
- Question: evidence/Move1_Sameer Question.jpg
- Response: evidence/Move1_Sameer Reponse.jpg

**The sentence I gave them:**
"Your bottleneck is not a knowledge gap. You keep going back to the LLM for a better plan instead of building the ugly first version of the last one, so you reset to zero every time. If you go learn more this week, you will have a fresh plan and still no working product."

**How they reacted / what they did next:**
Pushed back and re-asserted the knowledge framing. Said he would "still stick with his old response" and listed specific technical tasks he cannot do (getting API keys, embedding them in code, exporting to a working system). He did not act on the sentence. He defended the wall harder when it was named directly, generating a fresh technical-sounding reason to stay stuck.

---

### Person 2 — Satyam

**Raw record:**
- Description: evidence/Move1_Satyam.jpg
- Response: evidence/Move1_Satyam Reponse.jpg

**The sentence I gave them:**
"You are solving a scaling problem you do not have yet. RAG, databases, cost limits, rate limits — none of that matters before one working feature for one real user. You are about to research the architecture more instead of building."

**How they reacted / what they did next:**
Acknowledged the sentence ("Ok") and then immediately reached for more architecture in the same message — "thinking of using RAG, will check the database and if not present will use LLM, I need to think more about this." He named the exact escape hatch the diagnosis predicted, confirming the wall, and then walked straight into it.

---

## MOVE 2: THE HYPOTHESIS (timestamped, before first commit)

**The claim:**
A sharp predictive sentence — true of one person and false of most others, carrying the prediction that their instinctive fix will not work — will produce a behavioral response: they act on it, or ask unprompted "so what do I do about it." The same person handed a vague flattering line will only nod. The whole bet is the gap between those two reactions.

**Result that proves me right:**
Both people act on the sharp sentence (take action or ask what to do). Neither acts on the vague control line.

**Result that means I built a horoscope:**
The vague line moves them as much as the precise one. Both mostly nod, or both mostly act. No gap between the two reactions.

**Kill-number:**
Neither person acts on the sharp sentence (both give polite nods), OR the vague control line lands just as hard as the precise sentence person-for-person. Either means the discrimination failed and my sentences read like horoscopes.

**Timestamp / commit link:**
https://github.com/aiwithleo/C7_AI_Bottleneck_Diagnoser/commit/f81ad528cd6c2578d914795ad2d4d721e19b0886

---

## MOVE 3: THE SYSTEM DESIGN

![Move 3 Boundary Diagram](evidence/Move3_Boundary.jpg)

**Deterministic parts:**
- The 4-bottleneck taxonomy (planning_loop, premature_scaling, wont_ship, no_validated_problem) — fixed, defined by hand from Move 1 observations
- The escape hatch per bottleneck — fixed text, not generated
- The output sentence template per bottleneck — fixed, not generated
- The rule for what counts as behavioral evidence vs a polite nod

**Probabilistic parts:**
- The LLM (Llama 3.1 8B via Groq) reads the person's self-description and classifies it into one of the four fixed bottlenecks
- Temperature set to 0 to minimise drift

**Where the bottleneck gets judged, and why:**
The LLM classifies into my fixed taxonomy — it cannot free-generate a diagnosis or invent a new bottleneck. The taxonomy is deterministic and mine. The classification of which bucket this person belongs to is probabilistic. This means the output sentence and escape hatch are always drawn from a set I designed and tested, not hallucinated fresh for each user.

**Failure mode I accepted:**
The model only reads words, not behavior. It misclassified Sameer as premature_scaling (because he mentioned API keys and deployment) when the actual wall from watching him was planning_loop (he keeps re-planning, never starts). The model cannot see the gap between what someone says and what they actually do — which is exactly the gap a sharp human uses to locate the real wall. The taxonomy mitigates this but does not eliminate it.

---

## MOVE 4: DOMAIN MODELLING

![Move 4 Domain Model](evidence/Move4_Domain.jpg)

**Schema:**

`users` table (managed by Supabase Auth)
- id (PK, uuid)
- email

`sessions` table
- id (PK, uuid)
- user_id (FK → auth.users.id) — the load-bearing link: diagnosis belongs to one user
- self_description (text) — what the person typed
- bottleneck_identified (text) — which of the 4 buckets the LLM classified them into
- escape_hatch (text) — the fixed escape hatch for that bottleneck
- output_sentence (text) — the full sentence returned to the user
- created_at (timestamptz)

The foreign key from sessions.user_id to auth.users.id is the evidence link — it connects what the tool said to who received it, which is the only way to prove the tool found a specific person rather than generating a generic sentence.

**Row-level security:**
RLS enabled on sessions table. Policy: `auth.uid() = user_id` for all operations. One user can never read, update, or delete another user's rows.

**Two-user test — two accounts, attempted cross-read, result:**

1. Signed in as testuser1@test.com — inserted one session row (ID: 195e6d08-2107-4610-b1e9-d7aa3a84258d)
2. Signed in as testuser2@test.com — queried all sessions
3. Result: `[]` — empty array. Zero rows returned. RLS blocked the cross-read completely.

---

## MOVE 5: THE FINAL REPORT

### Person A — Cold user (did not know about the tool beforehand)

**The diagnosis I gave:**
`no_validated_problem`

"You are building for an imagined user. You have not yet talked to a real person who has this problem badly enough that they would change their behavior to fix it. You are about to build more features to make it more appealing. Flip it — one real conversation with a potential user before one more line of code."

**What they actually did after (behavioral evidence):**
Immediately handed me their own tool to test, making me their first real user within the same conversation. The escape hatch said "one real conversation with a potential user" — they acted on it before the conversation ended. They did not nod and move on. They turned to the person next to them and said: test mine.

Evidence: evidence/Tool - no_validated_problem diagnosis.jpg + cold user evidence (attached)

---

### Person B — Satyam (coached, from Move 1)

**The diagnosis I gave:**
`premature_scaling`

"You are solving a scaling problem you do not have yet. RAG, databases, cost limits, rate limits — none of that matters before one working feature for one real user. You are about to research the architecture more. Do not. Build it broken for one person first — that is completely free on Groq's free tier."

**What they actually did after (behavioral evidence):**
Acknowledged the diagnosis and in the same message reached for more architecture: "thinking of using RAG, will check the database, I need to think more about this." Named the exact escape hatch the sentence predicted, then walked straight into it.

---

### The surprise

My Move 2 bet was that a sharp sentence creates motion. The kill condition fired on both Move 1 subjects — Sameer re-asserted his knowledge framing, Satyam reached for RAG. Neither acted. Both confirmed the diagnosis was accurate, then used that confirmation to generate a fresh reason to stay exactly where they were.

But the cold stranger moved immediately.

The difference was not sentence sharpness. The sentence was the same quality in all three cases. The difference was readiness. Sameer and Satyam had already built a practiced defense for their wall — naming it gave them something to push against. The cold user had not yet rehearsed a defense. The same sentence that bounced off an entrenched pattern cut straight through a fresh one.

The real finding: the tool locates the wall accurately but cannot predict whether the person is ready to stop defending it. Accuracy and motion are different variables. I had conflated them in Move 2.
