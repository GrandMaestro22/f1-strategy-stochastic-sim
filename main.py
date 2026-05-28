import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from constants import TIRE_STATS
from tire import Tire
from racecar import RaceCar
from track import Track

if __name__ == "__main__":
    def plot_tire_comparison(total_laps: int):
        plt.style.use("dark_background")
        compounds = ["Soft", "Medium", "Hard"]
        lap_data = {comp: [] for comp in compounds}
        laps = list(range(1, total_laps + 1))

        for comp in compounds:
            test_car = RaceCar("Sim", "Test", comp, fuel=120)
            track = Track()
            for _ in laps:
                lap_time = test_car.calculate_lap_time(track)
                lap_data[comp].append(lap_time)
                test_car.drive_lap(track)

        plt.figure(figsize=(12, 7))
        plt.plot(laps, lap_data["Soft"], label="Soft (Degradation)", color="#FF3333", lw=2)
        plt.plot(laps, lap_data["Medium"], label="Medium", color="#FFFF33", lw=2)
        plt.plot(laps, lap_data["Hard"], label="Hard (Endurance)", color="#FFFFFF", lw=2)
        plt.title("F1 Apex Optimizer: Tire Crossover Analysis", fontsize=16, color="cyan")
        plt.xlabel("Lap Number", fontsize=12)
        plt.ylabel("Lap Time (Seconds)", fontsize=12)
        plt.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)
        plt.legend(facecolor="black", edgecolor="gray")
        plt.savefig("f1_strategy_plot.png", dpi=300)
        plt.close()

    def find_best_strategy(driver_name: str, compound_start: str, compound_end: str, total_laps: int):
        results = {}
        for pit_lap in range(1, total_laps):
            test_car = RaceCar("SimTeam", driver_name, compound_start, fuel=130)
            track = Track()
            for lap in range(1, total_laps + 1):
                test_car.drive_lap(track)
                if lap == pit_lap:
                    test_car.pit_stop(compound_end, silent=True)
                track.update_weather()
            results[pit_lap] = test_car.total_time

        best_lap = min(results, key=results.get)
        return best_lap, results[best_lap]

    plot_tire_comparison(50)

    print("--- Strategy Team: Calculating Optimal Window ---")
    best_lap, best_time = find_best_strategy("Kimi Antonelli", "Soft", "Hard", 50)
    print(f"SUGGESTED STRATEGY: Pit on Lap {best_lap} for a projected {best_time:.2f}s total.\n")

    mercedes = RaceCar("Mercedes", "Kimi Antonelli", "Soft", fuel=120)
    red_bull = RaceCar("Red Bull", "Max Verstappen", "Hard", fuel=120)
    track = Track()

    print("--- 50 Lap Race Start ---")
    for lap in range(1, 51):
        track.update_weather()
        mercedes.drive_lap(track)
        red_bull.drive_lap(track)

        if lap == best_lap:
            mercedes.pit_stop("Hard")

        if lap % 10 == 0:
            print(f"\nLAP {lap}")
            print(f"Merc Pace: {mercedes.total_time:.2f}s | Fuel: {mercedes.fuel:.1f}kg")
            print(f"RB Pace: {red_bull.total_time:.2f}s | Fuel: {red_bull.fuel:.1f}kg")

        if mercedes.fuel <= 0 or red_bull.fuel <= 0:
            print("\n--- CRITICAL: FUEL DEPLETED ---")
            break

    print("\n--- Final Result ---")
    winner = "Mercedes" if mercedes.total_time < red_bull.total_time else "Red Bull"
    print(f"The winner is {winner}!")
