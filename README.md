# 🩺 Scribeo

**An end-to-end AI Clinical Scribe and Billing Assistant.**

Scribeo converts Urdu-English doctor-patient conversations into structured English SOAP notes and automatically generates accurate ICD-10 and CPT billing codes.

## 🚀 Live Demo
[Click here to try the live app](https://scribeo.streamlit.app)

## ✨ Features
*   **Bilingual Transcription:** Uses Whisper (via Groq) to flawlessly transcribe mixed Urdu-English audio.
*   **SOAP Note Generation:** Uses Llama-3 (via Groq) to structure the transcript into Subjective, Objective, Assessment, and Plan.
*   **Editable UI:** Doctors can edit the AI's draft before downloading.
*   **Auto-Billing (v2):** Automatically analyzes the clinical note to suggest ICD-10 diagnosis codes and CPT procedure codes, saving clinics time and preventing revenue loss.

## 🧠 Engineering Highlights
*   Built with **Python**, **Streamlit**, and **Groq API**.
*   Implemented a custom Regex parser to handle LLM formatting hallucinations.
*   Configured Linux system dependencies (`packages.txt`) to run audio processing in a cloud environment.
*   Deployed 100% free using Streamlit Community Cloud.
