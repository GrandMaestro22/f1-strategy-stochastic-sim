import random
import csv
from datetime import datetime, timezone
import argparse
import matplotlib.pyplot as plt

# Tire compound performance parameters.
# - base_pace_mod: additive lap-time modifier for compound (sec)
# - wear_rate: how quickly grip/time degrades per lap on that compound
# - wet_efficiency: how well the compound performs on wet track (1.0 is ideal in rain)
TIRE_STATS = {
    "Soft": {"base_pace_mod": -1.0, "wear_rate": 0.15, "wet_efficiency": 0.1},
    "Medium": {"base_pace_mod": 0.0, "wear_rate": 0.08, "wet_efficiency": 0.15},
    "Hard": {"base_pace_mod": 1.5, "wear_rate": 0.03, "wet_efficiency": 0.2},
    "Inters": {"base_pace_mod": 5.0, "wear_rate": 0.8, "wet_efficiency": 0.95},
    "Full_Wet": {"base_pace_mod": 10.0, "wear_rate": 1.2, "wet_efficiency": 1.0}
}

class Track:
    def __init__(self):
        # Current track wetness (0.0 dry -> 1.0 fully flooded)
        self.wetness = 0.0
        # Instantaneous rain intensity (used to change wetness over time)
        self.rain_intensity = 0.0
        # Whether a Safety Car period is active
        self.safety_car = False
        
    def update_weather(self):
        # 1. Weather shifts (5% chance)
        if random.random() < 0.05:
            if self.rain_intensity == 0:
                self.rain_intensity = random.uniform(0.1, 0.5) 
            else:
                self.rain_intensity = max(0, self.rain_intensity + random.uniform(-0.2, 0.2))

        # 2. Update wetness
        if self.rain_intensity > 0:
            self.wetness = min(1.0, self.wetness + (self.rain_intensity * 0.2))
        else:
            self.wetness = max(0.0, self.wetness - 0.05)
            
        # 3. Safety Car (2% chance to deploy, 30% chance to end)
        if not self.safety_car and random.random() < 0.02:
            self.safety_car = True
            print("\n⚠️ SAFETY CAR DEPLOYED! ⚠️")
        elif self.safety_car and random.random() < 0.3:
            self.safety_car = False
            print("\n🟢 SAFETY CAR ENDING - RACE RESUMED 🟢")

class RaceCar:
    def __init__(self, team, driver_name, tire_compound, fuel):
        self.team = team
        self.driver_name = driver_name
        # Tire currently fitted to the car (string matching TIRE_STATS keys)
        self.tire_type = tire_compound
        # Laps completed on the current set of tires
        self.current_lap_on_tire = 0
        # Accumulated race time (seconds)
        self.total_time = 0.0
        # Fuel remaining (kg) — used to apply a small fuel-weight penalty per lap
        self.fuel = fuel
        # Whether this car pitted during the current lap (reset after logging)
        self.pitted_this_lap = False
        # Per-driver telemetry and counters
        self.lap_times = []
        self.pit_count = 0
        self.cumulative_pit_time = 0.0
        self.fastest_lap = None

    def calculate_lap_time(self, track):
        # If Safety Car is active, laps are slow and fairly consistent
        if track.safety_car:
            return 110.0 + random.uniform(0.1, 0.5)

        # Base tire/track calculations
        stats = TIRE_STATS[self.tire_type]
        # Weather penalty scales with how poorly the tire handles wet conditions
        weather_gap = (1.0 - stats["wet_efficiency"]) * track.wetness * 30.0
        # Tire wear penalty grows with the number of laps on the tyre
        wear_penalty = (self.current_lap_on_tire * stats["wear_rate"])

        # Intermediates / full wets wear much faster on a dry track
        if self.tire_type in ["Inters", "Full_Wet"] and track.wetness < 0.2:
            wear_penalty *= 2.0

        # Final lap time is base + compound modifier + weather + wear
        return 85.0 + stats["base_pace_mod"] + weather_gap + wear_penalty

    def drive_lap(self, track):
        # Check strategy before driving
        self.decide_pit_stop(track)
        
        lap_time = self.calculate_lap_time(track)
        if not track.safety_car and getattr(track, 'was_sc_last_lap', False):
            lap_time += 1.0
        self.total_time += lap_time
        self.current_lap_on_tire += 1
        self.fuel -= 1.8

        # record per-lap telemetry
        self.lap_times.append(lap_time)
        if self.fastest_lap is None or lap_time < self.fastest_lap:
            self.fastest_lap = lap_time

        return lap_time

    def pit_stop(self, new_compound, track, silent=False):
        # Pit stops are quicker under Safety Car conditions
        time_loss = 12.0 if track.safety_car else 22.0
        self.total_time += time_loss

        if not silent:
            status = " (CHEAP STOP)" if track.safety_car else ""
            print(f"[{self.driver_name}] BOX BOX for {new_compound}{status}")

        # Fit the new compound and reset tyre lap counter
        self.tire_type = new_compound
        self.current_lap_on_tire = 0
        # Mark that a pit happened this lap (caller will clear after logging)
        self.pitted_this_lap = True
        # record pit stats
        self.pit_count += 1
        self.cumulative_pit_time += time_loss

    def decide_pit_stop(self, track):
        # 1. Rain Logic
        # Switch to intermediates/full wets when track crosses a wetness threshold
        if track.wetness > 0.5 and self.tire_type not in ["Inters", "Full_Wet"]:
            self.pit_stop("Inters", track)
        # Switch back to a dry compound once the track is sufficiently dry
        elif track.wetness < 0.2 and self.tire_type in ["Inters", "Full_Wet"]:
            self.pit_stop("Medium", track)

        # Opportunistic Safety Car stop: if SC present and tyres are fairly worn
        elif track.safety_car and self.current_lap_on_tire > 15:
            self.pit_stop("Soft", track)

def save_race_results(filename, race_data):
    # Persist a CSV telemetry file with extended headers including timestamp
    keys = [
        "Lap", "Driver", "Tire", "LapTime", "TrackWetness",
        "RaceTime", "Fuel", "Pit", "Timestamp"
    ]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(race_data)
    print(f"\nSaved results to {filename}")


def save_per_driver_csvs(history):
    # Write one CSV per driver by filtering the full history
    drivers = {}
    for row in history:
        drivers.setdefault(row["Driver"], []).append(row)

    for driver, rows in drivers.items():
        safe_name = driver.replace(" ", "_")
        fname = f"{safe_name}_telemetry.csv"
        # Use the same headers as the main telemetry export
        keys = ["Lap", "Driver", "Tire", "LapTime", "TrackWetness", "RaceTime", "Fuel", "Pit", "Timestamp"]
        with open(fname, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved per-driver telemetry to {fname}")


def save_race_report(txt_fname, cars, report_format: str = "both"):
    # Produce a CSV summary and a human-readable text report
    csv_fname = "race_summary.csv"
    keys = ["Driver", "Team", "TotalTime", "PitCount", "CumulativePitTime", "FastestLap", "AverageLap"]
    rows = []
    winner = None
    best_time = None

    for car in cars:
        avg = round(sum(car.lap_times) / len(car.lap_times), 3) if car.lap_times else 0.0
        fastest = round(car.fastest_lap, 3) if car.fastest_lap is not None else 0.0
        rows.append({
            "Driver": car.driver_name,
            "Team": car.team,
            "TotalTime": round(car.total_time, 3),
            "PitCount": car.pit_count,
            "CumulativePitTime": round(car.cumulative_pit_time, 3),
            "FastestLap": fastest,
            "AverageLap": avg
        })

        if best_time is None or car.total_time < best_time:
            best_time = car.total_time
            winner = car

    # write CSV summary
    with open(csv_fname, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    # write textual report if requested
    if report_format in ("text", "both"):
        with open(txt_fname, "w") as f:
            f.write("Race Report\n")
            f.write("===========\n\n")
            f.write(f"Winner: {winner.driver_name} ({winner.team}) - Total Time: {round(winner.total_time,3)}s\n\n")
            for r in rows:
                f.write(f"{r['Driver']} ({r['Team']}): Total={r['TotalTime']}s, Pits={r['PitCount']}, Fastest={r['FastestLap']}s, Avg={r['AverageLap']}s\n")

    # write markdown report if requested (same content in markdown)
    if report_format in ("md", "both"):
        md_name = txt_fname.replace('.txt', '.md')
        with open(md_name, 'w') as f:
            f.write("# Race Report\n\n")
            f.write(f"**Winner:** {winner.driver_name} ({winner.team}) — **Total Time:** {round(winner.total_time,3)}s\n\n")
            f.write("| Driver | Team | Total Time (s) | Pits | Fastest Lap (s) | Avg Lap (s) |\n")
            f.write("|---|---:|---:|---:|---:|---:|\n")
            for r in rows:
                f.write(f"| {r['Driver']} | {r['Team']} | {r['TotalTime']} | {r['PitCount']} | {r['FastestLap']} | {r['AverageLap']} |\n")

    print(f"Saved race summary to {csv_fname} and {txt_fname} (md={report_format in ('md','both')})")


def _make_timestamp(mode: str) -> str:
    """Return an ISO timestamp string according to `mode`.

    mode: 'utc' for timezone-aware UTC, 'local' for local timezone
    """
    if mode == "local":
        return datetime.now().astimezone().isoformat()
    # default to timezone-aware UTC
    return datetime.now(timezone.utc).isoformat()


def run_simulation(laps: int = 50, ts_mode: str = "utc", report_format: str = "both"):
    track = Track()
    mercedes = RaceCar("Mercedes", "Kimi Antonelli", "Soft", 100)
    red_bull = RaceCar("Red Bull", "Max Verstappen", "Soft", 100)
    history = []

    # Main race loop: simulate each lap, update weather, run both cars,
    # record telemetry for each car every lap, and handle opportunistic SC stops.
    for lap in range(1, laps + 1):
        # Remember whether Safety Car was active last lap so cars can apply
        # post-SC adjustments (the drive_lap check uses `was_sc_last_lap`).
        prev_sc = track.safety_car

        # Update track conditions for this lap (may deploy or clear SC).
        track.update_weather()

        # Mark if Safety Car ended this lap (was active previous lap but not now)
        track.was_sc_last_lap = (prev_sc and not track.safety_car)

        # Drive both cars for this lap
        mer_time = mercedes.drive_lap(track)
        rb_time = red_bull.drive_lap(track)

        # Safety Car opportunistic pit logic (same checks as before)
        if track.safety_car:
            if mercedes.total_time < red_bull.total_time and mercedes.current_lap_on_tire > 12:
                mercedes.pit_stop("Soft", track)
            elif red_bull.current_lap_on_tire < 20:
                print(f"[{red_bull.driver_name}] Staying out to take the lead!")

        # Append telemetry rows for both drivers each lap, including
        # a wall-clock timestamp and cumulative race time.
        ts = _make_timestamp(ts_mode)

        history.append({
            "Lap": lap,
            "Driver": mercedes.driver_name,
            "Tire": mercedes.tire_type,
            "LapTime": round(mer_time, 3),
            "TrackWetness": round(track.wetness, 2),
            "RaceTime": round(mercedes.total_time, 3),
            "Fuel": round(mercedes.fuel, 2),
            "Pit": bool(mercedes.pitted_this_lap),
            "Timestamp": ts
        })
        # clear per-lap pit marker after logging
        mercedes.pitted_this_lap = False

        history.append({
            "Lap": lap,
            "Driver": red_bull.driver_name,
            "Tire": red_bull.tire_type,
            "LapTime": round(rb_time, 3),
            "TrackWetness": round(track.wetness, 2),
            "RaceTime": round(red_bull.total_time, 3),
            "Fuel": round(red_bull.fuel, 2),
            "Pit": bool(red_bull.pitted_this_lap),
            "Timestamp": ts
        })
        red_bull.pitted_this_lap = False

    save_race_results("race_telemetry.csv", history)
    # Also export per-driver files and a summary report
    save_per_driver_csvs(history)
    # write textual report and optionally markdown
    save_race_report("race_report.txt", [mercedes, red_bull], report_format=report_format)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run F1 strategy stochastic simulator")
    parser.add_argument("--laps", type=int, default=50, help="Number of laps to simulate")
    parser.add_argument("--timestamp-mode", choices=["utc", "local"], default="utc", help="Timestamp mode for telemetry")
    parser.add_argument("--report-format", choices=["text", "md", "both"], default="both", help="Format for race report output")
    args = parser.parse_args()

    run_simulation(laps=args.laps, ts_mode=args.timestamp_mode, report_format=args.report_format)