from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # for dev, allow all; later restrict to your frontend domain
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
data = await request.json()
user_message = data.get("message", "")

model = genai.GenerativeModel("models/gemini-1.5-flash")
response = model.generate_content(user_message)

return {"reply": response.text}



from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# Allow frontend calls
app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # for dev, allow all
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)



user_data = {} # {user_id: {"messages": [], "count": 0, "plan": "free"}}

FREE_LIMIT = 10 # max queries/day for free tier


@app.post("/chat")
async def chat(request: Request):
data = await request.json()
user_id = data.get("user_id", "guest") # 👈 mock user, in real SaaS you'd use auth
user_message = data.get("message", "")

if not user_message:
raise HTTPException(status_code=400, detail="Message is required.")

# Initialize user session if new
if user_id not in user_data:
user_data[user_id] = {"messages": [], "count": 0, "plan": "free"}

user_info = user_data[user_id]

# Check subscription limits
if user_info["plan"] == "free" and user_info["count"] >= FREE_LIMIT:
return {"reply": "⚠️ Free plan limit reached. Upgrade to Premium for unlimited access."}

# Call Gemini API
model = genai.GenerativeModel("models/gemini-1.5-flash")
response = model.generate_content(user_message)

# Save history & count
user_info["messages"].append({"user": user_message, "bot": response.text})
user_info["count"] += 1

return {
"reply": response.text,
"messages": user_info["messages"], # return history
"plan": user_info["plan"],
"queries_used": user_info["count"],
}


@app.post("/upgrade")
async def upgrade(request: Request):
"""Mock endpoint to upgrade user to premium plan."""
data = await request.json()
user_id = data.get("user_id", "guest")

if user_id not in user_data:
user_data[user_id] = {"messages": [], "count": 0, "plan": "free"}

user_data[user_id]["plan"] = "premium"
return {"status": "success", "message": "✅ User upgraded to Premium."}
