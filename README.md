# 📞 AI Calling Agent

> An AI-powered Python calling system that reads contacts from a CSV file, places outbound calls using **Twilio**, records them, and transcribes the conversation into text.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Twilio](https://img.shields.io/badge/Twilio-Voice%20API-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🧠 Overview

The **AI Calling Agent** is a Python-based automation tool designed to simulate a voice calling assistant.  
It reads phone numbers from a CSV file, places calls automatically using Twilio’s **Programmable Voice API**, records each call, and generates text transcripts from the audio files.

This project demonstrates the integration of **Python**, **Twilio Voice API**, and **Speech-to-Text** systems (like Whisper or SpeechRecognition).

---

## ✨ Features

- 📂 Reads user data (name, phone) from `contacts.csv`
- 📞 Places automated outbound calls using **Twilio Programmable Voice**
- 🗣️ Speaks customizable messages using `<Say>` TwiML
- 🎧 Records the entire conversation
- 🧾 Converts audio recordings into text transcripts automatically
- 📊 Saves transcripts and call details locally
- ⚙️ Secure environment variable configuration (`.env` support)

---

## 🧱 Project Structure

Calling-Agent/
├── main.py # Handles automated calling logic
├── transcribe.py # Converts recorded audio to text
├── contacts.csv # Contact list with phone numbers
├── .gitignore # Ignored files and folders
├── requirements.txt # Dependencies list
└── README.md # Documentation (this file)

---

## ⚙️ Setup & Installation

###  Clone the Repository
```bash
git clone https://github.com/<your-username>/AI-Calling-Agent.git
cd AI-Calling-Agent


###  Clone the Repository
```bash
git clone https://github.com/<your-username>/AI-Calling-Agent.git
cd AI-Calling-Agent


###  Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

### Install Dependencies
pip install -r requirements.txt


### Create a .env File
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1XXXXXXXXXX

###🧾 Prepare Your CSV File

NAME,PHONE
User1,+919876543210
User2,+14155552671

### Run the Calling Agent
python main.py

### 🧩 Example Output
✅ Loaded 2 contacts from contacts.csv
📞 Calling Harshit at +919876543210
🎧 Recording saved to recordings/Harshit.wav
🧾 Transcript saved to transcripts/Harshit.txt


### Transcript Sample
Caller: Hello Harshit, this is an automated confirmation call.
Harshit: Yes, I can hear you clearly.
Caller: Thank you. Have a great day!


### 🧩 Requirements
pip install -r requirements.txt

### 🧩 Example Output
✅ Loaded 2 contacts from contacts.csv
📞 Calling User1 at +9198769999
🎧 Recording saved to recordings/User.wav
🧾 Transcript saved to transcripts/Harshit.txt


### Transcript Sample
Caller: Hello User1, this is an automated confirmation call.
User1: Yes, I can hear you clearly.
Caller: Thank you. Have a great day!
