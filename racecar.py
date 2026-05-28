import random
from tire import Tire
from constants import TIRE_STATS
from track import Track


class RaceCar:
    def __init__(self, team: str, driver_name: str, tire_compound: str, fuel: float):
        self.team = team
        self.driver_name = driver_name
        self.current_tire = Tire(tire_compound)
        self.base_lap_time = 85.0
        self.total_time = 0.0
        self.fuel = fuel
        self.current_lap_on_tire = 1

    @property
    def tire_type(self):
        return self.current_tire.compound

    def calculate_lap_time(self, track: Track | None = None) -> float:
        if track is None:
            track = Track()

        stats = TIRE_STATS[self.current_tire.compound]
        weather_gap = (1.0 - stats["wet_efficiency"]) * track.wetness * 30.0
        wear_penalty = (self.current_lap_on_tire - 1) * stats["wear_rate"]
        if self.current_tire.compound in ["Inters", "Full_Wet"] and track.wetness < 0.2:
            wear_penalty *= 2.0

        fuel_penalty = max(0.0, self.fuel) * 0.03
        randomness = random.uniform(-0.1, 0.3)

        return self.base_lap_time + stats["base_pace_mod"] + weather_gap + wear_penalty + fuel_penalty + randomness

    def pit_stop(self, new_compound: str, silent: bool = False):
        self.total_time += 22.0
        if not silent:
            print(f"\n--- {self.driver_name} is BOXING ---")
        self.current_tire = Tire(new_compound)
        self.current_lap_on_tire = 1

    def burn_fuel(self):
        if self.fuel > 1.8:
            self.fuel -= 1.8
        else:
            self.fuel = 0.0

    def drive_lap(self, track: Track | None = None) -> float:
        if track is None:
            track = Track()
        lap_time = self.calculate_lap_time(track)
        self.total_time += lap_time
        self.current_tire.wear()
        self.burn_fuel()
        self.current_lap_on_tire += 1
        return lap_time

    def decide_pit_stop(self, track: Track) -> bool:
        if track.wetness > 0.5 and self.tire_type in ["Soft", "Medium", "Hard"]:
            print(f"[{self.driver_name}] Track is too wet! Pitting for INTERS.")
            self.pit_stop("Inters")
            return True
        if track.wetness < 0.2 and self.tire_type == "Inters":
            print(f"[{self.driver_name}] Track is drying! Pitting for SLICKS.")
            self.pit_stop("Soft")
            return True
        return False
