import streamlit as st
import tempfile
import os
from utils.speech import transcribe, text
from utils.llm import call_llm
import time
from hashlib import md5

# Page configuration
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Poppins:wght@600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }



    /* Header with gradient text */
    .main-header {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin: 0.25rem 0 1.25rem 0;
        letter-spacing: 0.5px;
        background: linear-gradient(90deg, #5e35b1, #7e57c2, #3f51b5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Sub headers */
    .sub-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #4527A0;
        margin: 0.25rem 0 0.75rem 0;
    }


    /* Highlight block */
    .highlight {
        background: linear-gradient(180deg, #EEF0FF 0%, #F5F6FF 100%);
        padding: 0.9rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(63, 81, 181, 0.18);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #5E35B1, #3F51B5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        letter-spacing: 0.3px;
        transition: all 0.15s ease;
        box-shadow: 0 6px 16px rgba(63, 81, 181, 0.25);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(63, 81, 181, 0.35);
        filter: brightness(1.03);
    }

    /* Ghost button variant */
    .btn-ghost .stButton > button {
        background: white !important;
        color: #3F51B5 !important;
        border: 1px solid rgba(63, 81, 181, 0.25) !important;
        box-shadow: none !important;
    }
    .btn-ghost .stButton > button:hover {
        background: #F3F5FF !important;
    }

    /* Chips (history) */
    .chip {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        margin: 0.25rem 0.25rem 0 0;
        background: white;
        border: 1px solid rgba(63, 81, 181, 0.18);
        color: black;
        border-radius: 999px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.12s ease;
        user-select: none;
    }
    .chip:hover {
        background: #EEF0FF;
        transform: translateY(-1px);
    }

    /* Audio */
    .audio-wrapper {
        border: 1px dashed rgba(63, 81, 181, 0.25);
        border-radius: 12px;
        padding: 0.8rem;
        background: rgba(255,255,255,0.6);
    }

    /* Progress bar tweaks */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #5E35B1, #3F51B5);
    }

    /* Sidebar polish */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
    .side-section-title {
        font-weight: 700;
        color: #4527A0;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
    }

    /* Small separators */
    .divider {
        height: 1px;
        width: 100%;
        background: linear-gradient(90deg, rgba(63,81,181,.15), rgba(63,81,181,.05), rgba(63,81,181,.15));
        margin: 0.8rem 0;
    }
    
    .ai-response {
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)


if 'current_audio' not in st.session_state:
    st.session_state.current_audio = None
if 'audio_files' not in st.session_state:
    st.session_state.audio_files = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'typed_q' not in st.session_state:
    st.session_state.typed_q = ""
if 'pending_question' not in st.session_state:
    st.session_state.pending_question = None
if 'trigger_response' not in st.session_state:
    st.session_state.trigger_response = False
if 'last_audio_hash' not in st.session_state:
    st.session_state.last_audio_hash = None

# App header
st.markdown("<h1 class='main-header'>Voice Chatbot</h1>", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.markdown("<div class='side-section-title'>How to use</div>", unsafe_allow_html=True)
    st.markdown("""
    1) Type or record a question
    2) Click Submit
    3) Listen and download the response
    """)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='side-section-title'>Settings</div>", unsafe_allow_html=True)
    voice_speed = st.slider("Voice Speed", min_value=0.8, max_value=1.2, value=1.0, step=0.1, help="Adjust playback speed")


    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='side-section-title'>Recent Questions</div>", unsafe_allow_html=True)
    if st.session_state.chat_history:
        chip_cols = st.columns(1)
        with chip_cols[0]:
            for q in reversed(st.session_state.chat_history[-10:]):
                if st.button(q[:40] + ("…" if len(q) > 40 else ""), key=f"chip_{hash(q)}"):
                    st.session_state.typed_q = q
    else:
        st.caption("No recent questions yet.")
    col_clear1, col_clear2 = st.columns([1, 1])
    with col_clear1:
        st.button("Clear history", key="clear_hist", on_click=lambda: st.session_state.update(chat_history=[]), help="Remove saved questions")


st.markdown("### 💬 Ask Your Interview Question")

text_tab, voice_tab = st.tabs(["Text", "Voice"])

with text_tab:
    
    with st.form("ask_form", clear_on_submit=False):
        st.text_area(
            "Type your question:",
            key="typed_q",
            height=120,
            placeholder="Enter your interview question here..."
        )
        st.caption("Tip: Focus the textarea and press Ctrl+Enter to submit.")
        submitted = st.form_submit_button("🚀 Submit Question", use_container_width=True, type="primary")

with voice_tab:
    st.markdown("<h3 class='sub-header'>🎙️ Record your question</h3>", unsafe_allow_html=True)

    audio_value = st.audio_input("Record or upload audio", key="voice_audio")
    if audio_value:
        audio_bytes = audio_value.getvalue()
        audio_hash = md5(audio_bytes).hexdigest()

        
        if st.session_state.last_audio_hash != audio_hash:
            st.session_state.last_audio_hash = audio_hash

            
            if audio_value.type != "audio/wav":
                st.error(f"Unsupported audio type: {audio_value.type}. Please use a browser that records WAV (try Chrome/Edge).")
            else:
                tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                try:
                    tmpfile.write(audio_bytes)
                    tmpfile.flush()
                    with st.spinner("Transcribing..."):
                        try:
                            transcribed = transcribe(tmpfile.name)
                        except Exception as e:
                            transcribed = ""
                            st.error(f"Transcription error: {e}")
                finally:
                    try:
                        os.unlink(tmpfile.name)
                    except:
                        pass

                # Auto-submit after transcription
                if transcribed and transcribed.strip():
                    q = transcribed.strip()
                    st.session_state.pending_question = q
                    st.session_state.trigger_response = True
                    if q not in st.session_state.chat_history:
                        st.session_state.chat_history.append(q)
                    st.rerun()
        else:
            st.caption("Audio already processed. Record again to ask another question.")

    voice_submitted = st.button("🚀 Submit Question", key="voice_submit", use_container_width=True)

if submitted or voice_submitted:
    if not st.session_state.typed_q.strip():
        st.warning("Please enter or record a question first.")
    else:
        st.session_state.pending_question = st.session_state.typed_q.strip()
        st.session_state.trigger_response = True
        if st.session_state.pending_question not in st.session_state.chat_history:
            st.session_state.chat_history.append(st.session_state.pending_question)


if st.session_state.trigger_response and st.session_state.pending_question:
    question = st.session_state.pending_question

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>AI Response</h3>", unsafe_allow_html=True)

    with st.spinner("Thinking..."):
        answer = call_llm(question)

    st.markdown(f"<div class='highlight ai-response'>{answer}</div>", unsafe_allow_html=True)

    # Clean up previous audio file
    if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
        try:
            os.remove(st.session_state.current_audio)
        except:
            pass

    # Generate new audio
    with st.spinner("Generating audio..."):
        mp3_file = text(answer)  # keep API as-is
        st.session_state.current_audio = mp3_file
        st.session_state.audio_files.append(mp3_file)

    st.markdown("<h3 class='sub-header'>🔊 Audio Response</h3>", unsafe_allow_html=True)
    st.audio(mp3_file, format="audio/mp3", autoplay=True)
    st.markdown("</div>", unsafe_allow_html=True)

    dl_col1, dl_col2 = st.columns([1.2, 2.8])
    
    with open(mp3_file, "rb") as file:
        st.download_button(
            label="📥 Download Audio",
            data=file,
            file_name="interview_response.mp3",
            mime="audio/mp3",
            use_container_width=True
        )


    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.trigger_response = False
    st.session_state.pending_question = None


