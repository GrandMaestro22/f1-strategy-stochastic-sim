import random

TIRE_STATS = {
    "Soft": {"grip_penalty": 0.15, "base_modifier": -1.0},
    "Medium": {"grip_penalty": 0.08, "base_modifier": 0.0},
    "Hard": {"grip_penalty": 0.03, "base_modifier": 1.5}
}

class Tire:
    def __init__(self, compound):
        if compound not in TIRE_STATS:
            print(f"Error: {compound} is not a valid tire. Defaulting to Medium.")
            compound = "Medium"
        self.compound = compound
        self.life = 100
        self.penalty_rate = TIRE_STATS[self.compound]["grip_penalty"]

    def wear(self):
        self.life -= 5


def find_best_strategy(driver_name, compound_start, compound_end, total_laps):
    results = {}
    for pit_lap in range(1, total_laps):
        test_car = RaceCar("SimTeam", driver_name, compound_start, 130)
        for lap in range(1, total_laps + 1):
            test_car.drive_lap()
            if lap == pit_lap:
                # FIX 1: Pass silent=True here to stop the over-printing
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

    def calculate_lap_time(self):
        compound_speed = TIRE_STATS[self.current_tire.compound]["base_modifier"]

        wear_penalty = (100 - max(0, self.current_tire.life)) * self.current_tire.penalty_rate
        fuel_penalty = self.fuel * 0.03
        random_variance = random.uniform(-0.1, 0.3)
        return self.base_lap_time + wear_penalty + fuel_penalty + compound_speed + random_variance

    def pit_stop(self, new_compound, silent=False):
        self.total_time += 22.0
        if not silent:
            print(f"\n--- {self.driver_name} is BOXING ---")
        self.current_tire = Tire(new_compound)

    def burn_fuel(self):
        if self.fuel > 1.8:
            self.fuel -= 1.8
        else:
            self.fuel = 0

    def drive_lap(self):
        current_lap_time = self.calculate_lap_time()
        self.total_time += current_lap_time
        self.current_tire.wear()
        self.burn_fuel()
        return current_lap_time

    def lift_and_coast(self):
        # Driver saves fuel but loses 0.5s of pace
        self.fuel -= 1.2  # Reduced from 1.8
        self.total_time += 0.5
if __name__ == "__main__":
# 1. Run the Strategy Simulation first
    print("--- Strategy Team: Calculating Optimal Window ---")
    best_lap, best_time = find_best_strategy("Kimi Antonelli", "Soft", "Hard", 50)
    print(f"SUGGESTED STRATEGY: Pit on Lap {best_lap} for a projected {best_time:.2f}s total.\n")

    # 2. Set up the actual race
    mercedes = RaceCar("Mercedes", "Kimi Antonelli", "Soft", 120)
    red_bull = RaceCar("Red Bull", "Max Verstappen", "Hard", 120) # Bring Max back!

    print(f"--- 50 Lap Race Start ---")
    for lap in range(1, 51):
        mercedes.drive_lap()
        red_bull.drive_lap()

        # Execute the automated strategy
        if lap == best_lap:
            mercedes.pit_stop("Hard") # We want to see this one print!

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
