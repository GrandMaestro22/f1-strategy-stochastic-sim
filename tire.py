from constants import TIRE_STATS


class Tire:
    def __init__(self, compound: str):
        if compound not in TIRE_STATS:
            raise ValueError(f"Invalid tire compound: {compound}")
        self.compound = compound
        self.life = 100.0
        self.wear_rate = TIRE_STATS[self.compound]["wear_rate"]

    def wear(self):
        self.life = max(0.0, self.life - (self.wear_rate * 5.0))