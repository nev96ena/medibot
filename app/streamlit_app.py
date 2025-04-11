import streamlit as st
import time
import os
import tempfile
import whisper
from audio_recorder_streamlit import audio_recorder
from agent_setup import get_compiled_graph_app
from gtts import gTTS
from io import BytesIO
import base64
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="MediBot: Smart Health Assistant", layout="centered")

@st.cache_resource

# Load whisper
def load_whisper_model(model_size="base"):
    try:
        is_streamlit_cloud = os.getenv('STREAMLIT_SERVER_RUNNING_ON') == 'streamlitcloud'
        effective_model_size = 'tiny' if is_streamlit_cloud and model_size in ['base', 'small'] else model_size
        model = whisper.load_model(effective_model_size)
        return model
    except Exception as e:
        st.error(f"Fatal error loading Whisper model: {e}")
        st.stop()

whisper_model = load_whisper_model("base")

def transcribe_audio_local(audio_bytes, model):
    if not audio_bytes or not model:
        return None
    tmp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
            tmp_audio_file.write(audio_bytes)
            tmp_audio_path = tmp_audio_file.name
        result = model.transcribe(tmp_audio_path, fp16=False)
        transcribed_text = result["text"]
        os.remove(tmp_audio_path)
        return transcribed_text.strip()
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        if tmp_audio_path and os.path.exists(tmp_audio_path):
            os.remove(tmp_audio_path)
        return None

def text_to_audio_gtts(text_to_speak, lang='en'):
    if not text_to_speak: return None
    if not any(c.isalnum() for c in text_to_speak): return None
    try:
        tts = gTTS(text=text_to_speak, lang=lang, slow=False)
        audio_fp = BytesIO(); tts.write_to_fp(audio_fp); audio_fp.seek(0)
        return audio_fp.read()
    except Exception as e:
        st.error(f"Error during gTTS generation: {e}")
        return None

# Title 
st.markdown("""
    <h1 style='text-align: center; color: white;'>🩺 MediBot: Smart Health Assistant</h1>
""", unsafe_allow_html=True)

# Session state for messages 
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask your question via text or microphone."}
    ]

if st.session_state.get("audio_playing"):
    st.components.v1.html("""
        <script>
            const audios = window.parent.document.querySelectorAll('audio');
            audios.forEach(audio => {
                if (!audio.paused) { audio.pause(); }
            });
        </script>
    """, height=0)
    st.session_state.audio_playing = False

message_container = st.container()
with message_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

transcribed_text = None

# Chat + mic
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.chat_input("Type your question here...")
with col2:
    audio_bytes = audio_recorder(text="", icon_size="2x", key="audio_recorder_key")

if audio_bytes:
    if st.session_state.get("audio_playing"):
         st.session_state.audio_playing = True

    with st.spinner("Transcribing your audio..."):
        transcribed_text = transcribe_audio_local(audio_bytes, whisper_model)
    if transcribed_text:
        st.write(f"Transcribed: *{transcribed_text}*")
    else:
        st.warning("Transcription failed.")
    prompt = transcribed_text
else:
    prompt = user_input

# Q&A
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        audio_html_placeholder = st.empty()
        audio_response_bytes = None

        # thinking_msg = "Thinking..."
        # message_placeholder.markdown(f"*{thinking_msg}*")

        with st.spinner("Thinking..."):
            try:
                agent_app = get_compiled_graph_app()
                if agent_app:

                    history_for_agent_dicts = st.session_state.messages[:-1]
                    formatted_history_for_agent = []
                    for msg in history_for_agent_dicts:
                        if msg["role"] == "user":
                            formatted_history_for_agent.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            formatted_history_for_agent.append(AIMessage(content=msg["content"]))

                    inputs = {
                        "question": prompt,
                        "chat_history": formatted_history_for_agent
                    }

                    response_state = agent_app.invoke(inputs)
                    full_response = response_state.get('final_answer', 'Sorry, no answer was found.')
                else:
                    full_response = "Agent could not be initialized."
                    st.error(full_response)

                if full_response:
                    with st.spinner("Generating audio..."):
                        audio_response_bytes = text_to_audio_gtts(full_response, lang='en')

            except Exception as e:
                full_response = f"Critical error: {e}"
                st.error(full_response)
                import traceback
                traceback.print_exc()

        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        if audio_response_bytes:
            try:
                b64 = base64.b64encode(audio_response_bytes).decode()
                player_id = f"audio_player_{len(st.session_state.messages)}"
                audio_html = f"""
                    <audio id="{player_id}" controls autoplay style="width: 100%; min-height: 50px;">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        Your browser does not support the audio element.
                    </audio>
                    """
                st.components.v1.html(audio_html, height=100)
                st.session_state.audio_playing = True
            except Exception as html_err:
                 st.error(f"Failed to generate audio player: {html_err}")
                 st.session_state.audio_playing = False
