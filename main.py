import random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

TIRE_STATS = {
    "Soft": {
        "base_pace_mod": -1.0,  # Fastest base speed
        "wear_rate": 0.15,      # High wear
        "wet_efficiency": 0.1   # Terrible in rain
    },
    "Medium": {
        "base_pace_mod": 0.0,   # Neutral base
        "wear_rate": 0.08,      # Balanced wear
        "wet_efficiency": 0.15
    },
    "Hard": {
        "base_pace_mod": 1.5,   # Slowest base
        "wear_rate": 0.03,      # Lowest wear
        "wet_efficiency": 0.2
    },
    "Inters": {
        "base_pace_mod": 5.0,   # Naturally slow on dry track
        "wear_rate": 0.8,       # Wears fast on dry track
        "wet_efficiency": 0.95  # Great in rain
    },
    "Full_Wet": {
        "base_pace_mod": 10.0,  # Very slow on dry track
        "wear_rate": 1.2,       # Shreds on dry track
        "wet_efficiency": 1.0   # Perfect for rain
    }
}

def plot_tire_comparison(total_laps):
    plt.style.use('dark_background')

    compounds = ["Soft", "Medium", "Hard"]
    lap_data = {comp: [] for comp in compounds}
    laps = list(range(1, total_laps + 1))

    for comp in compounds:
        test_car = RaceCar("Sim", "Test", comp, 100)
        for lap in laps:
            lap_time = test_car.calculate_lap_time()
            lap_data[comp].append(lap_time)
            test_car.drive_lap()

    # 1. CREATE THE PLOT
    plt.figure(figsize=(12, 7))
    plt.plot(laps, lap_data["Soft"], label="Soft (Degradation)", color="#FF3333", lw=3)
    plt.plot(laps, lap_data["Medium"], label="Medium", color="#FFFF33", lw=3)
    plt.plot(laps, lap_data["Hard"], label="Hard (Endurance)", color="#FFFFFF", lw=3)

    # 2. ADD STYLE & LABELS
    plt.title("F1 Apex Optimizer: Tire Crossover Analysis", fontsize=16, color="cyan")
    plt.xlabel("Lap Number", fontsize=12)
    plt.ylabel("Lap Time (Seconds)", fontsize=12)
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
    plt.legend(facecolor='black', edgecolor='gray')
    plt.savefig("f1_strategy_plot.png", dpi=300)
    plt.close()

class Track:
    def __init__(self):
        self.wetness = 0.0  # 0.0 (Dry) to 1.0 (Flooded)
        self.rain_intensity = 0.0 # How hard it is currently raining
        
    def update_weather(self):
        # 1. Determine if a weather shift happens (5% chance per lap)
        if random.random() < 0.05:
            # If it's dry, start a random rain intensity
            if self.rain_intensity == 0:
                self.rain_intensity = random.uniform(0.1, 0.5) 
            else:
                # If already raining, it might stop or get heavier
                self.rain_intensity = max(0, self.rain_intensity + random.uniform(-0.2, 0.2))

        # 2. Update track wetness based on intensity
        if self.rain_intensity > 0:
            self.wetness = min(1.0, self.wetness + (self.rain_intensity * 0.2))
        else:
            # If no rain, the track naturally dries (0.05 per lap)
            self.wetness = max(0.0, self.wetness - 0.05)

    def get_condition(self):
        if self.wetness < 0.1: return "Dry"
        if self.wetness < 0.4: return "Damp"
        if self.wetness < 0.7: return "Wet"
        return "Extreme Wet"
    
    def check_strategy(self, tire_type):
        # The 'Crossover' logic
        if self.wetness > 0.5 and tire_type == "Slick":
            return "PIT FOR INTERS"

        if self.wetness < 0.2 and tire_type == "Inters":
            return "PIT FOR SLICKS"
        
        return "STAY OUT"
    
class Tire:
    def __init__(self, compound):
        if compound not in TIRE_STATS:
            print(f"Error: {compound} is not a valid tire. Defaulting to Medium.")
            compound = "Medium"
        self.compound = compound
        self.life = 100
        self.wear_rate = TIRE_STATS[self.compound]["wear_rate"]

    def wear(self):
        self.life = max(0.0, self.life - (self.wear_rate * 5.0))


def find_best_strategy(driver_name, compound_start, compound_end, total_laps):
    results = {}
    for pit_lap in range(1, total_laps):
        test_car = RaceCar("SimTeam", driver_name, compound_start, 130)
        for lap in range(1, total_laps + 1):
            test_car.drive_lap()
            if lap == pit_lap:
                test_car.pit_stop(compound_end, silent=True)
        results[pit_lap] = test_car.total_time

    best_lap = min(results, key=results.get)
    best_time = results[best_lap]
    return best_lap, best_time

class RaceCar:
    def __init__(self, team, driver_name, tire_compound, fuel):
        self.team = team
        self.driver_name = driver_name
        self.current_tire = Tire(tire_compound)
        self.base_lap_time = 80.0
        self.total_time = 0.0
        self.fuel = fuel

        self.current_lap_on_tire = 1

    @property
    def tire_type(self):
        return self.current_tire.compound

    def calculate_lap_time(self, track=None):
        if track is None:
            track = Track()

        base_time = 85.0
        stats = TIRE_STATS[self.current_tire.compound]
        weather_gap = (1.0 - stats["wet_efficiency"]) * track.wetness * 30.0
        wear_penalty = self.current_lap_on_tire * stats["wear_rate"]

        if self.current_tire.compound in ["Inters", "Full_Wet"] and track.wetness < 0.2:
            wear_penalty *= 2.0

        fuel_penalty = self.fuel * 0.03
        randomness = random.uniform(-0.1, 0.3)

        return base_time + stats["base_pace_mod"] + weather_gap + wear_penalty + fuel_penalty + randomness

    def pit_stop(self, new_compound, silent=False):
        self.total_time += 22.0
        if not silent:
            print(f"\n--- {self.driver_name} is BOXING ---")
        self.current_tire = Tire(new_compound)
        self.current_lap_on_tire = 1

    def burn_fuel(self):
        if self.fuel > 1.8:
            self.fuel -= 1.8
        else:
            self.fuel = 0

    def drive_lap(self, track=None):
        current_lap_time = self.calculate_lap_time(track)
        self.total_time += current_lap_time
        self.current_tire.wear()
        self.burn_fuel()
        self.current_lap_on_tire += 1
        return current_lap_time

    def lift_and_coast(self):
        self.fuel -= 1.2  
        self.total_time += 0.5

    def decide_pit_stop(self, track):
        """
        The car looks at the Track object to decide if it needs
        to change tires based on the crossover point.
        """
        if track.wetness > 0.5 and self.tire_type == "Slick":
            print(f"[{self.driver_name}] Track is too wet! Pitting for INTERS.")
            self.current_tire = Tire("Inters")
            self.current_lap_on_tire = 1
            return True

        if track.wetness < 0.2 and self.tire_type == "Inters":
            print(f"[{self.driver_name}] Track is drying! Pitting for SLICKS.")
            self.current_tire = Tire("Soft")
            self.current_lap_on_tire = 1
            return True

        return False
        

if __name__ == "__main__":
    plot_tire_comparison(50)
    # 1. Run the Strategy Simulation
    print("--- Strategy Team: Calculating Optimal Window ---")
    best_lap, best_time = find_best_strategy("Kimi Antonelli", "Soft", "Hard", 50)
    print(f"SUGGESTED STRATEGY: Pit on Lap {best_lap} for a projected {best_time:.2f}s total.\n")

    # 2. Set up the actual race
    mercedes = RaceCar("Mercedes", "Kimi Antonelli", "Soft", 120)
    red_bull = RaceCar("Red Bull", "Max Verstappen", "Hard", 120)

    print(f"--- 50 Lap Race Start ---")
    for lap in range(1, 51):
        mercedes.drive_lap()
        red_bull.drive_lap()

        if lap == best_lap:
            mercedes.pit_stop("Hard")

        # Progress reporting
        if lap % 10 == 0:
            print(f"\nLAP {lap}")
            print(f"Merc Pace: {mercedes.total_time:.2f}s | Fuel: {mercedes.fuel:.1f}kg")
            print(f"RB Pace: {red_bull.total_time:.2f}s | Fuel: {red_bull.fuel:.1f}kg")

        # DNF Check
        if mercedes.fuel <= 0 or red_bull.fuel <= 0:
            print("\n--- CRITICAL: FUEL DEPLETED ---")
            break

    print("\n--- Final Result ---")
    winner = "Mercedes" if mercedes.total_time < red_bull.total_time else "Red Bull"
    print(f"The winner is {winner}!")
