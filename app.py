import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai

load_dotenv()
app=Flask(__name__)
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
MODEL_NAME="gemini-3.6-flash"
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured in the .env file.")
client=genai.Client(api_key=GEMINI_API_KEY)
SYSTEM_PROMPT=Path(__file__).with_name("chatbot_config").read_text(encoding="utf-8").strip()

@app.get("/")
def home(): return render_template("index.html")

@app.post("/chat")
def chat():
    data=request.get_json(silent=True) or {}
    message=str(data.get("message","")).strip()
    if not message: return jsonify({"reply":"Please enter a question."}),400
    try:
        r=client.models.generate_content(model=MODEL_NAME,contents=f"{SYSTEM_PROMPT}\n\nUSER QUESTION:\n{message}")
        return jsonify({"reply":(r.text or "").strip() or "I could not generate a response. Please try again."})
    except Exception as e:
        print("Gemini API error:",e)
        return jsonify({"reply":"Sorry, I could not process your question right now."}),500

if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=True)
