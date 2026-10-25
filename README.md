# A.E.G.I.S.
## **Autonomous Edge-Guardian & Identity Shield**
> *“Invisible when you are safe. Indomitable when you are not.”*

---

## 💡 What is A.E.G.I.S.?
* **A.E.G.I.S.** stands for **Autonomous Edge-Guardian & Identity Shield**.
* The word *"Aegis"* historically refers to an impenetrable, protective shield.
* It is a **zero-trust, privacy-first personal safety ecosystem** designed to protect women across both **physical travel** (street, cab, bus) and **digital environments** (online photo leaks, deepfakes, stalking).

---

## 🚨 The Problem A.E.G.I.S. Solves

Traditional safety apps fail in real-world emergencies for three critical reasons:
1. **Victims cannot tap buttons in panic:** If someone grabs your hand or snatches your phone, you cannot unlock your screen, find an app, and tap an "SOS" button.
2. **Surveillance & Stalking Risks:** Existing apps track your live GPS coordinates 24/7 on central servers. This allows abusive partners or hackers to spy on your exact room and everyday movements.
3. **Ignoring Digital Threats:** Harassment today is hybrid—stalkers use hidden Bluetooth tags (AirTags) to trail cabs, or use non-consensual photo leaks and AI deepfakes for online extortion.

---

## 🛡️ How A.E.G.I.S. Works (5 Core Features)

1. **Secret Calculator Disguise (Chameleon Shell)**
   * On your home screen, the app looks and works like an everyday calculator.
   * Typing **`9999 =`** unlocks the secret Safety App.
   * If an attacker forces you to unlock your phone, typing **`5555 =`** opens a fake **Daily Expenses** screen while **silently calling Police 112** with your real GPS location!

2. **Hands-Free Scream & Voice Listener (On-Device Edge-AI)**
   * You don't need to touch your phone. The app listens locally on the phone's chip.
   * If you scream or say *"Help"*, it automatically triggers an emergency alert.
   * **100% Private:** Zero audio is ever uploaded to the cloud or saved.

3. **Private Safe Route (Zero-Tracking Geofence)**
   * Uses cryptographic Zero-Knowledge Proofs (ZK-SNARKs) to confirm to your family that you are safely on your daily route.
   * **Your exact latitude, longitude, and room location stay private** and only unlock if an actual emergency occurs or if your travel timer expires.

4. **Stop Leaked Photos & AI Deepfakes (Digital Shield)**
   * Uses 64-bit perceptual image hashing (pHash) to detect unconsented photo re-uploads and synthetic deepfakes.
   * Generates a formal legal demand requiring **mandatory 24-hour removal** under Section 66E/67 of the IT Act and Rule 3(2)(b) of the IT Rules, 2021.

5. **Find Hidden Trackers & Masked Numbers**
   * **Bluetooth Tracker Radar:** Scans for unknown Apple AirTags or GPS tags following your auto-rickshaw or bus.
   * **Disposable Numbers:** Creates temporary relay numbers for Swiggy, Zepto, Ola, or Uber so delivery persons and cab drivers never get your real phone number.

---

## 🚀 Quickstart Guide

### 1. Clone & Install:
```bash
git clone https://github.com/rithikarvrs/aegis-women-safety.git
cd aegis-women-safety
pip install fastapi uvicorn websockets
```

### 2. Run the Server:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8080
```

### 3. Open in Browser:
Open **[http://127.0.0.1:8080](http://127.0.0.1:8080)** in your browser.

---

## 🧪 Run Automated Verification Tests
```bash
python test_suite.py
```

---

## 🎯 Demo Cheat-Sheet

| Feature | Key / Action | What It Does |
| :--- | :--- | :--- |
| **Normal Calculator** | Standard math (`25 * 4 =`) | Works as an everyday benign calculator. |
| **Secret Safety App** | Type **`9999 =`** (or `1234 =`) | Unlocks the hidden **Aegis Safety Shield**. |
| **Emergency Fake PIN** | Type **`5555 =`** (or `0000 =`) | Renders a decoy daily expense budget while secretly dispatching real GPS to Police 112. |
| **Scream & Voice Trigger** | Click **`🗣️ Say "Help"`** or **`🚨 Scream`** | On-device acoustic classifier detects distress and unlocks emergency coordinates. |
| **Real GPS Location** | Click **`📍 Detect My Real GPS Location`** | Uses device GPS to center map directly on user's live location with high accuracy. |
| **Safe Route Protection** | Click **`Walk Along Route`** | Generates 128-byte mathematical proofs confirming safety without disclosing exact coordinates. |
| **Stop Leaked Photos** | Click **`Scan`** under Media Shield | Evaluates 64-bit perceptual hash and generates formal 24-hour removal notice under IT Act Rule 3(2)(b). |
| **Find Hidden Trackers** | Click **`Detect Trailing Tracker`** | Analyzes background RF signals to detect unknown AirTags trailing the user. |
| **Police 112 Dispatch** | Click **`Dispatch Police 112 / PCR Van`** | Routes nearest response unit to decrypted GPS and sends silent haptic heartbeat to victim. |

---

## 📂 Project Structure

```
aegis-women-safety/
├── app.py                 # FastAPI server with WebSockets & Emergency 112 dispatch
├── crypto_engine.py       # Cryptographic engine (Shamir 3-of-5, ZK Geofence, pHash, BLE, Merkle)
├── test_suite.py          # Automated verification test suite
├── static/
│   └── index.html         # Interactive dual-screen application (Phone + Police Control Room)
└── README.md              # Project documentation and purpose guide
```
