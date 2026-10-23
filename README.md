# 🩺 Scribeo

**A bilingual AI Clinical Scribe for Urdu-English conversations.**

Scribeo converts mixed Urdu-English doctor-patient audio into structured English SOAP notes, saving doctors hours of administrative work.

## 🚀 Live Demo
[Click here to try the live app](https://scribeo.streamlit.app)

## ✨ Features
*   **Bilingual Transcription:** Uses Whisper (via Groq) to accurately transcribe mixed Urdu-English audio.
*   **SOAP Note Generation:** Uses Llama-3 (via Groq) to structure the transcript into Subjective, Objective, Assessment, and Plan.
*   **Editable UI:** Doctors can review and edit the AI's draft before saving.
*   **Smart Safety Check:** The app detects if the audio doesn't contain a medical conversation and alerts the user instead of hallucinating.

## 🧠 Engineering Highlights
*   Built with **Python**, **Streamlit**, and **Groq API**.
*   Implemented a custom Regex parser to handle LLM formatting hallucinations (ensuring text never gets lost).
*   Configured Linux system dependencies (`packages.txt`) to run audio processing in a cloud environment.
*   Deployed 100% free using Streamlit Community Cloud.
