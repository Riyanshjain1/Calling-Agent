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

