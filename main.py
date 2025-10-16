from twilio.rest import Client
from dotenv import load_dotenv
import os, csv, time, requests
from requests.auth import HTTPBasicAuth
from twilio.base.exceptions import TwilioRestException

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# -----------------------------
# Make AI Call and Auto-Transcribe
# -----------------------------
def make_ai_call(to_number, name, message="Please speak after the beep.",
                 poll_timeout=240, poll_every=5):
    # import inside to avoid circular import
    from transcribe import transcribe_dual_or_mono as transcribe_audio
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        # ✅ Clean TwiML: say -> (optional short pause) -> record WITH BEEP
        # NOTE: No external OGG. No action/method (no webhook needed).
        twiml = f"""
<Response>
  <Say>Hello {name}! {message}</Say>
  <Pause length="1"/>
  <Record
      maxLength="30"
      timeout="3"
      playBeep="true"
      trim="trim-silence"
      recordingTrack="both"
      recordingChannels="dual"
  />
  <Say>Thank you! Recording finished.</Say>
</Response>
""".strip()

        # 1) Place the call
        call = client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=FROM_NUMBER,
            record=True,
            recording_channels="dual",
            recording_track="both"
        )
        print(f"📞 Call initiated to {name} ({to_number}), SID: {call.sid}")

        # 2) Wait for a recording to appear
        waited = 0
        selected = None
        print("⏳ Waiting for recording to appear...")
        while waited < poll_timeout:
            recs = client.recordings.list(call_sid=call.sid)
            if recs:
                selected = max(recs, key=lambda r: (int(r.duration) if r.duration else 0))
                break
            time.sleep(poll_every)
            waited += poll_every

        if not selected:
            print(f"⚠️ No recording found for {to_number} (call SID {call.sid}) after waiting {poll_timeout}s.")
            return

        # 3) Wait until Twilio finishes processing
        print("⏳ Waiting for recording to complete processing...")
        waited = 0
        while waited < poll_timeout:
            rec = client.recordings(selected.sid).fetch()
            if getattr(rec, "status", None) == "completed":
                break
            time.sleep(poll_every)
            waited += poll_every

        # 4) Download media (retry .mp3 then .wav)
        def try_download(recording_sid: str, retries: int = 12, backoff_sec: float = 3.0):
            import requests as rq
            attempts = 0
            base_uri = client.recordings(recording_sid).fetch().uri
            while attempts < retries:
                try:
                    for ext in (".mp3", ".wav"):
                        url = f"https://api.twilio.com{base_uri.replace('.json', ext)}"
                        r = rq.get(url, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN), timeout=60)
                        if r.status_code == 200 and r.content:
                            return r.content, ext
                    attempts += 1
                    print(f"   ↻ Media not ready yet (attempt {attempts}/{retries})...")
                    time.sleep(backoff_sec)
                except Exception:
                    attempts += 1
                    time.sleep(backoff_sec)
            return None, None

        media, ext = try_download(selected.sid)
        if not media:
            print(f"❌ Failed to download recording for {to_number} after repeated retries.")
            return

        # 5) Save audio and transcribe
        safe_name = (name or "unknown").replace(" ", "_")
        audio_file = f"recording_{safe_name}_{call.sid}{ext}"
        with open(audio_file, "wb") as f:
            f.write(media)
        print(f"✅ Recording saved: {audio_file}  (duration: {selected.duration or 'unknown'}s)")

        transcribe_audio(audio_file)

    except TwilioRestException as tre:
        print(f"⚠️ Twilio error for {name} ({to_number}): {tre}. Skipping.")
    except Exception as e:
        print(f"⚠️ Unexpected error for {name} ({to_number}): {e}. Skipping.")

# -----------------------------
# Load contacts from CSV
# -----------------------------
def get_contacts_from_csv(filename):
    contacts = []
    if not os.path.exists(filename):
        print("❌ contacts.csv not found in project folder.")
        return contacts
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = (row.get("NAME") or "").strip()
            phone = (row.get("PHONE") or "").strip()
            if phone.startswith('+') and phone[1:].isdigit():
                contacts.append((name or "unknown", phone))
            else:
                print(f"Skipping invalid phone format in CSV: {phone} (row name: {name})")
    return contacts

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    contacts = get_contacts_from_csv("contacts.csv")
    print(f"📋 Found {len(contacts)} contacts.")
    for name, number in contacts:
        print(f"--> Attempting call to {name} ({number})")
        make_ai_call(number, name)
    print("✅ All call attempts finished.")
