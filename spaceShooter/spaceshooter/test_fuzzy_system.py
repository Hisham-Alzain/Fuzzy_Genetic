import csv
from fuzzy_engine import FuzzyDifficultyEngine


def run_validation_tests():
    print("Initializing Fuzzy Expert System for Headless Testing...")
    engine = FuzzyDifficultyEngine()

    # =====================================================================
    # THE VALIDATION DATASET
    # 15 distinct scenarios carefully crafted to trigger the 24 rule base.
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
            "inputs": (150, 60, 90, 4, 1, 1),
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
            "inputs": (200, 150, 85, 4, 3, 1),
        },
        # --- GROUP D: SPECIAL / COMPLEX SCENARIOS (Edge Cases) ---
        {
            "id": 11,
            "scenario": "Glass Cannon (Max gun/kills, critical health)",
            "inputs": (500, 200, 15, 2, 3, 2),
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
            "inputs": (150, 500, 40, 2, 1, 1),
        },
        {
            "id": 15,
            "scenario": "The Last Stand (Final life, max guns/kills, long time)",
            "inputs": (550, 500, 20, 1, 3, 4),
        },
    ]

    results_data = []

    print("\nRunning Test Cases...")
    print("-" * 80)

    for tc in test_cases:
        # Unpack inputs
        k, d, h, l, g, r = tc["inputs"]

        # Run inference
        out = engine.evaluate(k, d, h, l, g, r)

        # Extract the highest triggered rule for reporting
        top_rule = out["fired_rules"][0] if out["fired_rules"] else "None"

        # Format the console output
        print(f"Test {tc['id']:02d}: {tc['scenario']}")
        print(
            f"  Inputs -> Kills:{k:3} | Time:{d:3} | HP:{h:3} | Lvs:{l} | Gun:{g} | Restarts:{r:2}"
        )
        print(
            f"  Output -> Speed: {out['speed_mult']:.2f}x | Delay: {out['spawn_delay']:.2f}s | Size: {out['mob_size']:.2f}x"
        )
        print(f"  Fired  -> {top_rule}")
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
                "Expected Difficulty": _get_expected_difficulty(tc["id"]),
                "Actual Speed": out["speed_mult"],
                "Actual Delay": out["spawn_delay"],
                "Actual Size": out["mob_size"],
                "Primary Rule Fired": top_rule.split("THEN")[0].strip()
                + "...",  # Truncate for neatness
            }
        )

    # Export to CSV
    csv_filename = "fuzzy_validation_results.csv"
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results_data[0].keys())
        writer.writeheader()
        writer.writerows(results_data)

    print(f"\nSuccess! Validation dataset exported to '{csv_filename}'.")
    print("You can copy this directly into your final report to satisfy Requirement 8.")


def _get_expected_difficulty(test_id):
    """Helper to generate the 'Expected Output' column for the report."""
    if test_id in [1, 2, 3, 4]:
        return "Low (Mercy)"
    if test_id in [5, 6, 7]:
        return "Medium (Neutral)"
    if test_id in [8, 9, 10]:
        return "High (Challenge)"
    if test_id in [11]:
        return "V.High Speed, Low Size (Glass Cannon)"
    if test_id in [12]:
        return "Low Speed, V.High Size (Tank Swarm)"
    if test_id in [13, 15]:
        return "Maximum Overdrive (Extreme)"
    if test_id in [14]:
        return "Medium Speed, Small Size (Attrition)"
    return "Unknown"


if __name__ == "__main__":
    run_validation_tests()
