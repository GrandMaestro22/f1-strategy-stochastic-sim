from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import random

from main import RaceCar, Track


AVAILABLE_GRID_PRESETS = [
    {"team": "McLaren", "driver": "Lando Norris"},
    {"team": "McLaren", "driver": "Oscar Piastri"},
    {"team": "Ferrari", "driver": "Charles Leclerc"},
    {"team": "Ferrari", "driver": "Lewis Hamilton"},
    {"team": "Red Bull", "driver": "Max Verstappen"},
    {"team": "Red Bull", "driver": "Yuki Tsunoda"},
    {"team": "Mercedes", "driver": "George Russell"},
    {"team": "Mercedes", "driver": "Kimi Antonelli"},
    {"team": "Aston Martin", "driver": "Fernando Alonso"},
    {"team": "Aston Martin", "driver": "Lance Stroll"},
    {"team": "Alpine", "driver": "Pierre Gasly"},
    {"team": "Alpine", "driver": "Franco Colapinto"},
    {"team": "Haas", "driver": "Esteban Ocon"},
    {"team": "Haas", "driver": "Oliver Bearman"},
    {"team": "Williams", "driver": "Alexander Albon"},
    {"team": "Williams", "driver": "Carlos Sainz"},
    {"team": "Racing Bulls", "driver": "Liam Lawson"},
    {"team": "Racing Bulls", "driver": "Isack Hadjar"},
    {"team": "Sauber", "driver": "Nico Hulkenberg"},
    {"team": "Sauber", "driver": "Gabriel Bortoleto"},
    {"team": "Cadillac", "driver": "Sergio Perez"},
    {"team": "Cadillac", "driver": "Valtteri Bottas"},
]

STARTING_TYRES = ("Soft", "Medium", "Hard", "Inters", "Full_Wet")


@dataclass(frozen=True)
class SimulationResult:
    team: str
    driver: str
    starting_tire: str
    fuel_load: float
    laps: int
    best_lap_time: float
    best_lap_number: int
    total_time: float
    pit_count: int
    average_lap: float
    lap_times: list[float]


def make_timestamp(mode: str) -> str:
    if mode == "local":
        return datetime.now().astimezone().isoformat()
    return datetime.now(timezone.utc).isoformat()


def run_single_driver_simulation(
    team: str,
    driver: str,
    starting_tire: str,
    fuel_load: float,
    laps: int,
) -> SimulationResult:
    track = Track()
    car = RaceCar(team, driver, starting_tire, fuel_load)

    for _lap in range(1, laps + 1):
        prev_sc = track.safety_car
        track.update_weather()
        track.was_sc_last_lap = prev_sc and not track.safety_car
        car.drive_lap(track)
        car.pitted_this_lap = False

    best_lap_time = min(car.lap_times) if car.lap_times else 0.0
    best_lap_number = car.lap_times.index(best_lap_time) + 1 if car.lap_times else 0
    average_lap = sum(car.lap_times) / len(car.lap_times) if car.lap_times else 0.0

    return SimulationResult(
        team=team,
        driver=driver,
        starting_tire=starting_tire,
        fuel_load=fuel_load,
        laps=laps,
        best_lap_time=round(best_lap_time, 3),
        best_lap_number=best_lap_number,
        total_time=round(car.total_time, 3),
        pit_count=car.pit_count,
        average_lap=round(average_lap, 3),
        lap_times=[round(time, 3) for time in car.lap_times],
    )


def find_best_lap(
    team: str,
    driver: str,
    starting_tire: str,
    fuel_load: float,
    laps: int,
    trials: int = 10,
) -> SimulationResult:
    trials = max(1, trials)
    best_result: SimulationResult | None = None

    for _ in range(trials):
        result = run_single_driver_simulation(team, driver, starting_tire, fuel_load, laps)
        if best_result is None:
            best_result = result
            continue

        if result.best_lap_time < best_result.best_lap_time:
            best_result = result
            continue

        if result.best_lap_time == best_result.best_lap_time and result.total_time < best_result.total_time:
            best_result = result

    if best_result is None:
        raise RuntimeError("Strategy search did not produce a result")

    return best_result


def format_result(result: SimulationResult, trials: int) -> str:
    return (
        f"Team: {result.team}\n"
        f"Driver: {result.driver}\n"
        f"Starting Tire: {result.starting_tire}\n"
        f"Fuel Load: {result.fuel_load:.1f} kg\n"
        f"Laps Simulated: {result.laps}\n"
        f"Trials Evaluated: {trials}\n"
        f"Best Lap: {result.best_lap_time:.3f}s on lap {result.best_lap_number}\n"
        f"Average Lap: {result.average_lap:.3f}s\n"
        f"Total Time: {result.total_time:.3f}s\n"
        f"Pit Stops: {result.pit_count}\n"
    )