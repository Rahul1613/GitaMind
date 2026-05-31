import streamlit as st
import os
import sys

# Add backend directory to sys.path to import db_manager
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))
import db_manager

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GitaMind | Timeless Wisdom",
    page_icon="🕉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CHATGPT-STYLE UI & CSS
# -----------------------------
st.markdown("""
    <style>
    /* Hide Streamlit Defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Adjust main padding */
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# AUTHENTICATION UI
# -----------------------------
if st.session_state.user_id is None:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("<h1 style='text-align: center;'>🕉 GitaMind</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Login or Sign Up to continue</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                login_username = st.text_input("Username")
                login_password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login")
                
                if submit_login:
                    if login_username and login_password:
                        success, result = db_manager.verify_user(login_username, login_password)
                        if success:
                            st.session_state.user_id = result
                            st.session_state.username = login_username
                            st.rerun()
                        else:
                            st.error(result)
                    else:
                        st.warning("Please fill in all fields.")
                        
        with tab2:
            with st.form("signup_form"):
                signup_username = st.text_input("Choose a Username")
                signup_password = st.text_input("Choose a Password", type="password")
                submit_signup = st.form_submit_button("Sign Up")
                
                if submit_signup:
                    if signup_username and signup_password:
                        success, result = db_manager.create_user(signup_username, signup_password)
                        if success:
                            st.success("Account created! Please log in.")
                        else:
                            st.error(result)
                    else:
                        st.warning("Please fill in all fields.")
                        
    st.stop()

# -----------------------------
# SYSTEM INITIALIZATION
# -----------------------------
@st.cache_resource
def load_db():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db_path = "/Users/rahul/Desktop/degree/all projects/geeta/BhagavadGitaAI/embeddings/gita_db"
    return Chroma(persist_directory=db_path, embedding_function=embeddings)

@st.cache_resource
def load_llm():
    return Ollama(model="qwen3:4b")

try:
    db = load_db()
    llm = load_llm()
except Exception as e:
    st.error(f"Error loading AI models: {e}")
    st.stop()

# -----------------------------
# SIDEBAR (CHAT HISTORY)
# -----------------------------
with st.sidebar:
    st.markdown("### 🕉 GitaMind")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.active_chat_id = None
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.markdown("**Recent Chats**")
    
    # Load user chats
    user_chats = db_manager.get_user_chats(st.session_state.user_id)
    if not user_chats:
        st.caption("No recent chats.")
    else:
        for chat in user_chats:
            # Highlight active chat
            is_active = (chat['id'] == st.session_state.active_chat_id)
            btn_label = f"💬 {chat['title']}"
            if st.button(btn_label, key=chat['id'], use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.active_chat_id = chat['id']
                st.session_state.messages = db_manager.get_chat_messages(chat['id'])
                st.rerun()
                
    st.divider()
    st.markdown(f"👤 **{st.session_state.username}**")
    if st.button("Logout", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.active_chat_id = None
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# MAIN CHAT UI
# -----------------------------

# Show hero only if chat is empty
if len(st.session_state.messages) == 0:
    st.markdown("<h1 style='text-align: center; margin-top: 10vh; font-weight: 600;'>How can I guide you today?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.1rem;'>Ask a question to receive timeless wisdom from the Bhagavad Gita.</p>", unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    avatar = "🕉" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message.get("docs"):
            with st.expander("Explore the Sacred References"):
                for doc in message["docs"]:
                    st.markdown(f"> {doc}")

# React to user input
if prompt := st.chat_input("Ask for spiritual guidance..."):
    
    # If no active chat, create one
    if st.session_state.active_chat_id is None:
        title = prompt[:30] + "..." if len(prompt) > 30 else prompt
        new_chat_id = db_manager.create_chat(st.session_state.user_id, title)
        st.session_state.active_chat_id = new_chat_id
    
    # Add user message to UI and DB
    st.session_state.messages.append({"role": "user", "content": prompt, "docs": None})
    db_manager.add_message(st.session_state.active_chat_id, "user", prompt)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant", avatar="🕉"):
        with st.spinner("The Sage is contemplating..."):
            try:
                # 1. Retrieve context from Chroma DB
                docs = db.similarity_search(prompt, k=5)
                context = ""
                doc_contents = []
                for doc in docs:
                    context += doc.page_content + "\n\n"
                    doc_contents.append(doc.page_content)

                # 2. Prepare the prompt for Ollama
                llm_prompt = f"""
You are NOT a normal AI assistant.
You are a spiritual guide that answers ONLY using Bhagavad Gita philosophy and teachings of Lord Krishna.

STRICT RULES:
- Do NOT give modern psychological advice.
- Do NOT give generic motivational advice.
- Answer ONLY according to Bhagavad Gita wisdom.
- Explain in simple language.
- Reply in the SAME LANGUAGE as the user's question.
- Mention chapter and verse references whenever possible.
- Keep answers spiritual, calm, wise and practical.

Teachings:
{context}

Question: {prompt}
Answer:
"""
                
                # 3. Stream the response directly to the UI
                response_placeholder = st.empty()
                full_response = ""
                
                # Ollama's streaming
                for chunk in llm.stream(llm_prompt):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                
                # Final response display
                response_placeholder.markdown(full_response)
                
                # Display references
                if doc_contents:
                    with st.expander("Explore the Sacred References"):
                        for doc in doc_contents:
                            st.markdown(f"> {doc}")
                
                # Add assistant response to session and DB
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "docs": doc_contents
                })
                db_manager.add_message(st.session_state.active_chat_id, "assistant", full_response, docs=doc_contents)

            except Exception as e:
                st.error(f"A spiritual mist has clouded the connection. Please try again. (Error: {e})")
