# Apex Pit Optimizer: F1 Race Strategy Simulator

A Python-based discrete-event simulation engine that models Formula 1 race dynamics. This tool uses Object-Oriented Programming (OOP) to simulate the interplay between tire degradation, fuel weight penalties, and pit stop timing to determine optimal race strategies.

## 🚀 Key Features
- **Dynamic Performance Modeling:** Lap times are calculated using a multi-variable linear model factoring in base car pace, tire compound modifiers, and fuel-load weight.
- **Tire Degradation Curves:** Supports multiple compounds (Soft, Medium, Hard) with unique wear rates and "performance cliffs."
- **Resource Constraints:** Implements fuel-burn logic and DNF (Did Not Finish) conditions for energy management.
- **Strategic Decision Engine:** Supports manual and logic-based pit stop triggers to compare "undercut" and "overcut" strategies.

## 🛠️ Technical Concepts Applied
- **Object-Oriented Programming:** Encapsulation of `RaceCar` and `Tire` states.
- **State Machines:** The car’s state (fuel/wear) updates iteratively per lap.
- **Mathematical Modeling:** - **Tire Wear:** $Time_{penalty} = (100 - life) \times \text{decay\_rate}$
  - **Fuel Weight:** $Time_{penalty} = \text{fuel\_mass} \times 0.03s/kg$
- **Simulation Logic:** Stochastic-ready framework for Monte Carlo testing.

## 📦 Installation
1. Clone the repo:
   ```bash
   git clone [https://github.com/yourusername/f1-strategy-sim.git](https://github.com/yourusername/f1-strategy-sim.git)