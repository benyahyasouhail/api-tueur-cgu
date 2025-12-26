import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import json

# --- CONFIGURATION API ---
app = FastAPI()

# Permet à l'extension Chrome (qui tourne sur n'importe quel site) de parler au serveur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Gemini (Réutilise ta clé)
os.environ["GEMINI_API_KEY"] = "AIzaSyBmV31ornKkLcMu6-OzGKJmLkyqSsL3vNc" # <-- N'oublie pas de remettre ta clé !
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Modèle de données : Ce que l'extension va nous envoyer
class CGURequest(BaseModel):
    text: str

# --- LA FONCTION D'INTELLIGENCE (Celle que tu as validée) ---
def analyze_logic(text_cgu):
    system_prompt = """
    Tu es "Le Tueur de CGU". Analyse ce texte juridique.
    Cherche ces dangers : Vol de Propriété Intellectuelle, Vente de données, Résiliation difficile, Renonciation aux recours.
    
    Réponds UNIQUEMENT en JSON strict avec ce format :
    {
      "danger_level": "SAFE" | "WARNING" | "TOXIC",
      "summary": "Résumé court",
      "flags": [
        {"title": "Titre", "quote": "Preuve", "explanation": "Pourquoi c'est grave"}
      ]
    }
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{system_prompt}\n\nTEXTE À ANALYSER :\n{text_cgu}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# --- LA ROUTE (Le point d'entrée pour l'extension) ---
@app.post("/analyze")
async def analyze_endpoint(request: CGURequest):
    print(f"📩 Reçu une demande d'analyse ({len(request.text)} caractères)")
    result = analyze_logic(request.text)
    return result

@app.get("/")
def read_root():
    return {"status": "Le Tueur de CGU est en ligne 🟢"}

if __name__ == "__main__":
    print("🚀 Démarrage du serveur sur http://127.0.0.1:8000")

    uvicorn.run(app, host="127.0.0.1", port=8000)
