import random


class Track:
    def __init__(self):
        self.wetness = 0.0
        self.rain_intensity = 0.0

    def update_weather(self):
        if random.random() < 0.05:
            if self.rain_intensity == 0:
                self.rain_intensity = random.uniform(0.1, 0.5)
            else:
                self.rain_intensity = max(0.0, self.rain_intensity + random.uniform(-0.2, 0.2))

        if self.rain_intensity > 0:
            self.wetness = min(1.0, self.wetness + (self.rain_intensity * 0.2))
        else:
            self.wetness = max(0.0, self.wetness - 0.05)

    def get_condition(self):
        if self.wetness < 0.1:
            return "Dry"
        if self.wetness < 0.4:
            return "Damp"
        if self.wetness < 0.7:
            return "Wet"
        return "Extreme Wet"

    def check_strategy(self, tire_type: str) -> str:
        if self.wetness > 0.5 and tire_type in ["Soft", "Medium", "Hard"]:
            return "PIT FOR INTERS"
        if self.wetness < 0.2 and tire_type == "Inters":
            return "PIT FOR SLICKS"
        return "STAY OUT"