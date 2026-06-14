import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyDifficultyEngine:
    def __init__(self):
        # =====================================================
        # 1. UNIVERSES OF DISCOURSE
        # =====================================================

        # --- 5-Tier Continuous Inputs ---
        self.mobs_killed = ctrl.Antecedent(np.arange(0, 601, 1), "mobs_killed")
        self.time_elapsed = ctrl.Antecedent(np.arange(0, 601, 5), "time_elapsed")
        self.health = ctrl.Antecedent(np.arange(0, 101, 1), "health")

        # --- 3-Tier Discrete Inputs ---
        self.lives = ctrl.Antecedent(np.arange(1, 6, 1), "lives")
        self.gun_level = ctrl.Antecedent(np.arange(1, 4, 1), "gun_level")
        self.restart_count = ctrl.Antecedent(np.arange(0, 21, 1), "restart_count")

        # --- 5-Tier Outputs ---
        self.speed_mult = ctrl.Consequent(np.arange(0.5, 1.55, 0.05), "speed_mult")
        self.spawn_delay = ctrl.Consequent(np.arange(0.5, 3.1, 0.1), "spawn_delay")
        self.mob_size = ctrl.Consequent(np.arange(0.6, 1.85, 0.05), "mob_size")

        # =====================================================
        # 2. MEMBERSHIP FUNCTIONS
        # =====================================================

        # --- mobs_killed (Gaussian) ---
        self.mobs_killed["very_low"] = fuzz.gaussmf(self.mobs_killed.universe, 0, 30)
        self.mobs_killed["low"] = fuzz.gaussmf(self.mobs_killed.universe, 100, 35)
        self.mobs_killed["medium"] = fuzz.gaussmf(self.mobs_killed.universe, 260, 70)
        self.mobs_killed["high"] = fuzz.gaussmf(self.mobs_killed.universe, 400, 55)
        self.mobs_killed["very_high"] = fuzz.gaussmf(self.mobs_killed.universe, 600, 45)

        # --- time_elapsed (Triangular / Trapezoidal) ---
        self.time_elapsed["very_low"] = fuzz.trimf(
            self.time_elapsed.universe, [0, 0, 60]
        )
        self.time_elapsed["low"] = fuzz.trimf(self.time_elapsed.universe, [20, 90, 120])
        self.time_elapsed["medium"] = fuzz.trimf(
            self.time_elapsed.universe, [60, 240, 420]
        )
        self.time_elapsed["high"] = fuzz.trimf(
            self.time_elapsed.universe, [180, 360, 500]
        )
        self.time_elapsed["very_high"] = fuzz.trapmf(
            self.time_elapsed.universe, [420, 540, 600, 600]
        )

        # --- health (Triangular) ---
        self.health["very_low"] = fuzz.trimf(self.health.universe, [0, 0, 25])
        self.health["low"] = fuzz.trimf(self.health.universe, [15, 30, 40])
        self.health["medium"] = fuzz.trimf(self.health.universe, [25, 50, 75])
        self.health["high"] = fuzz.trimf(self.health.universe, [65, 75, 90])
        self.health["very_high"] = fuzz.trimf(self.health.universe, [80, 100, 100])

        # --- lives (3-Tier) ---
        self.lives["low"] = fuzz.trimf(self.lives.universe, [1, 1, 2])
        self.lives["normal"] = fuzz.trimf(self.lives.universe, [1, 2, 4])
        self.lives["high"] = fuzz.trapmf(self.lives.universe, [3, 4, 5, 5])

        # --- gun_level (3-Tier) ---
        self.gun_level["low"] = fuzz.trimf(self.gun_level.universe, [1, 1, 2])
        self.gun_level["normal"] = fuzz.trimf(self.gun_level.universe, [1, 2, 3])
        self.gun_level["high"] = fuzz.trimf(self.gun_level.universe, [2, 3, 3])

        # --- restart_count (3-Tier) ---
        self.restart_count["low"] = fuzz.trimf(self.restart_count.universe, [0, 0, 7])
        self.restart_count["normal"] = fuzz.trimf(
            self.restart_count.universe, [4, 10, 15]
        )
        self.restart_count["high"] = fuzz.trapmf(
            self.restart_count.universe, [13, 18, 20, 20]
        )

        # --- speed_mult output (5-Tier) ---
        self.speed_mult["very_low"] = fuzz.trimf(
            self.speed_mult.universe, [0.5, 0.5, 0.7]
        )
        self.speed_mult["low"] = fuzz.trimf(self.speed_mult.universe, [0.6, 0.9, 1.0])
        self.speed_mult["medium"] = fuzz.trimf(
            self.speed_mult.universe, [0.8, 1.1, 1.25]
        )
        self.speed_mult["high"] = fuzz.trimf(self.speed_mult.universe, [1.15, 1.3, 1.4])
        self.speed_mult["very_high"] = fuzz.trimf(
            self.speed_mult.universe, [1.3, 1.50, 1.55]
        )

        # --- spawn_delay output (5-Tier) ---
        self.spawn_delay["very_low"] = fuzz.trimf(
            self.spawn_delay.universe, [0.5, 0.5, 0.75]
        )
        self.spawn_delay["low"] = fuzz.trimf(self.spawn_delay.universe, [0.7, 1.2, 1.5])
        self.spawn_delay["medium"] = fuzz.trimf(
            self.spawn_delay.universe, [1.35, 1.7, 2.0]
        )
        self.spawn_delay["high"] = fuzz.trimf(
            self.spawn_delay.universe, [1.9, 2.3, 2.7]
        )
        self.spawn_delay["very_high"] = fuzz.trimf(
            self.spawn_delay.universe, [2.5, 3.0, 3.0]
        )

        # --- mob_size output (5-Tier) ---
        self.mob_size["very_low"] = fuzz.trimf(self.mob_size.universe, [0.6, 0.6, 0.75])
        self.mob_size["low"] = fuzz.trimf(self.mob_size.universe, [0.7, 0.9, 1.05])
        self.mob_size["medium"] = fuzz.trimf(self.mob_size.universe, [0.95, 1.2, 1.35])
        self.mob_size["high"] = fuzz.trimf(self.mob_size.universe, [1.15, 1.5, 1.65])
        self.mob_size["very_high"] = fuzz.trimf(
            self.mob_size.universe, [1.5, 1.8, 1.85]
        )

        # =====================================================
        # 3. RULE BASE  (24 Rules in 4 Groups)
        # =====================================================
        #
        # Player struggling  -> ease off  (slow mobs, sparse spawns, small targets)
        # Player stable      -> hold      (medium everything)
        # Player dominating  -> ramp up   (fast mobs, dense spawns, big targets)
        # Player special     -> New challenges (chaos, high damage, low dodge)

        self.rules_info = []  # Stores (rule_obj, description) pairs

        # ---- GROUP A: LOW / MERCY RULES (1-6) ----

        r1 = ctrl.Rule(
            self.lives["low"] & self.health["very_low"],
            (
                self.speed_mult["very_low"],
                self.spawn_delay["very_high"],
                self.mob_size["very_low"],
            ),
        )
        self.rules_info.append((r1, "R1:  IF lives=Low AND health=V.Low THEN ease MAX"))

        r2 = ctrl.Rule(
            (self.time_elapsed["high"] | self.time_elapsed["very_high"])
            & self.health["low"],
            (self.speed_mult["low"], self.spawn_delay["high"], self.mob_size["low"]),
        )
        self.rules_info.append(
            (r2, "R2:  IF time=High+ AND health=Low THEN fatigue pullback")
        )

        r3 = ctrl.Rule(
            self.restart_count["high"],
            (self.speed_mult["low"], self.spawn_delay["high"], self.mob_size["low"]),
        )
        self.rules_info.append((r3, "R3:  IF restarts=High THEN persistent mercy"))

        r4 = ctrl.Rule(
            self.time_elapsed["very_low"] & self.health["very_low"],
            (self.speed_mult["low"], self.spawn_delay["high"], self.mob_size["low"]),
        )
        self.rules_info.append(
            (r4, "R4:  IF time=V.Low AND health=V.Low THEN early mercy")
        )

        r5 = ctrl.Rule(
            self.health["very_low"],
            (self.speed_mult["low"], self.spawn_delay["high"], self.mob_size["low"]),
        )
        self.rules_info.append((r5, "R5:  IF health=V.Low THEN safety net"))

        # NEW R6: Low DPS Struggle - Player survives but can't kill anything.
        r6 = ctrl.Rule(
            self.gun_level["low"]
            & self.mobs_killed["very_low"]
            & (self.time_elapsed["medium"] | self.time_elapsed["high"]),
            (
                self.speed_mult["very_low"],
                self.spawn_delay["high"],
                self.mob_size["low"],
            ),
        )
        self.rules_info.append(
            (r6, "R6:  IF gun=Low AND kills=V.Low AND time=Med+ THEN low dps struggle")
        )

        # ---- GROUP B: MEDIUM / NEUTRAL RULES (7-12) ----

        r7 = ctrl.Rule(
            self.time_elapsed["very_low"] & self.mobs_killed["very_low"],
            (self.speed_mult["low"], self.spawn_delay["high"], self.mob_size["low"]),
        )
        self.rules_info.append(
            (r7, "R7:  IF time=V.Low AND kills=V.Low THEN gentle intro")
        )

        r8 = ctrl.Rule(
            self.mobs_killed["medium"] & self.time_elapsed["medium"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append((r8, "R8:  IF kills=Med AND time=Med THEN standard"))

        r9 = ctrl.Rule(
            self.health["medium"] & self.lives["normal"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r9, "R9:  IF health=Med AND lives=Normal THEN baseline")
        )

        r10 = ctrl.Rule(
            self.gun_level["high"] & self.health["low"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r10, "R10:  IF gun=High AND health=Low THEN equipment compensates")
        )

        r11 = ctrl.Rule(
            self.restart_count["normal"] & self.health["medium"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r11, "R11: IF restarts=Normal AND health=Med THEN stable")
        )

        # NEW R12: Stable Start - Prevent sudden spikes in early game if player is just doing okay.
        r12 = ctrl.Rule(
            self.time_elapsed["low"] & self.mobs_killed["medium"] & self.health["high"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r12, "R12: IF time=Low AND kills=Med AND health=High THEN stable start")
        )

        # ---- GROUP C: HIGH / CHALLENGE RULES (13-18) ----

        r13 = ctrl.Rule(
            self.mobs_killed["high"] & self.time_elapsed["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r13, "R13: IF kills=High AND time=High THEN challenge ramp")
        )

        r14 = ctrl.Rule(
            self.mobs_killed["very_high"]
            & self.health["very_high"]
            & self.lives["high"],
            (
                self.speed_mult["very_high"],
                self.spawn_delay["very_low"],
                self.mob_size["very_high"],
            ),
        )
        self.rules_info.append(
            (r14, "R14: IF kills=V.High AND health=V.High AND lives=High THEN max")
        )

        r15 = ctrl.Rule(
            self.gun_level["high"] & self.health["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r15, "R15: IF gun=High AND health=High THEN weapon escalation")
        )

        r16 = ctrl.Rule(
            self.time_elapsed["very_high"] & self.health["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r16, "R16: IF time=V.High AND health=High THEN endurance push")
        )

        r17 = ctrl.Rule(
            self.mobs_killed["high"] & self.lives["high"] & self.restart_count["low"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r17, "R17: IF kills=High AND lives=High AND restarts=Low THEN talent")
        )

        # NEW R18: Early Dominance - Patches the gap you found!
        r18 = ctrl.Rule(
            self.gun_level["high"]
            & self.mobs_killed["high"]
            & self.time_elapsed["low"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r18, "R18: IF gun=High AND kills=High AND time=Low THEN early dominance")
        )

        # ---- GROUP D: SPECIAL / COMPLEX RULES (19-24) ----

        # R16: Glass Cannon (Player has massive firepower & kills, but low health)
        # Give them fast enemies but smaller hitboxes to dodge, testing their aim.
        r19 = ctrl.Rule(
            self.gun_level["high"] & self.health["low"] & self.mobs_killed["high"],
            (
                self.speed_mult["very_high"],
                self.spawn_delay["low"],
                self.mob_size["low"],
            ),
        )
        self.rules_info.append(
            (r19, "R19: IF gun=High+kills=High+health=Low THEN fast glass cannon mode")
        )

        # R17: The Comeback / Redemption (Player died a lot before, but is currently surviving well)
        # We increase difficulty to match their current good run, but not to the absolute max so we don't unfairly ruin their comeback.
        r20 = ctrl.Rule(
            self.restart_count["high"] & self.mobs_killed["high"] & self.health["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["medium"]),
        )
        self.rules_info.append(
            (
                r20,
                "R20: IF restarts=High+kills=High+health=High THEN redemption challenge",
            )
        )

        # R18: Tank but Ineffective (Player is surviving a long time, but not killing much)
        # Force them to act by swarming them with massive, slow-moving targets.
        r21 = ctrl.Rule(
            self.health["very_high"]
            & self.lives["high"]
            & self.mobs_killed["low"]
            & (self.time_elapsed["medium"] | self.time_elapsed["high"]),
            (
                self.speed_mult["low"],
                self.spawn_delay["very_low"],
                self.mob_size["very_high"],
            ),
        )
        self.rules_info.append(
            (r21, "R21: IF time=Med+health=V.High+kills=Low THEN giant slow swarm")
        )

        # R19: Maximum Overdrive / God Mode (Player is dominating absolutely everything)
        # Absolute maximum difficulty. Fast, huge, and spawning constantly.
        r22 = ctrl.Rule(
            self.gun_level["high"]
            & self.health["very_high"]
            & self.lives["high"]
            & self.time_elapsed["very_high"]
            & self.mobs_killed["very_high"],
            (
                self.speed_mult["very_high"],
                self.spawn_delay["very_low"],
                self.mob_size["very_high"],
            ),
        )
        self.rules_info.append((r22, "R22: IF ALL stats dominating THEN MAX OVERDRIVE"))

        # R20: War of Attrition (Player survived a long time, but with weak weapons and few kills)
        # Lots of normal-speed, small targets.
        r23 = ctrl.Rule(
            self.time_elapsed["high"]
            & self.gun_level["low"]
            & self.restart_count["low"],
            (self.speed_mult["medium"], self.spawn_delay["low"], self.mob_size["low"]),
        )
        self.rules_info.append(
            (r23, "R23: IF time=High+gun=Low+restarts=Low THEN war of attrition")
        )

        # NEW R24: The Last Stand - Final life, huge weapons, lots of kills, but surviving a long time. Pure chaos.
        r24 = ctrl.Rule(
            self.lives["low"]
            & self.gun_level["high"]
            & self.mobs_killed["high"]
            & self.time_elapsed["high"],
            (
                self.speed_mult["very_high"],
                self.spawn_delay["very_low"],
                self.mob_size["high"],
            ),
        )
        self.rules_info.append(
            (
                r24,
                "R24: IF lives=Low AND gun=High AND kills=High AND time=High THEN the last stand",
            )
        )

        # =====================================================
        # 4. COMPILE ENGINE
        # =====================================================
        all_rules = [info[0] for info in self.rules_info]
        self.dda_control = ctrl.ControlSystem(all_rules)
        self.simulator = ctrl.ControlSystemSimulation(self.dda_control)

        # =====================================================
        # 5. UI DISPLAY DICTIONARY (24 Rules)
        # =====================================================
        self.rule_descriptions = {
            # --- GROUP A: LOW / MERCY RULES ---
            "R1": {
                "name": "Critical Mercy",
                "effect": "speed_mult=very_low, spawn_delay=very_high, mob_size=very_low",
            },
            "R2": {
                "name": "Fatigue Pullback",
                "effect": "speed_mult=low, spawn_delay=high, mob_size=low",
            },
            "R3": {
                "name": "Persistent Mercy",
                "effect": "speed_mult=low, spawn_delay=high, mob_size=low",
            },
            "R4": {
                "name": "Early Struggle",
                "effect": "speed_mult=low, spawn_delay=high, mob_size=low",
            },
            "R5": {
                "name": "Safety Net",
                "effect": "speed_mult=low, spawn_delay=high, mob_size=low",
            },
            "R6": {
                "name": "Low DPS Struggle",
                "effect": "speed_mult=very_low, spawn_delay=high, mob_size=low",
            },
            # --- GROUP B: MEDIUM / NEUTRAL RULES ---
            "R7": {
                "name": "Gentle Intro",
                "effect": "speed_mult=low, spawn_delay=high, mob_size=low",
            },
            "R8": {
                "name": "Standard Pace",
                "effect": "speed_mult=medium, spawn_delay=medium, mob_size=medium",
            },
            "R9": {
                "name": "Balanced State",
                "effect": "speed_mult=medium, spawn_delay=medium, mob_size=medium",
            },
            "R10": {
                "name": "Equipment Comp.",
                "effect": "speed_mult=medium, spawn_delay=medium, mob_size=medium",
            },
            "R11": {
                "name": "Stabilized Run",
                "effect": "speed_mult=medium, spawn_delay=medium, mob_size=medium",
            },
            "R12": {
                "name": "Stable Start",
                "effect": "speed_mult=medium, spawn_delay=medium, mob_size=medium",
            },
            # --- GROUP C: HIGH / CHALLENGE RULES ---
            "R13": {
                "name": "Challenge Ramp",
                "effect": "speed_mult=high, spawn_delay=low, mob_size=high",
            },
            "R14": {
                "name": "Peak Performance",
                "effect": "speed_mult=very_high, spawn_delay=very_low, mob_size=very_high",
            },
            "R15": {
                "name": "Weapon Escalation",
                "effect": "speed_mult=high, spawn_delay=low, mob_size=high",
            },
            "R16": {
                "name": "Endurance Push",
                "effect": "speed_mult=high, spawn_delay=low, mob_size=high",
            },
            "R17": {
                "name": "Talent Recognition",
                "effect": "speed_mult=high, spawn_delay=low, mob_size=high",
            },
            "R18": {
                "name": "Early Dominance",
                "effect": "speed_mult=high, spawn_delay=low, mob_size=high",
            },
            # --- GROUP D: SPECIAL / COMPLEX RULES ---
            "R19": {
                "name": "Glass Cannon",
                "effect": "speed_mult=very_high, spawn_delay=low, mob_size=low",
            },
            "R20": {
                "name": "The Comeback",
                "effect": "speed_mult=high, spawn_delay=low, mob_size=medium",
            },
            "R21": {
                "name": "Tank Swarm",
                "effect": "speed_mult=low, spawn_delay=very_low, mob_size=very_high",
            },
            "R22": {
                "name": "MAX OVERDRIVE",
                "effect": "speed_mult=very_high, spawn_delay=very_low, mob_size=very_high",
            },
            "R23": {
                "name": "War of Attrition",
                "effect": "speed_mult=medium, spawn_delay=low, mob_size=low",
            },
            "R24": {
                "name": "The Last Stand",
                "effect": "speed_mult=very_high, spawn_delay=very_low, mob_size=high",
            },
        }

    # ----------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------

    def evaluate(self, kills, duration, health, lives, gun, restarts):
        """Run Mamdani inference with centroid defuzzification.
        Returns dict with 3 outputs + list of fired rule descriptions."""
        try:
            self.simulator.input["mobs_killed"] = float(np.clip(kills, 0, 600))
            self.simulator.input["time_elapsed"] = float(np.clip(duration, 0, 600))
            self.simulator.input["health"] = float(np.clip(health, 0, 100))
            self.simulator.input["lives"] = float(np.clip(lives, 1, 5))
            self.simulator.input["gun_level"] = float(np.clip(gun, 1, 3))
            self.simulator.input["restart_count"] = float(np.clip(restarts, 0, 20))

            self.simulator.compute()

            fired = self._get_fired_rules(kills, duration, health, lives, gun, restarts)

            return {
                "speed_mult": round(self.simulator.output["speed_mult"], 3),
                "spawn_delay": round(self.simulator.output["spawn_delay"], 3),
                "mob_size": round(self.simulator.output["mob_size"], 3),
                "fired_rules": fired,
            }
        except Exception as e:
            print(f"[Fuzzy Engine Failsafe] {e}")
            return {
                "speed_mult": 1.0,
                "spawn_delay": 1.5,
                "mob_size": 1.0,
                "fired_rules": ["Engine failsafe active — no rules fired"],
            }

    def get_mf_data(self):
        """Return membership function arrays for all 9 variables (for pygame plot rendering).
        Returns list of dicts in display order."""
        ordered = [
            ("Mobs Killed", self.mobs_killed, "input"),
            ("Time Elapsed", self.time_elapsed, "input"),
            ("Health", self.health, "input"),
            ("Lives", self.lives, "input"),
            ("Gun Level", self.gun_level, "input"),
            ("Restarts", self.restart_count, "input"),
            ("Speed Mult", self.speed_mult, "output"),
            ("Spawn Delay", self.spawn_delay, "output"),
            ("Mob Size", self.mob_size, "output"),
        ]
        result = []
        for name, var, vtype in ordered:
            terms = {}
            for label in var.terms:
                terms[label] = var[label].mf.copy()
            result.append(
                {
                    "name": name,
                    "universe": var.universe.copy(),
                    "terms": terms,
                    "type": vtype,
                }
            )
        return result

    def plot_graphs(self):
        """Open matplotlib windows for documentation screenshots."""
        self.mobs_killed.view()
        self.time_elapsed.view()
        self.health.view()
        self.lives.view()
        self.gun_level.view()
        self.restart_count.view()
        self.speed_mult.view()
        self.spawn_delay.view()
        self.mob_size.view()
        import matplotlib.pyplot as plt

        plt.show()

    # ----------------------------------------------------------
    # INTERNAL: Fired rules detection
    # ----------------------------------------------------------

    def _mu(self, var, term, value):
        """Interpolate membership degree for a crisp value in a fuzzy set."""
        clamped = float(np.clip(value, var.universe[0], var.universe[-1]))
        return float(fuzz.interp_membership(var.universe, var[term].mf, clamped))

    def _get_fired_rules(self, kills, duration, health, lives, gun, restarts):
        """Compute which rules have non-zero activation and their strength."""
        mk = {t: self._mu(self.mobs_killed, t, kills) for t in self.mobs_killed.terms}
        te = {
            t: self._mu(self.time_elapsed, t, duration) for t in self.time_elapsed.terms
        }
        hp = {t: self._mu(self.health, t, health) for t in self.health.terms}
        lv = {t: self._mu(self.lives, t, lives) for t in self.lives.terms}
        gl = {t: self._mu(self.gun_level, t, gun) for t in self.gun_level.terms}
        rc = {
            t: self._mu(self.restart_count, t, restarts)
            for t in self.restart_count.terms
        }

        # Firing strength per rule (AND = min, OR = max)
        # Firing strength per rule (AND = min, OR = max)
        strengths = [
            # --- GROUP A ---
            min(lv["low"], hp["very_low"]),  # R1
            min(max(te["high"], te["very_high"]), hp["low"]),  # R2
            rc["high"],  # R3
            min(te["very_low"], hp["very_low"]),  # R4
            hp["very_low"],  # R5
            min(gl["low"], mk["very_low"], max(te["medium"], te["high"])),  # R6
            # --- GROUP B ---
            min(te["very_low"], mk["very_low"]),  # R7
            min(mk["medium"], te["medium"]),  # R8
            min(hp["medium"], lv["normal"]),  # R9
            min(gl["high"], hp["low"]),  # R10
            min(rc["normal"], hp["medium"]),  # R11
            min(te["low"], mk["medium"], hp["high"]),  # R12
            # --- GROUP C ---
            min(mk["high"], te["high"]),  # R13
            min(mk["very_high"], hp["very_high"], lv["high"]),  # R14
            min(gl["high"], hp["high"]),  # R15
            min(te["very_high"], hp["high"]),  # R16
            min(mk["high"], lv["high"], rc["low"]),  # R17
            min(gl["high"], mk["high"], te["low"]),  # R18
            # --- GROUP D ---
            min(gl["high"], hp["low"], mk["high"]),  # R19
            min(rc["high"], mk["high"], hp["high"]),  # R20
            min(
                hp["very_high"], lv["high"], mk["low"], max(te["medium"], te["high"])
            ),  # R21
            min(
                gl["high"],
                hp["very_high"],
                lv["high"],
                te["very_high"],
                mk["very_high"],
            ),  # R22
            min(te["high"], gl["low"], rc["low"]),  # R23
            min(lv["low"], gl["high"], mk["high"], te["high"]),  # R24
        ]

        fired = []
        for i, strength in enumerate(strengths):
            if strength > 0.01:
                desc = self.rules_info[i][1]
                fired.append(f"{desc}  [{strength:.2f}]")

        return fired if fired else ["No rules currently active"]
