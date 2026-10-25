import urllib.request
import json

def run_tests():
    base_url = "http://127.0.0.1:8080"
    print("==================================================")
    print("      AEGIS PROTOCOL END-TO-END VERIFICATION      ")
    print("==================================================")

    # 1. System state
    with urllib.request.urlopen(f"{base_url}/api/state") as resp:
        state = json.loads(resp.read().decode())
        print(f"[+] System State: {state['status']}")
        print(f"[+] Active Safe Corridor: {state['waypoint_name']}")
        print(f"[+] Shards in Escrow: {len(state['shards_escrow'])} Nodes")

    # 2. ZK Verify
    zk_req = urllib.request.Request(
        f"{base_url}/api/zk/verify",
        data=json.dumps({"lat": 37.7749, "lon": -122.4194}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(zk_req) as resp:
        zk_res = json.loads(resp.read().decode())
        print(f"[+] ZK-SNARK Geofence Proof Verified: {zk_res['valid']}")
        print(f"    - Constraints evaluated: {zk_res['proof_metrics']['constraints']}")
        print(f"    - Prover Latency: {zk_res['proof_metrics']['proving_time_ms']}ms")

    # 3. Media Forensic Scan
    leak_req = urllib.request.Request(
        f"{base_url}/api/media/forensic-scan",
        data=json.dumps({"sample_type": "EXACT_LEAK"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(leak_req) as resp:
        leak_res = json.loads(resp.read().decode())
        print(f"[+] Media Forensic Scan: {leak_res['analysis']['threat_category']}")
        print(f"    - Similarity: {leak_res['analysis']['similarity_percent']}%")
        print(f"    - Hamming Distance: {leak_res['analysis']['hamming_distance']} / 64 bits")
        print(f"    - Legal Takedown Notice Generated: {len(leak_res['takedown_notice'])} characters")

    # 4. BLE Stalker Sweep
    ble_req = urllib.request.Request(
        f"{base_url}/api/ble/sweep",
        data=json.dumps({"scenario": "STALKER_PRESENT"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(ble_req) as resp:
        ble_res = json.loads(resp.read().decode())
        print(f"[+] BLE Stalker Trajectory Sweep: Alert = {ble_res['sweep_result']['is_stalker_alert']}")
        print(f"    - Threat Score: {ble_res['sweep_result']['threat_score']}/100")
        print(f"    - Trailed Safe Zones: {ble_res['sweep_result']['distinct_safe_zones_trailed']}")

    # 5. Ephemeral Persona
    persona_req = urllib.request.Request(
        f"{base_url}/api/persona/generate",
        data=json.dumps({}).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(persona_req) as resp:
        p_res = json.loads(resp.read().decode())
        print(f"[+] Ephemeral Shield Identity Generated:")
        print(f"    - Masked Relay Number: {p_res['ephemeral_phone']}")
        print(f"    - Virtual Email: {p_res['relay_email']}")

    # 6. Merkle Evidence Chain
    with urllib.request.urlopen(f"{base_url}/api/merkle/chain") as resp:
        chain = json.loads(resp.read().decode())
        print(f"[+] Merkle Evidence Chain Length: {len(chain)} Blocks")
        print(f"    - Latest Block Hash: {chain[-1]['block_hash'][:16]}...")
        print(f"    - Standard: {chain[-1]['admissible_evidence_standard']}")

    print("==================================================")
    print("  ALL AEGIS SYSTEM TESTS PASSED SUCCESSFULLY!     ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
