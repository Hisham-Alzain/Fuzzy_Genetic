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
        # 3. RULE BASE  (15 Rules in 3 Groups)
        # =====================================================
        #
        # Player struggling  -> ease off  (slow mobs, sparse spawns, small targets)
        # Player stable      -> hold      (medium everything)
        # Player dominating  -> ramp up   (fast mobs, dense spawns, big targets)

        self.rules_info = []  # Stores (rule_obj, description) pairs

        # ---- GROUP A: MERCY RULES (1-5) ----

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

        # ---- GROUP B: NEUTRAL RULES (6-10) ----

        r6 = ctrl.Rule(
            self.time_elapsed["very_low"] & self.mobs_killed["very_low"],
            (self.speed_mult["low"], self.spawn_delay["high"], self.mob_size["low"]),
        )
        self.rules_info.append(
            (r6, "R6:  IF time=V.Low AND kills=V.Low THEN gentle intro")
        )

        r7 = ctrl.Rule(
            self.mobs_killed["medium"] & self.time_elapsed["medium"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append((r7, "R7:  IF kills=Med AND time=Med THEN standard"))

        r8 = ctrl.Rule(
            self.health["medium"] & self.lives["normal"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r8, "R8:  IF health=Med AND lives=Normal THEN baseline")
        )

        r9 = ctrl.Rule(
            self.gun_level["high"] & self.health["low"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r9, "R9:  IF gun=High AND health=Low THEN equipment compensates")
        )

        r10 = ctrl.Rule(
            self.restart_count["normal"] & self.health["medium"],
            (
                self.speed_mult["medium"],
                self.spawn_delay["medium"],
                self.mob_size["medium"],
            ),
        )
        self.rules_info.append(
            (r10, "R10: IF restarts=Normal AND health=Med THEN stable")
        )

        # ---- GROUP C: CHALLENGE RULES (11-15) ----

        r11 = ctrl.Rule(
            self.mobs_killed["high"] & self.time_elapsed["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r11, "R11: IF kills=High AND time=High THEN challenge ramp")
        )

        r12 = ctrl.Rule(
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
            (r12, "R12: IF kills=V.High AND health=V.High AND lives=High THEN max")
        )

        r13 = ctrl.Rule(
            self.gun_level["high"] & self.health["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r13, "R13: IF gun=High AND health=High THEN weapon escalation")
        )

        r14 = ctrl.Rule(
            self.time_elapsed["very_high"] & self.health["high"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r14, "R14: IF time=V.High AND health=High THEN endurance push")
        )

        r15 = ctrl.Rule(
            self.mobs_killed["high"] & self.lives["high"] & self.restart_count["low"],
            (self.speed_mult["high"], self.spawn_delay["low"], self.mob_size["high"]),
        )
        self.rules_info.append(
            (r15, "R15: IF kills=High AND lives=High AND restarts=Low THEN talent")
        )

        # =====================================================
        # 4. COMPILE ENGINE
        # =====================================================
        all_rules = [info[0] for info in self.rules_info]
        self.dda_control = ctrl.ControlSystem(all_rules)
        self.simulator = ctrl.ControlSystemSimulation(self.dda_control)

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
        strengths = [
            min(lv["low"], hp["very_low"]),  # R1
            min(max(te["high"], te["very_high"]), hp["low"]),  # R2
            rc["high"],  # R3
            min(te["very_low"], hp["very_low"]),  # R4
            hp["very_low"],  # R5
            min(te["very_low"], mk["very_low"]),  # R6
            min(mk["medium"], te["medium"]),  # R7
            min(hp["medium"], lv["normal"]),  # R8
            min(gl["high"], hp["low"]),  # R9
            min(rc["normal"], hp["medium"]),  # R10
            min(mk["high"], te["high"]),  # R11
            min(mk["very_high"], hp["very_high"], lv["high"]),  # R12
            min(gl["high"], hp["high"]),  # R13
            min(te["very_high"], hp["high"]),  # R14
            min(mk["high"], lv["high"], rc["low"]),  # R15
        ]

        fired = []
        for i, strength in enumerate(strengths):
            if strength > 0.01:
                desc = self.rules_info[i][1]
                fired.append(f"{desc}  [{strength:.2f}]")

        return fired if fired else ["No rules currently active"]
