# Apex Pit Optimizer: F1 Race Strategy Simulator

A Python-based discrete-event simulation engine that models Formula 1 race dynamics. This tool uses **Object-Oriented Programming (OOP)** to simulate the interplay among tire degradation, fuel weight penalties, and pit-stop timing to determine optimal race strategies.

## 🚀 Key Features
- **Dynamic Performance Modeling:** Lap times are calculated using a multi-variable linear model factoring in base car pace, tire compound modifiers, and fuel-load weight.
- **Automated Strategy Optimizer:** Features a brute-force search algorithm that iterates through every possible pit window to identify the mathematically optimal strategy.
- **Stochastic Variance:** Uses Gaussian-style randomness to simulate driver inconsistency and varying track conditions.
- **Resource Constraints:** Implements fuel-burn logic and DNF (Did Not Finish) conditions for realistic energy management.

## 🛠️ Technical Concepts Applied

### Object-Oriented Programming (OOP)
The project is built on state encapsulation. The `RaceCar` class maintains its own fuel and timing data, while the `Tire` class manages its own degradation metrics. This modularity allows for easy expansion (e.g., adding a `Track` class or `Weather` effects).

### Brute-Force Optimization
The Strategy Optimizer implements a search algorithm that runs independent race simulations for every possible pit lap. By recording the `total_time` for each permutation, the program identifies the "Global Minimum"—the pit stop that results in the fastest race completion.

### Mathematical Modeling
The simulation uses the following formulas to bridge the gap between physical variables and race time:

**1. Tire Wear Penalty**
> $$Time_{penalty} = (100 - \text{life}) \times \text{decay rate}$$

**2. Fuel Weight Penalty**
> $$Time_{penalty} = \text{fuel mass} \times 0.03s/kg$$

**3. Stochastic Factor**
> $$Lap_{time} = \text{Base} + \text{Penalties} + \text{Random}(-0.1, 0.3)$$

### Containerization & DevOps
By implementing a **Dockerfile**, the application is encapsulated within a lightweight virtual environment. This eliminates "dependency drift" and ensures that the simulation's math and logic remain consistent regardless of the host operating system.

## 📦 Installation & Usage

1. **Clone the repository:(Option 1)**
   ```bash
   git clone [https://github.com/yourusername/f1-strategy-sim.git](https://github.com/yourusername/f1-strategy-sim.git)

2. **Run the simulation:**
   ``python main.py

**Option 2: Docker (Recommended)**

   Build the image:
    
    Bash
    docker build -t f1-sim .

   Run the container:
    
    Bash
    docker run f1-sim

## 📊 SAMPLE OUTPUT

--- Strategy Team: Calculating Optimal Window ---
SUGGESTED STRATEGY: Pit on Lap 24 for a projected 4120.45s total.

--- 50 Lap Race Start ---
LAP 10
Merc Pace: 842.15s | Fuel: 102.0kg
RB Pace: 845.30s | Fuel: 102.0kg

--- Kimi Antonelli is BOXING ---
...
The winner is Mercedes!

## Tracks & Future Roadmap

[ ] Data Visualization: Integrate matplotlib to graph the crossover points between different tire compounds.

[ ] Weather Engine: Implement dynamic track temperatures and rain conditions that alter grip coefficients.

[ ] Multi-Car Grid: Expand the simulation to handle 20+ cars with overtaking logic and "dirty air" penalties.
