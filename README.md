# AEGIS: Zero-Trust Safety & Sovereign Fabric
> **“Invisible when you’re safe. Indomitable when you’re not.”**

AEGIS is an on-device personal security ecosystem that merges **Edge-AI acoustic distress detection**, **Zero-Knowledge (ZK) safe-transit proofs**, **Shamir's Secret Sharing threshold escrow**, and a **Digital Sovereign Media Shield**.

---

## 🚀 Live Working Model Quickstart

The live interactive application is currently running at:
👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

### To Run / Restart Manually:
```powershell
cd C:\Users\murug\.gemini\antigravity\scratch\aegis-safety-protocol
python -m uvicorn app:app --host 127.0.0.1 --port 8080
```

### To Run the Verification Test Suite:
```powershell
python test_suite.py
```

---

## 🎯 Hackathon Judge Demo Cheat-Sheet

| Interaction | Action | What Happens Cryptographically |
| :--- | :--- | :--- |
| **Normal Calculator** | Enter standard math (`42 * 5 =`) | Operates as a benign scientific calculator (`CalcPro+`). |
| **Chameleon Unlock** | Type `1842.50 =` on the keypad | Triggers biometric animation and unfolds the hidden **AEGIS Command Console**. |
| **Duress Hostage PIN** | Type `0000 =` on the keypad | Renders a decoy financial budget for the attacker while silently firing a **Level-3 Hostage Emergency** to CAD with raw GPS coordinates. |
| **Whisper Safe-Word** | Click `🗣️ "Lemons"` or toggle real mic | Simulated on-device Gemini Nano acoustic classifier detects sub-vocalized safe word; reconstructs coordinates via 3-of-5 Shamir threshold. |
| **Acoustic Scream** | Click `🚨 Scream` or make loud noise | Triggers high-G acoustic stress pipeline and alerts police CAD. |
| **ZK Geofence Step** | Click `Step Along Route` | Generates 128-byte Groth16 proof: confirms safety inside corridor without revealing lat/lon coordinates. |
| **Media Takedown** | Click `Scan` in Digital Shield | Evaluates 64-bit pHash Hamming distance and drafts 18 U.S.C. § 2261A / DMCA cease-and-desist notice. |
| **BLE Stalker Sweep** | Click `Detect Trailing Tag` | Evaluates RSSI deltas across waypoints to detect rogue Apple AirTags. |
| **CAD Dispatch** | Click `Dispatch Unit #104` | Police CAD routes unit to decrypted GPS and sends silent haptic heartbeat to victim. |

---

## 📂 Project Directory Structure

```
aegis-safety-protocol/
├── app.py                 # FastAPI microservice with WebSockets & REST endpoints
├── crypto_engine.py       # Mathematical primitives (Shamir 3-of-5, ZK Geofence, pHash, BLE, Merkle)
├── test_suite.py          # Automated verification test suite
├── static/
│   └── index.html         # Interactive dual-screen client (Chameleon phone + Police CAD)
└── README.md              # Documentation & pitch guide
```
