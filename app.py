import streamlit as st
import numpy as np
import soundfile as sf
import os
import io
import re
from groq import Groq

st.set_page_config(page_title="Scribeo", page_icon="🩺", layout="wide")

# --- GROQ CLIENT ---
@st.cache_resource
def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found.")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

system_prompt = """You are a medical scribe assistant.
Convert a doctor-patient transcript into a structured SOAP note.
Rules:
- Output ONLY the SOAP note.
- Preserve all medical facts: symptoms, durations, dosages, drug names.
- Correct obvious misspellings of drug names.
- If a section has no information, write "Not documented."
Format exactly like this:
SUBJECTIVE: ...
OBJECTIVE: ...
ASSESSMENT: ...
PLAN: ..."""

# --- BULLETPROOF PARSER ---
def parse_soap(text):
    sections = {"S": "", "O": "", "A": "", "P": ""}
    
    subj_match = re.search(r"SUBJECTIVE[:\*\s]*(.*?)(?=OBJECTIVE|ASSESSMENT|PLAN|$)", text, re.DOTALL | re.IGNORECASE)
    if subj_match: sections["S"] = subj_match.group(1).strip()
    
    obj_match = re.search(r"OBJECTIVE[:\*\s]*(.*?)(?=SUBJECTIVE|ASSESSMENT|PLAN|$)", text, re.DOTALL | re.IGNORECASE)
    if obj_match: sections["O"] = obj_match.group(1).strip()
    
    assess_match = re.search(r"ASSESSMENT[:\*\s]*(.*?)(?=SUBJECTIVE|OBJECTIVE|PLAN|$)", text, re.DOTALL | re.IGNORECASE)
    if assess_match: sections["A"] = assess_match.group(1).strip()
    
    plan_match = re.search(r"PLAN[:\*\s]*(.*?)(?=SUBJECTIVE|OBJECTIVE|ASSESSMENT|$)", text, re.DOTALL | re.IGNORECASE)
    if plan_match: sections["P"] = plan_match.group(1).strip()
    
    return sections

# --- SESSION STATE INITIALIZATION ---
if "sections" not in st.session_state:
    st.session_state.sections = None
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

# --- UI ---
st.title("🩺 Scribeo")
st.write("Convert Urdu-English doctor-patient conversations into structured medical notes.")

col1, col2 = st.columns(2)
with col1:
    audio_recording = st.audio_input("Record Audio")
with col2:
    uploaded_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a"])

if st.button("⚡ Generate Note", use_container_width=True):
    audio_data = uploaded_file.read() if uploaded_file else (audio_recording.read() if audio_recording else None)
    
    if audio_data is None:
        st.warning("Please upload or record audio.")
    else:
        with st.spinner("Processing audio and generating note..."):
            try:
                try:
                    audio_array, samplerate = sf.read(io.BytesIO(audio_data))
                except:
                    temp_in = "/tmp/in_audio"
                    with open(temp_in, "wb") as f: f.write(audio_data)
                    audio_array, samplerate = sf.read(temp_in)
                
                if len(audio_array.shape) > 1: audio_array = audio_array.mean(axis=1)
                temp_wav = "/tmp/out.wav"
                sf.write(temp_wav, audio_array, samplerate)
                
                with open(temp_wav, "rb") as f:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", f.read()),
                        model="whisper-large-v3-turbo",
                        language="ur",
                        response_format="text"
                    )
                transcript = transcription if isinstance(transcription, str) else transcription.text
                
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Convert: {transcript}"}],
                    temperature=0.1
                )
                soap = response.choices[0].message.content
                sections = parse_soap(soap)
                
                st.session_state.transcript = transcript
                st.session_state.sections = sections
                st.rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# --- DISPLAY RESULTS ---
if st.session_state.sections is not None:
    s = st.session_state.sections
    
    total_words = len((s.get("S", "") + s.get("O", "") + s.get("A", "") + s.get("P", "")).split())
    
    if total_words < 3:
        st.warning("⚠️ The AI could not find a medical conversation in this audio. Please upload a real doctor-patient audio file.")
    else:
        st.success("Note generated successfully!")
        st.subheader("📋 Medical Note")
        
        st.markdown("**Subjective**")
        subj = st.text_area("subj_key", value=s.get("S", ""), height=100, label_visibility="collapsed")
        
        st.markdown("**Objective**")
        obj = st.text_area("obj_key", value=s.get("O", ""), height=100, label_visibility="collapsed")
        
        st.markdown("**Assessment**")
        assess = st.text_area("assess_key", value=s.get("A", ""), height=100, label_visibility="collapsed")
        
        st.markdown("**Plan**")
        plan = st.text_area("plan_key", value=s.get("P", ""), height=100, label_visibility="collapsed")
        
        note_text = f"SUBJECTIVE:\n{subj}\n\nOBJECTIVE:\n{obj}\n\nASSESSMENT:\n{assess}\n\nPLAN:\n{plan}"
        st.download_button("⬇️ Download Note", note_text, file_name="scribeo_note.txt")
        
    with st.expander("📝 View Raw Transcript"):
        st.write(st.session_state.transcript)
