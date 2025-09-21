# AI Interview VoiceBot

An interactive **voice-based interview assistant** built for the **100x AI Agent Team assessment**.
This web app allows users to **ask interview-style questions by voice or text** and hear responses spoken back, as if from the candidate (**Srinivas Peethala**).

The bot uses:

* **Speech-to-Text (STT)** → Converts user's voice into text.
* **LLM (Groq's LLaMA-3.3-70B)** → Generates interview-style answers in first person.
* **Text-to-Speech (TTS)** → Speaks responses back to the user.
* **Streamlit Web App** → Simple, universal interface (no coding required).

## Features

* Voice input (record directly in browser)
* Text input option for non-microphone users
* Spoken responses (auto-play audio)
* Realistic candidate persona with professional interview tone
* Fully web-based — no installations or API keys needed from users

## Project Structure

```
voicebot/
├── app.py           # Main Streamlit web app
├── requirements.txt # Dependencies
├── README.md        # Documentation
└── utils/           # Utility modules
    ├── audio.py     # Handles recording and playback of audio
    ├── llm.py       # Connects to Groq LLaMA-3.3-70B for respons
    └── speech.py    # Speech-to-Text and Text-to-Speech functions
```

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/srinivasp174/voicebot.git
cd voicebot
```

### 2. Create virtual environment (recommended)

```bash
python -m venv myenv
source myenv/bin/activate   # On Linux/Mac
myenv\Scripts\activate      # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

You will see a local URL in the terminal, e.g.:

```
Local URL: http://localhost:8502
```

Open it in your browser to test the bot.

## How It Works

### 1. Recording & Playback (`audio.py`)

* Detects available microphones
* Records audio input
* Converts saved `.wav` files into base64 for browser playback

### 2. Speech-to-Text & Text-to-Speech (`speech.py`)

* **STT** → Uses Google Speech Recognition to transcribe user audio
* **TTS** → Uses `gTTS` (Google Text-to-Speech) to generate `.mp3` answers

### 3. LLM Response (`llm.py`)

* Connects to **Groq API** with **LLaMA-3.3-70B**
* Persona: **Srinivas Peethala (candidate)**
* Responds in 2–4 sentences, confident and professional

### 4. Web Interface (`app.py`)

* Built with **Streamlit**
* Simple buttons for recording & playing responses
* Works on any browser, no setup required for end-users

## Example Questions

Try asking:

* "What should we know about your life story in a few sentences?"
* "What's your #1 superpower?"
* "What are the top 3 areas you'd like to grow in?"
* "What misconception do your coworkers have about you?"
* "How do you push your boundaries and limits?"

## Deployment

For universal access, deploy on **Streamlit Community Cloud** (free).

1. Push your repo to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect GitHub → Select repo → Deploy
4. Share the public URL in your submission
