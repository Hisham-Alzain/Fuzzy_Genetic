import csv
import re
from fuzzy_engine import FuzzyDifficultyEngine


def run_validation_tests():
    print("Initializing Fuzzy Expert System for Headless Testing...")
    engine = FuzzyDifficultyEngine()

    # =====================================================================
    # THE VALIDATION DATASET
    # 15 distinct scenarios carefully crafted to trigger specific rules.
    # Inputs: kills, duration, health, lives, gun, restarts
    # =====================================================================
    test_cases = [
        # --- GROUP A: MERCY / LOW DIFFICULTY (Struggling Players) ---
        {
            "id": 1,
            "scenario": "Critical Mercy (Dying immediately)",
            "inputs": (10, 20, 10, 1, 1, 0),
        },
        {
            "id": 2,
            "scenario": "Persistent Mercy (Too many restarts)",
            "inputs": (50, 100, 40, 2, 1, 18),
        },
        {
            "id": 3,
            "scenario": "Fatigue Pullback (High time, low health)",
            "inputs": (300, 500, 20, 2, 2, 5),
        },
        {
            "id": 4,
            "scenario": "Low DPS Struggle (High time, no kills)",
            "inputs": (20, 300, 80, 4, 1, 2),
        },
        # --- GROUP B: NEUTRAL / MEDIUM DIFFICULTY (Average Runs) ---
        {
            "id": 5,
            "scenario": "Gentle Intro (Game just started)",
            "inputs": (0, 10, 100, 5, 1, 0),
        },
        {
            "id": 6,
            "scenario": "Standard Pace (Mid-game, average stats)",
            "inputs": (250, 250, 50, 3, 2, 5),
        },
        {
            "id": 7,
            "scenario": "Stable Start (Doing well early on)",
            "inputs": (260, 60, 75, 4, 1, 1),
        },
        # --- GROUP C: CHALLENGE / HIGH DIFFICULTY (Skilled Players) ---
        {
            "id": 8,
            "scenario": "Challenge Ramp (Late game, many kills)",
            "inputs": (450, 400, 60, 3, 2, 2),
        },
        {
            "id": 9,
            "scenario": "Early Dominance (Massive kills early)",
            "inputs": (400, 50, 90, 5, 3, 0),
        },
        {
            "id": 10,
            "scenario": "Weapon Escalation (Max gun, high health)",
            "inputs": (200, 150, 80, 4, 3, 1),
        },
        # --- GROUP D: SPECIAL / COMPLEX SCENARIOS (Edge Cases) ---
        {
            "id": 11,
            "scenario": "Glass Cannon (Max gun/kills, critical health)",
            "inputs": (400, 200, 30, 2, 3, 2),
        },
        {
            "id": 12,
            "scenario": "Tank Swarm (Max health/lives, no kills)",
            "inputs": (30, 350, 100, 5, 1, 0),
        },
        {
            "id": 13,
            "scenario": "MAX OVERDRIVE (God Mode - Max everything)",
            "inputs": (600, 600, 100, 5, 3, 0),
        },
        {
            "id": 14,
            "scenario": "War of Attrition (Long survive, weak weapon)",
            "inputs": (150, 360, 40, 2, 1, 1),
        },
        {
            "id": 15,
            "scenario": "The Last Stand (Final life, max guns/kills, long time)",
            "inputs": (400, 360, 20, 1, 3, 4),
        },
    ]

    results_data = []
    correct_predictions = 0
    total_tests = len(test_cases)

    print("\nRunning Test Cases...")
    print("-" * 80)

    for tc in test_cases:
        # Unpack inputs
        k, d, h, l, g, r = tc["inputs"]

        # Run inference
        out = engine.evaluate(k, d, h, l, g, r)

        # Extract all fired rules and their IDs
        fired_rules_list = out.get("fired_rules", [])
        fired_rule_ids = [_extract_rule_id(rule) for rule in fired_rules_list]

        expected_rule_id = _get_expected_target_rule(tc["id"])

        # Check if the expected rule is INCLUDED anywhere in the fired rules
        is_correct = expected_rule_id in fired_rule_ids

        if is_correct:
            correct_predictions += 1
            match_status = "[✔ FIRED]"
        else:
            match_status = "[✖ DID NOT FIRE]"

        # Get primary rule for logging purposes
        primary_rule_id = fired_rule_ids[0] if fired_rule_ids else "None"
        primary_rule_text = (
            fired_rules_list[0].split("THEN")[0].strip() + "..."
            if fired_rules_list
            else "None"
        )

        # Format the console output
        print(f"Test {tc['id']:02d}: {tc['scenario']}")
        print(
            f"  Inputs   -> Kills:{k:3} | Time:{d:3} | HP:{h:3} | Lvs:{l} | Gun:{g} | Restarts:{r:2}"
        )
        print(f"  Expected -> {expected_rule_id} {match_status}")
        print(f"  Fired    -> {', '.join(fired_rule_ids)}")
        if primary_rule_id != expected_rule_id and is_correct:
            print(f"  Note     -> Target matched, but Primary was {primary_rule_id}")
        print("-" * 80)

        # Save for CSV
        results_data.append(
            {
                "Test ID": tc["id"],
                "Scenario Definition": tc["scenario"],
                "Kills": k,
                "Time (s)": d,
                "Health (%)": h,
                "Lives": l,
                "Gun Lvl": g,
                "Restarts": r,
                "Expected Target Rule": expected_rule_id,
                "Did Target Fire?": is_correct,
                "All Fired Rule IDs": ", ".join(fired_rule_ids),
                "Primary Rule Fired": primary_rule_id,
                "Actual Speed": round(out["speed_mult"], 3),
                "Actual Delay": round(out["spawn_delay"], 3),
                "Actual Size": round(out["mob_size"], 3),
                "Primary Rule Detail": primary_rule_text,
            }
        )

    # Calculate and Print Total Accuracy
    accuracy_percentage = (correct_predictions / total_tests) * 100
    print("\n" + "=" * 80)
    print(f"VALIDATION COMPLETE")
    print(
        f"Target Rule Inclusion Match: {correct_predictions} / {total_tests} ({accuracy_percentage:.2f}%)"
    )
    print("=" * 80 + "\n")

    # Export to CSV
    csv_filename = "fuzzy_validation_results.csv"
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results_data[0].keys())
        writer.writeheader()
        writer.writerows(results_data)

    print(f"Success! Validation dataset exported to '{csv_filename}'.")


def _get_expected_target_rule(test_id):
    """Maps a test case ID directly to the primary rule it was engineered to trigger."""
    expected_mapping = {
        1: "R1",  # Critical Mercy
        2: "R3",  # Persistent Mercy
        3: "R2",  # Fatigue Pullback
        4: "R6",  # Low DPS Struggle
        5: "R7",  # Gentle Intro
        6: "R8",  # Standard Pace
        7: "R12",  # Stable Start
        8: "R13",  # Challenge Ramp
        9: "R18",  # Early Dominance
        10: "R15",  # Weapon Escalation
        11: "R19",  # Glass Cannon
        12: "R21",  # Tank Swarm
        13: "R22",  # MAX OVERDRIVE
        14: "R23",  # War of Attrition
        15: "R24",  # The Last Stand
    }
    return expected_mapping.get(test_id, "Unknown")


def _extract_rule_id(rule_str):
    """Extracts the R# identifier from the front of the rule string."""
    if not rule_str or rule_str == "None":
        return "None"

    # Looks for "R1:", "R24:", etc.
    match = re.search(r"^(R\d+):", str(rule_str))
    if match:
        return match.group(1)
    return "Unknown"


if __name__ == "__main__":
    run_validation_tests()
