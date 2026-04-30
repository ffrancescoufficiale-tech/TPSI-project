import json
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def genera_quiz(argomento: str, difficolta: str, n: int, lingua: str = "it") -> dict:
    lingua_istruzione = (
        "Generate all questions, options and explanations in ENGLISH."
        if lingua == "en"
        else "Genera tutte le domande, opzioni e spiegazioni in ITALIANO."
    )

    prompt = f"""{lingua_istruzione}
Crea un quiz con {n} domande su "{argomento}".
Difficoltà: {difficolta}. Numero domande: {n}.
Rispondi SOLO con un JSON valido, senza testo prima o dopo, senza markdown, senza backtick.
Struttura esatta:
{{
  "domande": [
    {{
      "testo": "testo della domanda",
      "opzioni": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "corretta": "A",
      "spiegazione": "breve spiegazione del perché questa è la risposta corretta"
    }}
  ]
}}"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Sei un Quiz Master. Rispondi SOLO con JSON valido, niente altro."},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=3000,
        temperature=0.7,
    )

    raw = completion.choices[0].message.content.strip()

    # Pulizia robusta: estrai solo il JSON
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Il modello non ha restituito JSON valido:\n{raw}")

    data = json.loads(raw[start:end])

    u = completion.usage
    data["tokens"] = {
        "prompt":   u.prompt_tokens,
        "risposta": u.completion_tokens,
        "totale":   u.total_tokens,
    }
    return data