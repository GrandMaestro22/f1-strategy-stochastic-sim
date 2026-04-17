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

    def pit_stop(self, new_compound):
        self.total_time += 22.0
        print(f"\n--- {self.driver_name} is BOXING for {new_compound}s ---")
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
    mercedes = RaceCar("Mercedes", "Kimi Antonelli", "Soft", 120)
    red_bull = RaceCar("Red Bull", "Max Verstappen", "Hard", 120 )

    print(f"--- 70 Lap Race: {mercedes.driver_name} vs {red_bull.driver_name} ---")

    for lap in range(1, 51):
        # Drive laps
        mercedes.drive_lap()
        red_bull.drive_lap()

        # Strategy logic
        if mercedes.current_tire.compound == "Soft" and lap == 23:
            mercedes.pit_stop("Soft")

        # Status and DNF checks
        if lap % 10 == 0:
            print(f"\nLAP {lap}")
            print(f"Merc Total: {mercedes.total_time:.2f}s | Fuel: {mercedes.fuel:.1f}kg")
            print(f"RB Total: {red_bull.total_time:.2f}s | Fuel: {red_bull.fuel:.1f}kg")
            if mercedes.fuel < 10:
                print(f"--- WARNING: {mercedes.driver_name} LOW FUEL ({mercedes.fuel:.1f}kg) ---")

        if mercedes.fuel <= 0 or red_bull.fuel <= 0:
            dnf_driver = mercedes.driver_name if mercedes.fuel <= 0 else red_bull.driver_name
            print(f"\n--- CRITICAL: {dnf_driver} has run out of fuel and DNF'd! ---")
            break

    print("\n--- Final Result ---")
    if mercedes.fuel > 0 and red_bull.fuel > 0:
        winner = "Mercedes" if mercedes.total_time < red_bull.total_time else "Red Bull"
        gap = abs(mercedes.total_time - red_bull.total_time)
        print(f"The winner is {winner} by {gap:.2f} seconds!")
    else:
        print("The race ended in a DNF.")
