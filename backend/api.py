import sys
import os

# Add current directory to path so db_manager can be found when run from repo root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# SQLite override for Render compatibility (deb/ubuntu systems might have old sqlite)
try:
    import sqlite3
    if sqlite3.sqlite_version_info < (3, 35, 0):
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import db_manager
from sse_starlette.sse import EventSourceResponse

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Models Setup
db = None
llm = None

@app.on_event("startup")
def startup_event():
    global db, llm
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        # Use relative path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "embeddings", "gita_db")
        db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        llm = Ollama(model="qwen3:4b")
        print("AI Models loaded successfully!")
    except Exception as e:
        print(f"Error loading AI models: {e}")

# -----------------
# Pydantic Models
# -----------------
class AuthRequest(BaseModel):
    username: str
    password: str

class ChatCreateRequest(BaseModel):
    user_id: str
    title: str

class MessageRequest(BaseModel):
    chat_id: str
    role: str
    content: str
    docs: Optional[List[str]] = None

class ChatPromptRequest(BaseModel):
    chat_id: str
    user_id: str
    prompt: str
    language: Optional[str] = "English"

# -----------------
# Authentication
# -----------------
@app.post("/auth/login")
def login(req: AuthRequest):
    success, result = db_manager.verify_user(req.username, req.password)
    if success:
        return {"success": True, "user_id": result, "username": req.username}
    raise HTTPException(status_code=401, detail=result)

@app.post("/auth/signup")
def signup(req: AuthRequest):
    success, result = db_manager.create_user(req.username, req.password)
    if success:
        return {"success": True, "message": "Account created!"}
    raise HTTPException(status_code=400, detail=result)

# -----------------
# Chats
# -----------------
@app.get("/users/{user_id}/chats")
def get_chats(user_id: str):
    return db_manager.get_user_chats(user_id)

@app.post("/chats")
def create_chat(req: ChatCreateRequest):
    chat_id = db_manager.create_chat(req.user_id, req.title)
    return {"chat_id": chat_id}

@app.get("/chats/{chat_id}/messages")
def get_messages(chat_id: str):
    return db_manager.get_chat_messages(chat_id)

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    # Optional: Implement delete in db_manager
    conn = db_manager.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    c.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/chats/{chat_id}/rename")
def rename_chat(chat_id: str, payload: dict):
    new_title = payload.get("title")
    conn = db_manager.get_connection()
    c = conn.cursor()
    c.execute("UPDATE chats SET title = ? WHERE id = ?", (new_title, chat_id))
    conn.commit()
    conn.close()
    return {"success": True}

# -----------------
# AI Chat Streaming
# -----------------
@app.post("/chats/{chat_id}/stream")
async def stream_chat(chat_id: str, req: ChatPromptRequest, request: Request):
    """
    Expects { chat_id, user_id, prompt }.
    Saves user message, generates AI response with SSE, saves AI message.
    """
    prompt = req.prompt
    
    # Save user message
    db_manager.add_message(chat_id, "user", prompt)

    # Context retrieval
    docs = db.similarity_search(prompt, k=5)
    context = ""
    doc_contents = []
    for doc in docs:
        context += doc.page_content + "\n\n"
        doc_contents.append(doc.page_content)

    llm_prompt = f"""
You are NOT a normal AI assistant.
You are a spiritual guide that answers ONLY using Bhagavad Gita philosophy and teachings of Lord Krishna.

STRICT RULES:
- Do NOT give modern psychological advice or generic motivational advice.
- Answer ONLY according to Bhagavad Gita wisdom.
- Reply ONLY in the requested language: {req.language}. (Note: Keep the Sanskrit shlok in Sanskrit, but translate the meaning, explanation, solution, and suggestions into {req.language}).
- Keep answers spiritual, calm, wise, and practical.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS (using markdown headings):

### 🕉 Solution
[Provide a clear, brief spiritual solution based on Gita teachings]

### 📖 Explanation
[Explain the philosophy behind this solution in simple language]

### 📜 Bhagavad Gita Shlok & Meaning
* **Shlok**: [Provide the relevant Sanskrit shlok or its transliteration]
* **Reference**: [Chapter X, Verse Y]
* **Meaning**: [Provide the translation and meaning of this shlok as it applies to the user's question]

### 💡 Practical Suggestions
[Give 1-2 actionable, spiritual suggestions or practices for daily life]

Teachings:
{context}

Question: {prompt}
Answer:
"""

    async def event_generator():
        full_response = ""
        try:
            for chunk in llm.stream(llm_prompt):
                if await request.is_disconnected():
                    break
                full_response += chunk
                # Send text chunk
                yield {"event": "message", "data": chunk}
            
            # Save assistant message to DB after completion
            db_manager.add_message(chat_id, "assistant", full_response, docs=doc_contents)
            
            # Send docs as a special event
            import json
            yield {"event": "docs", "data": json.dumps(doc_contents)}
            yield {"event": "done", "data": "[DONE]"}
            
        except Exception as e:
            traceback.print_exc()
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())
