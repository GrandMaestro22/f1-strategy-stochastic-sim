# Apex Pit Optimizer: F1 Race Strategy Simulator

A Python-based discrete-event simulation engine that models Formula 1 race dynamics. This tool uses **Object-Oriented Programming (OOP)** to simulate the interplay between tire degradation, fuel weight penalties, and pit stop timing to determine optimal race strategies.

## 🚀 Key Features
- **Dynamic Performance Modeling:** Lap times are calculated using a multi-variable linear model factoring in base car pace, tire compound modifiers, and fuel-load weight.
- **Tire Degradation Curves:** Supports multiple compounds (Soft, Medium, Hard) with unique wear rates and "performance cliffs."
- **Resource Constraints:** Implements fuel-burn logic and DNF (Did Not Finish) conditions for energy management.
- **Strategic Decision Engine:** Supports manual and logic-based pit stop triggers.

## 🛠️ Technical Concepts Applied

### Object-Oriented Programming (OOP)
The project is built on the encapsulation of states. The `RaceCar` class maintains its own fuel and timing data, while the `Tire` class manages its own degradation metrics. This modularity allows for easy expansion (e.g., adding a `Track` class).

### State Machines & Iterative Logic
The simulation functions as a state machine where the car's state (fuel level and tire health) updates iteratively every lap. Each "state change" influences the output of the next lap's performance.

### Mathematical Modeling
The simulation uses the following formulas to bridge the gap between physical variables and race time:

**1. Tire Wear Penalty**
> $$Time_{penalty} = (100 - life) \times decay\_rate$$

**2. Fuel Weight Penalty**
> $$Time_{penalty} = fuel\_mass \times 0.03s/kg$$

## 📦 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/f1-strategy-sim.git](https://github.com/yourusername/f1-strategy-sim.git)

2. **Run the simulation:**
   ``python main.py

## 📊 SAMPLE OUTPUT

--- 70 Lap Race: Kimi Antonelli vs Max Verstappen ---
...
LAP 20
--- Kimi Antonelli is BOXING for Hards ---
Merc Total: 1650.45s | Fuel: 64.0kg
RB Total: 1642.12s | Fuel: 64.0kg

--- Final Result ---
The winner is Red Bull by 8.42 seconds!

## Tracks & Future Roadmap

    [ ] Stochastic Elements: Add a random noise factor to lap times to simulate driver error.

    [ ] Strategy Optimizer: An iterative script to automatically test every pit window to find the mathematical "Global Minimum."

    [ ] Data Visualization: Integrate matplotlib to graph the crossover points between different tire compounds.
