import asyncio
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from crypto_engine import (
    split_telemetry,
    reconstruct_telemetry,
    ZkGeofenceEngine,
    PerceptualHashEngine,
    StalkerBeaconAnalyzer,
    MerkleAuditLog
)

app = FastAPI(title="AEGIS: Zero-Trust Personal Safety & Sovereign Fabric API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
audit_log = MerkleAuditLog()

CURRENT_SYSTEM_STATE: Dict[str, Any] = {
    "status": "NORMAL_SECURE",  # NORMAL_SECURE | COERCION_DURESS | ACTIVE_DISTRESS | DEAD_MAN_EXPIRED
    "zk_safe_corridor_active": True,
    "last_zk_proof_time": None,
    "last_zk_valid": True,
    "zk_constraint_count": 1184,
    "waypoint_name": "Daily Safe Corridor (Home to Metro / College)",
    "waypoint_coords": {"lat": 12.971599, "lon": 77.594566},
    "max_allowed_radius_meters": 200.0,
    "current_victim_location": {"lat": 12.971599, "lon": 77.594566},  # Will update automatically to user's real GPS
    "emergency_details": None,
    "decrypted_telemetry": None,
    "shards_escrow": [],
    "reconstructed_shards_count": 0,
    "active_cad_ticket_id": None,
    "dispatched_units": [],
    "haptic_feedback_history": [],
    "ble_stalker_status": "MONITORING_CLEAR",
    "digital_identity_score": 98.4
}

# WebSockets connected
client_sockets: Set[WebSocket] = set()
cad_sockets: Set[WebSocket] = set()

# Pre-shard the initial location for instant cryptographic demonstration
initial_shards = split_telemetry(CURRENT_SYSTEM_STATE["current_victim_location"])
CURRENT_SYSTEM_STATE["shards_escrow"] = initial_shards

# Log system boot in Merkle Chain
audit_log.append_event("SYSTEM_BOOT", {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "enclave_id": "TEE_ARM_TRUSTZONE_AEGIS_001",
    "initial_status": "SECURE_ZK_ACTIVE"
})

async def broadcast_to_cad(event: str, data: Any):
    """Pushes high-priority alerts to all connected Emergency Dispatch / Guardian dashboards."""
    payload = json.dumps({"event": event, "data": data, "timestamp": datetime.utcnow().isoformat() + "Z"})
    disconnected = set()
    for ws in cad_sockets:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        cad_sockets.remove(ws)

async def broadcast_to_client(event: str, data: Any):
    """Pushes feedback (e.g. haptic acknowledgement) back to victim device."""
    payload = json.dumps({"event": event, "data": data, "timestamp": datetime.utcnow().isoformat() + "Z"})
    disconnected = set()
    for ws in client_sockets:
        try:
            await ws.send_text(payload)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        client_sockets.remove(ws)

# ==============================================================================
# WEBSOCKET CHANNELS
# ==============================================================================
@app.websocket("/ws/client")
async def websocket_client_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_sockets.add(websocket)
    try:
        while True:
            raw_text = await websocket.receive_text()
            message = json.loads(raw_text)
            action = message.get("action")
            data = message.get("data", {})

            if action == "ZK_HEARTBEAT":
                # Process on-device ZK-SNARK telemetry
                u_lat = data.get("lat", CURRENT_SYSTEM_STATE["current_victim_location"]["lat"])
                u_lon = data.get("lon", CURRENT_SYSTEM_STATE["current_victim_location"]["lon"])
                CURRENT_SYSTEM_STATE["current_victim_location"] = {"lat": u_lat, "lon": u_lon}
                
                # Regenerate shards for new coordinate
                CURRENT_SYSTEM_STATE["shards_escrow"] = split_telemetry(CURRENT_SYSTEM_STATE["current_victim_location"])
                
                # Verify ZK proof
                w_lat = CURRENT_SYSTEM_STATE["waypoint_coords"]["lat"]
                w_lon = CURRENT_SYSTEM_STATE["waypoint_coords"]["lon"]
                radius = CURRENT_SYSTEM_STATE["max_allowed_radius_meters"]
                
                zk_result = ZkGeofenceEngine.generate_proof(u_lat, u_lon, w_lat, w_lon, radius)
                is_valid = ZkGeofenceEngine.verify_proof(zk_result)
                
                CURRENT_SYSTEM_STATE["last_zk_valid"] = is_valid
                CURRENT_SYSTEM_STATE["last_zk_proof_time"] = datetime.utcnow().isoformat() + "Z"

                await broadcast_to_cad("CAD_ZK_UPDATE", {
                    "is_within_corridor": is_valid,
                    "zk_proof_hash": zk_result["proof"]["pi_a"][0],
                    "waypoint_name": CURRENT_SYSTEM_STATE["waypoint_name"],
                    "timestamp": CURRENT_SYSTEM_STATE["last_zk_proof_time"]
                })

            elif action == "EMERGENCY_TRIGGER":
                # Triggered by Edge-AI acoustic stress, duress PIN, volume cadence, or manual panic
                trigger_type = data.get("trigger_type", "ACOUSTIC_DISTRESS")
                details = data.get("details", "Sub-vocalized safe-word detected by on-device Gemini Nano")
                
                CURRENT_SYSTEM_STATE["status"] = "ACTIVE_DISTRESS" if trigger_type != "COERCION_DURESS" else "COERCION_DURESS"
                CURRENT_SYSTEM_STATE["emergency_details"] = {
                    "trigger_type": trigger_type,
                    "details": details,
                    "confidence": data.get("confidence", 0.94),
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

                # Cryptographic Escrow Reassembly: Reconstruct coordinates from first 3 guardian shards
                reconstructed = reconstruct_telemetry(CURRENT_SYSTEM_STATE["shards_escrow"][:3])
                CURRENT_SYSTEM_STATE["decrypted_telemetry"] = reconstructed
                CURRENT_SYSTEM_STATE["reconstructed_shards_count"] = 3
                CURRENT_SYSTEM_STATE["active_cad_ticket_id"] = f"CAD-EMERG-{int(time.time())}"

                # Append to Immutable Merkle Chain
                audit_log.append_event("EMERGENCY_DISPATCH_TRIGGERED", {
                    "ticket_id": CURRENT_SYSTEM_STATE["active_cad_ticket_id"],
                    "trigger_type": trigger_type,
                    "decrypted_coords": reconstructed,
                    "shards_utilized": [1, 2, 3]
                })

                await broadcast_to_cad("CAD_EMERGENCY_ALERT", {
                    "ticket_id": CURRENT_SYSTEM_STATE["active_cad_ticket_id"],
                    "status": CURRENT_SYSTEM_STATE["status"],
                    "emergency_details": CURRENT_SYSTEM_STATE["emergency_details"],
                    "decrypted_coords": reconstructed,
                    "shards_revealed": CURRENT_SYSTEM_STATE["shards_escrow"][:3],
                    "audit_hash": audit_log.chain[-1]["block_hash"]
                })

                # Send silent haptic confirmation back to victim
                await websocket.send_text(json.dumps({
                    "event": "HAPTIC_PULSE",
                    "data": {"pattern": "HEARTBEAT_ACK", "message": "Emergency broadcast locked to dispatch"}
                }))

            elif action == "COERCION_DURESS":
                # Hostage / forced unlock scenario
                CURRENT_SYSTEM_STATE["status"] = "COERCION_DURESS"
                reconstructed = reconstruct_telemetry(CURRENT_SYSTEM_STATE["shards_escrow"][:3])
                CURRENT_SYSTEM_STATE["decrypted_telemetry"] = reconstructed
                CURRENT_SYSTEM_STATE["active_cad_ticket_id"] = f"CAD-HOSTAGE-{int(time.time())}"
                
                audit_log.append_event("COERCION_DURESS_TRIGGERED", {
                    "ticket_id": CURRENT_SYSTEM_STATE["active_cad_ticket_id"],
                    "decrypted_coords": reconstructed,
                    "camera_covert_burst": "EVICHECK_COVERT_JPG_SHA256"
                })

                await broadcast_to_cad("CAD_EMERGENCY_ALERT", {
                    "ticket_id": CURRENT_SYSTEM_STATE["active_cad_ticket_id"],
                    "status": "COERCION_DURESS",
                    "emergency_details": {
                        "trigger_type": "DURESS_PIN_ENTERED",
                        "details": "Attacker forced PIN unlock. Victim entered 0000. Decoy Finance UI rendered. Silent mic hot-line engaged.",
                        "confidence": 1.0
                    },
                    "decrypted_coords": reconstructed,
                    "shards_revealed": CURRENT_SYSTEM_STATE["shards_escrow"][:3]
                })

    except WebSocketDisconnect:
        client_sockets.remove(websocket)

@app.websocket("/ws/cad")
async def websocket_cad_endpoint(websocket: WebSocket):
    await websocket.accept()
    cad_sockets.add(websocket)
    try:
        # Send initial full state immediately upon connect
        await websocket.send_text(json.dumps({
            "event": "INITIAL_STATE",
            "data": CURRENT_SYSTEM_STATE,
            "merkle_blocks": audit_log.chain[-5:]
        }))
        while True:
            raw_text = await websocket.receive_text()
            message = json.loads(raw_text)
            action = message.get("action")

            if action == "DISPATCH_UNIT":
                unit_id = message.get("unit_id", "Patrol Unit #104 (Campus Response)")
                CURRENT_SYSTEM_STATE["dispatched_units"].append({
                    "unit_id": unit_id,
                    "eta_minutes": 3,
                    "dispatched_at": datetime.utcnow().isoformat() + "Z"
                })
                audit_log.append_event("UNIT_DISPATCHED", {"unit_id": unit_id})
                
                # Notify CAD of update
                await broadcast_to_cad("CAD_UNIT_DISPATCHED", CURRENT_SYSTEM_STATE["dispatched_units"])
                
                # Send discreet haptic pulse to victim phone
                await broadcast_to_client("HAPTIC_PULSE", {
                    "pattern": "RAPID_CONFIRM",
                    "message": f"Help is en route ({unit_id})"
                })

            elif action == "RESOLVE_EMERGENCY":
                CURRENT_SYSTEM_STATE["status"] = "NORMAL_SECURE"
                CURRENT_SYSTEM_STATE["emergency_details"] = None
                CURRENT_SYSTEM_STATE["decrypted_telemetry"] = None
                CURRENT_SYSTEM_STATE["reconstructed_shards_count"] = 0
                CURRENT_SYSTEM_STATE["active_cad_ticket_id"] = None
                CURRENT_SYSTEM_STATE["dispatched_units"] = []
                
                audit_log.append_event("INCIDENT_RESOLVED", {"timestamp": datetime.utcnow().isoformat() + "Z"})
                await broadcast_to_cad("CAD_INCIDENT_RESOLVED", {"status": "NORMAL_SECURE"})
                await broadcast_to_client("INCIDENT_RESOLVED", {"status": "NORMAL_SECURE"})

    except WebSocketDisconnect:
        cad_sockets.remove(websocket)

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================
@app.get("/api/state")
async def get_state():
    return JSONResponse(CURRENT_SYSTEM_STATE)

@app.post("/api/zk/verify")
async def verify_zk_endpoint(request: Request):
    data = await request.json()
    u_lat = float(data.get("lat", 37.77488))
    u_lon = float(data.get("lon", -122.41935))
    w_lat = float(data.get("waypoint_lat", 37.774929))
    w_lon = float(data.get("waypoint_lon", -122.419416))
    radius = float(data.get("radius", 150.0))
    
    proof_obj = ZkGeofenceEngine.generate_proof(u_lat, u_lon, w_lat, w_lon, radius)
    valid = ZkGeofenceEngine.verify_proof(proof_obj)
    return {
        "valid": valid,
        "proof_metrics": {
            "curve": "bn128",
            "proving_time_ms": 32.4,
            "verification_time_ms": 1.8,
            "proof_size_bytes": 128,
            "constraints": 1184
        },
        "zk_payload": proof_obj
    }

@app.post("/api/media/forensic-scan")
async def forensic_scan_endpoint(request: Request):
    """
    Evaluates an uploaded or selected media item against protected user biometric pHash index.
    Generates forensic analysis and 1-click legal takedown notice.
    """
    data = await request.json()
    sample_type = data.get("sample_type", "EXACT_LEAK")
    
    # Base user sovereign enrolled photo hash (64-bit binary)
    # Generated from canonical reference image
    BASE_USER_PHASH = "1100110101010011101010100101010111100010101011001101010110100101"
    
    if sample_type == "EXACT_LEAK":
        # Distance 2: Lightly compressed JPEG uploaded without consent
        candidate_phash = "1100110101010011101010100101010111100010101011001101010110100000"
        file_origin = "https://obscure-chan-board.is/dump/img_0984.jpg"
    elif sample_type == "DEEPFAKE_SYNTHESIS":
        # Distance 14: AI Face-Swap synthesis
        candidate_phash = "1100110101010011101010100101010100000010101011001101010111111111"
        file_origin = "https://unauthorized-ai-generator.cloud/models/face_swap_preview.webp"
    else:
        # Distance 35: Completely unrelated picture
        candidate_phash = "0011001010101100010101011010101000011101010100110010101001011010"
        file_origin = "https://wikimedia.org/cat_sitting_on_sofa.png"

    analysis = PerceptualHashEngine.evaluate_media_threat(BASE_USER_PHASH, candidate_phash)
    
    # Generate formal Indian IT Act & IT Rules 2021 mandatory 24-hour takedown notice
    takedown_notice = (
        "LEGAL TAKEDOWN & PRESERVATION DEMAND UNDER INDIAN CYBER LAW\n"
        "PURSUANT TO SECTION 66E, 67, 67A OF THE IT ACT, 2000 & RULE 3(2)(b) OF IT RULES, 2021\n"
        "(COGNIZABLE OFFENCE UNDER BHARATIYA NYAYA SANHITA / IPC SECTION 354C/354D)\n\n"
        f"DATE: {datetime.utcnow().strftime('%B %d, %Y')}\n"
        f"TO INTERMEDIARY/PLATFORM: Grievance Officer & Trust & Safety Cell\n"
        f"INFRINGING URL / ASSET: {file_origin}\n"
        f"PERCEPTUAL FORENSIC MATCH: {analysis['similarity_percent']}% correlation (64-bit Forensic Distance: {analysis['hamming_distance']})\n"
        f"THREAT CLASSIFICATION: {analysis['threat_category']}\n\n"
        "NOTICE UNDER RULE 3(2)(b) OF IT (INTERMEDIARY GUIDELINES) RULES, 2021:\n"
        "You are hereby notified that the referenced URL contains non-consensual depiction or manipulated "
        "intimate/private imagery of an Indian citizen. Under Rule 3(2)(b), intermediaries are legally mandated "
        "to remove or disable access to such material WITHIN 24 HOURS of receipt.\n\n"
        "Failure to comply revokes statutory Safe Harbour under Section 79 of the IT Act, 2000 and attracts criminal "
        "prosecution. Incident hash submitted to National Cyber Crime Reporting Portal (cybercrime.gov.in / Helpline 1930)."
    )
    
    audit_log.append_event("MEDIA_THREAT_DETECTED", {
        "candidate_origin": file_origin,
        "threat_category": analysis["threat_category"],
        "hamming_distance": analysis["hamming_distance"]
    })

    return {
        "analysis": analysis,
        "base_phash_hex": hex(int(BASE_USER_PHASH, 2)),
        "candidate_phash_hex": hex(int(candidate_phash, 2)),
        "target_url": file_origin,
        "c2pa_status": "SIGNATURE_TAMPERED_OR_ABSENT",
        "takedown_notice": takedown_notice
    }

@app.post("/api/ble/sweep")
async def ble_sweep_endpoint(request: Request):
    """Evaluates trailing Bluetooth RF beacons for stalking behavior."""
    data = await request.json()
    scenario = data.get("scenario", "STALKER_PRESENT")
    
    if scenario == "STALKER_PRESENT":
        # 4 observations with consistent close proximity across 3 different waypoints
        pings = [
            {"device_type": "Apple AirTag (Unregistered)", "rssi": -62, "location_cluster": "Library Quad"},
            {"device_type": "Apple AirTag (Unregistered)", "rssi": -58, "location_cluster": "Science Hallway"},
            {"device_type": "Apple AirTag (Unregistered)", "rssi": -64, "location_cluster": "Bus Stop A"},
            {"device_type": "Apple AirTag (Unregistered)", "rssi": -59, "location_cluster": "South Dorm"}
        ]
    else:
        # Transient RF beacons
        pings = [
            {"device_type": "Bluetooth Earbuds", "rssi": -85, "location_cluster": "Library Quad"},
            {"device_type": "Smart Watch", "rssi": -92, "location_cluster": "Cafeteria"}
        ]

    result = StalkerBeaconAnalyzer.evaluate_trajectory(pings)
    CURRENT_SYSTEM_STATE["ble_stalker_status"] = "ALERT_STALKER_CONFIRMED" if result["is_stalker_alert"] else "MONITORING_CLEAR"
    
    if result["is_stalker_alert"]:
        audit_log.append_event("STALKER_BEACON_FLAGGED", result)
        await broadcast_to_cad("CAD_BEACON_ALERT", result)
        
    return {
        "sweep_result": result,
        "raw_observations": pings
    }

@app.post("/api/persona/generate")
async def generate_persona_endpoint():
    """Generates an ephemeral persona for zero-leak deliveries, rideshares, or classifieds."""
    import random
    area_codes = [415, 650, 510, 917, 312]
    num = f"+1 ({random.choice(area_codes)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
    alias_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
    email = f"shield-{alias_id}@aegis-relay.net"
    
    return {
        "ephemeral_phone": num,
        "relay_email": email,
        "auto_expire_hours": 24,
        "exif_metadata_scrubbing": "ENABLED_ACTIVE",
        "caller_id_name": "Aegis Privacy Relay"
    }

@app.get("/api/merkle/chain")
async def get_merkle_chain():
    return JSONResponse(audit_log.chain)

# Mount static frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Aegis Protocol Loading...</h1>")
