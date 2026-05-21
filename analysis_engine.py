# ============================================================
# FILE: analysis_engine.py
# ============================================================

from dataclasses import dataclass

# ============================================================
# CLUB DATABASE
# ============================================================

CLUB_DATABASE = {

    "Driver": {
        "static_loft": 10.5,
        "typical_smash": (1.45, 1.50),
    },

    "3W": {
        "static_loft": 15,
        "typical_smash": (1.42, 1.48),
    },

    "5I": {
        "static_loft": 27,
        "typical_smash": (1.32, 1.38),
    },

    "6I": {
        "static_loft": 30,
        "typical_smash": (1.31, 1.37),
    },

    "7I": {
        "static_loft": 34,
        "typical_smash": (1.30, 1.36),
    },

    "8I": {
        "static_loft": 38,
        "typical_smash": (1.28, 1.34),
    },

    "9I": {
        "static_loft": 42,
        "typical_smash": (1.25, 1.32),
    },

    "PW": {
        "static_loft": 46,
        "typical_smash": (1.18, 1.28),
    },
}


# ============================================================
# DATA STRUCTURE
# ============================================================

@dataclass
class ShotData:

    club: str

    launch_angle: float
    peak_height: float
    descent_angle: float

    spin: float
    spin_axis: float

    ball_speed: float

    horizontal_angle: float

    carry: float


# ============================================================
# HELPERS
# ============================================================

def clamp(value, low, high):

    return max(low, min(value, high))


# ============================================================
# MAIN ANALYSIS CLASS
# ============================================================

class ShotAnalysis:

    def __init__(self, data: ShotData):

        self.data = data

        self.results = {}

        self.flags = []

        self.confidence = {}

        self.start_direction = ""
        self.curvature = ""

        self.shot_shape = ""
        self.flight_window = ""

        self.severity = ""

        self.miss_pattern = ""

    # ========================================================
    # ESTIMATIONS
    # ========================================================

    def estimate_smash_factor(self):

        low, high = CLUB_DATABASE[
            self.data.club
        ]["typical_smash"]

        mid = (low + high) / 2

        self.results["smash_factor"] = {
            "estimate": round(mid, 2),
            "range": (round(low, 2), round(high, 2))
        }

        self.confidence["Smash Factor"] = "HIGH"

    def estimate_club_speed(self):

        smash = self.results["smash_factor"]["estimate"]

        speed = self.data.ball_speed / smash

        self.results["club_speed"] = round(speed, 1)

    def estimate_dynamic_loft(self):

        loft = (
            self.data.launch_angle
            + 6
            + (self.data.peak_height / 40)
        )

        self.results["dynamic_loft"] = {
            "estimate": round(loft, 1),
            "tolerance": 3
        }

        self.confidence["Dynamic Loft"] = "MEDIUM"

    def estimate_attack_angle(self):

        aoa = (
            (self.data.launch_angle - 20) * 0.4
            - ((self.data.spin - 6000) / 1500)
        )

        aoa = clamp(aoa, -6, 6)

        self.results["attack_angle"] = {
            "estimate": round(aoa, 1),
            "tolerance": 2
        }

        self.confidence["Attack Angle"] = "LOW"

    def estimate_face_angle(self):

        face = self.data.horizontal_angle * 0.8

        self.results["face_angle"] = {
            "estimate": round(face, 1),
            "tolerance": 1.5
        }

        self.confidence["Face Angle"] = "MEDIUM"

    def estimate_club_path(self):

        face = self.results["face_angle"]["estimate"]

        path = face - (self.data.spin_axis * 0.7)

        self.results["club_path"] = {
            "estimate": round(path, 1),
            "tolerance": 2
        }

        self.confidence["Club Path"] = "LOW-MEDIUM"

    def estimate_face_to_path(self):

        face = self.results["face_angle"]["estimate"]

        path = self.results["club_path"]["estimate"]

        ftp = face - path

        self.results["face_to_path"] = {
            "estimate": round(ftp, 1),
            "tolerance": 1
        }

        self.confidence["Face-to-Path"] = "MEDIUM"

    # ========================================================
    # CLASSIFICATIONS
    # ========================================================

    def classify_start_direction(self):

        hla = self.data.horizontal_angle

        if hla < -6:
            self.start_direction = "HARD PULL"

        elif -6 <= hla < -2:
            self.start_direction = "PULL"

        elif -2 <= hla <= 2:
            self.start_direction = "STRAIGHT"

        elif 2 < hla <= 6:
            self.start_direction = "PUSH"

        else:
            self.start_direction = "BLOCK"

    def classify_curvature(self):

        axis = self.data.spin_axis

        magnitude = abs(axis)

        if magnitude < 3:
            self.severity = "LIGHT"

        elif magnitude < 7:
            self.severity = "MODERATE"

        else:
            self.severity = "SEVERE"

        if axis < -10:
            self.curvature = "HOOK"

        elif -10 <= axis < -4:
            self.curvature = "DRAW"

        elif -4 <= axis <= 4:
            self.curvature = "STRAIGHT"

        elif 4 < axis <= 10:
            self.curvature = "FADE"

        else:
            self.curvature = "SLICE"

    def classify_shot_shape(self):

        sd = self.start_direction
        cv = self.curvature

        if sd == "STRAIGHT" and cv == "STRAIGHT":
            self.shot_shape = "STRAIGHT SHOT"

        elif sd == "STRAIGHT":
            self.shot_shape = cv

        elif cv == "STRAIGHT":
            self.shot_shape = sd

        else:
            self.shot_shape = f"{sd} {cv}"

    def classify_trajectory(self):

        la = self.data.launch_angle
        peak = self.data.peak_height
        descent = self.data.descent_angle

        if la < 12:
            launch_profile = "LOW"

        elif la > 22:
            launch_profile = "HIGH"

        else:
            launch_profile = "MID"

        if peak < 18:
            height_profile = "FLAT"

        elif peak > 35:
            height_profile = "BALLOONING"

        else:
            height_profile = "TOUR"

        if descent > 45:
            landing = "SOFT LANDING"

        elif descent < 35:
            landing = "HOT LANDING"

        else:
            landing = "NORMAL LANDING"

        self.flight_window = (
            f"{launch_profile} / "
            f"{height_profile} / "
            f"{landing}"
        )

    def classify_miss_pattern(self):

        if "PUSH" in self.shot_shape:

            self.miss_pattern = (
                "Right miss tendency"
            )

        elif "BLOCK" in self.shot_shape:

            self.miss_pattern = (
                "Severe right miss tendency"
            )

        elif "PULL" in self.shot_shape:

            self.miss_pattern = (
                "Left miss tendency"
            )

        else:

            self.miss_pattern = (
                "Centered dispersion tendency"
            )

    # ========================================================
    # EFFICIENCY
    # ========================================================

    def calculate_efficiency(self):

        carry_eff = (
            self.data.carry
            / self.data.ball_speed
        )

        if carry_eff > 1.55:

            rating = "EXCELLENT"

        elif carry_eff > 1.42:

            rating = "GOOD"

        elif carry_eff > 1.30:

            rating = "AVERAGE"

        else:

            rating = "LOW"

        self.results["carry_efficiency"] = {
            "value": round(carry_eff, 2),
            "rating": rating
        }

    # ========================================================
    # FLAGS
    # ========================================================

    def generate_flags(self):

        if "PUSH DRAW" in self.shot_shape:

            self.flags.append(
                "Likely in-to-out path"
            )

        if "PULL FADE" in self.shot_shape:

            self.flags.append(
                "Out-to-in path tendency"
            )

        if "SLICE" in self.shot_shape:

            self.flags.append(
                "Excessive left-to-right curvature"
            )

        if "HOOK" in self.shot_shape:

            self.flags.append(
                "Excessive right-to-left curvature"
            )

        if self.data.launch_angle > 22:

            self.flags.append(
                "High launch tendency"
            )

        if (
            self.results["dynamic_loft"]["estimate"] > 30
        ):

            self.flags.append(
                "Excess dynamic loft"
            )

        if (
            self.data.launch_angle > 22
            and self.data.carry < 135
        ):

            self.flags.append(
                "Possible early release / scoop"
            )

        if self.data.descent_angle > 45:

            self.flags.append(
                "Good stopping power"
            )

    # ========================================================
    # MAIN COMPUTE
    # ========================================================

    def compute_all(self):

        self.estimate_smash_factor()

        self.estimate_club_speed()

        self.estimate_dynamic_loft()

        self.estimate_attack_angle()

        self.estimate_face_angle()

        self.estimate_club_path()

        self.estimate_face_to_path()

        self.classify_start_direction()

        self.classify_curvature()

        self.classify_shot_shape()

        self.classify_trajectory()

        self.classify_miss_pattern()

        self.calculate_efficiency()

        self.generate_flags()