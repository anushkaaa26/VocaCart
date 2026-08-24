import streamlit as st
from theme import configure_page, render_header, strip_emoji

# Safely initialize database schema
try:
    import database
    if hasattr(database, "init_app_schema"):
        database.init_app_schema()
except Exception:
    pass

configure_page("Home")
render_header("Home")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None
if "last_item" not in st.session_state:
    st.session_state.last_item = None

# Hero Banner
st.markdown(
    """
<div class="hero-wrap fade-in">
    <div class="hero-title">What are we buying today?</div>
    <div class="hero-subtitle">Speak or type your request in English, Hindi, or Hinglish.</div>
</div>
""",
    unsafe_allow_html=True,
)

# Suggestion Chips
st.markdown("<div style='text-align:center; margin-bottom: 12px;'><span class='tag'>Try asking</span></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Add 2 Loaves of Bread", use_container_width=True):
        st.session_state["pending_text"] = "Add 2 loaves of bread to my cart"
        st.rerun()
with c2:
    if st.button("What is my total?", use_container_width=True):
        st.session_state["pending_text"] = "What is my current total?"
        st.rerun()
with c3:
    if st.button("Set budget to $50", use_container_width=True):
        st.session_state["pending_text"] = "Set my budget to 50 dollars"
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Audio and Text UI Controls
audio_val = st.audio_input("Record audio request", label_visibility="collapsed")
text_val = st.chat_input("Or type your prompt here...")

# Input Resolution Logic
user_text_command = None

if text_val:
    user_text_command = text_val
elif "pending_text" in st.session_state:
    user_text_command = st.session_state.pop("pending_text")
elif audio_val is not None:
    a_bytes = audio_val.getvalue()
    a_hash = hash(a_bytes)
    
    if st.session_state.processed_audio_hash != a_hash:
        st.session_state.processed_audio_hash = a_hash
        
        # Call voice module (returns tuple: transcribed_text, error)
        import voice
        transcribed_text, voice_err = voice.transcribe_audio(audio_val)
        
        if transcribed_text:
            user_text_command = transcribed_text
        else:
            st.session_state.messages.append({"role": "user", "content": "🎙️ [Voice Audio Recorded]"})
            err_msg = voice_err or "Unknown error"
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Audio transcription failed: {err_msg}. Please check your GROQ_API_KEY in `.streamlit/secrets.toml`."
            })
            st.rerun()

# Command Execution & Pipeline
if user_text_command:
    st.session_state.messages.append({"role": "user", "content": user_text_command})

    with st.spinner("Processing request..."):
        try:
            import shopping_agent

            # 1. Parse command logic, execute database changes, and track context
            cmd_result = shopping_agent.execute_command(
                user_text_command, 
                last_item=st.session_state.get("last_item")
            )
            
            # 2. Preserve last referenced item for follow-up context (e.g., "actually make that 5")
            if cmd_result.get("last_item"):
                st.session_state.last_item = cmd_result["last_item"]

            # 3. Format result dictionary into friendly output string
            agent_response = shopping_agent.render_response(cmd_result)

        except Exception as err:
            agent_response = f"Could not process request: {err}"

        cleaned_response = strip_emoji(str(agent_response))
        st.session_state.messages.append({"role": "assistant", "content": cleaned_response})

    st.rerun()

# Conversation History Display
if st.session_state.messages:
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="msg-user"><b>You</b><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="msg-agent"><b>VocaCart Assistant</b><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )