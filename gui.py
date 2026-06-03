from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from strategy_engine import AVAILABLE_GRID_PRESETS, STARTING_TYRES, find_best_lap, format_result


class StrategyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("F1 Strategy Simulator")
        self.geometry("1180x760")
        self.minsize(1080, 700)

        self._preset_lookup = {
            f"{preset['team']} - {preset['driver']}": preset for preset in AVAILABLE_GRID_PRESETS
        }

        self.preset_var = tk.StringVar()
        self.team_var = tk.StringVar()
        self.driver_var = tk.StringVar()
        self.tire_var = tk.StringVar(value="Soft")
        self.fuel_var = tk.DoubleVar(value=100.0)
        self.laps_var = tk.IntVar(value=25)
        self.trials_var = tk.IntVar(value=10)
        self.status_var = tk.StringVar(value="Choose a preset and run the strategy search.")

        self._build_style()
        self._build_layout()
        self._set_preset(next(iter(self._preset_lookup)))

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#10151f")
        style.configure("Header.TFrame", background="#151c2b")
        style.configure("TLabel", background="#10151f", foreground="#edf2ff", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#151c2b", foreground="#ffffff", font=("Segoe UI Semibold", 20))
        style.configure("SubTitle.TLabel", background="#151c2b", foreground="#b8c2db", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI Semibold", 10), padding=8)
        style.configure("TCombobox", padding=5)
        style.configure("TLabelframe", background="#10151f", foreground="#edf2ff")
        style.configure("TLabelframe.Label", background="#10151f", foreground="#edf2ff", font=("Segoe UI Semibold", 10))

    def _build_layout(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame", padding=(24, 18))
        header.pack(fill="x")

        ttk.Label(header, text="F1 Strategy Lab", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Pick a grid slot, tune fuel and tyres, then search for the fastest lap in a stochastic simulation.",
            style="SubTitle.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        content = ttk.Frame(self, padding=18)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        controls = ttk.LabelFrame(content, text="Strategy Controls", padding=16)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 14))

        ttk.Label(controls, text="Grid preset").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.preset_combo = ttk.Combobox(
            controls,
            textvariable=self.preset_var,
            values=list(self._preset_lookup.keys()),
            state="readonly",
            width=32,
        )
        self.preset_combo.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

        ttk.Label(controls, text="Team").grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Entry(controls, textvariable=self.team_var, width=34).grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(controls, text="Driver").grid(row=4, column=0, sticky="w", pady=(0, 4))
        ttk.Entry(controls, textvariable=self.driver_var, width=34).grid(row=5, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(controls, text="Starting tire").grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.tire_combo = ttk.Combobox(
            controls,
            textvariable=self.tire_var,
            values=list(STARTING_TYRES),
            state="readonly",
            width=32,
        )
        self.tire_combo.grid(row=7, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(controls, text="Fuel load (kg)").grid(row=8, column=0, sticky="w", pady=(0, 4))
        ttk.Spinbox(controls, from_=0.0, to=110.0, increment=0.5, textvariable=self.fuel_var, width=15).grid(
            row=9, column=0, sticky="ew", pady=(0, 12)
        )

        ttk.Label(controls, text="Laps to simulate").grid(row=10, column=0, sticky="w", pady=(0, 4))
        ttk.Spinbox(controls, from_=1, to=150, increment=1, textvariable=self.laps_var, width=15).grid(
            row=11, column=0, sticky="ew", pady=(0, 12)
        )

        ttk.Label(controls, text="Search trials").grid(row=12, column=0, sticky="w", pady=(0, 4))
        ttk.Spinbox(controls, from_=1, to=50, increment=1, textvariable=self.trials_var, width=15).grid(
            row=13, column=0, sticky="ew", pady=(0, 16)
        )

        self.run_button = ttk.Button(controls, text="Run Strategy Search", command=self._run_strategy)
        self.run_button.grid(row=14, column=0, sticky="ew")

        ttk.Label(
            controls,
            text="The simulation runs several stochastic trials and keeps the run with the best lap.",
            wraplength=300,
            foreground="#b8c2db",
        ).grid(row=15, column=0, sticky="w", pady=(16, 0))

        results = ttk.Frame(content)
        results.grid(row=0, column=1, sticky="nsew")
        results.rowconfigure(1, weight=1)
        results.columnconfigure(0, weight=1)

        ttk.Label(results, textvariable=self.status_var).grid(row=0, column=0, sticky="ew", pady=(0, 10))

        plot_frame = ttk.LabelFrame(results, text="Lap Time Chart", padding=12)
        plot_frame.grid(row=1, column=0, sticky="nsew")
        plot_frame.rowconfigure(0, weight=1)
        plot_frame.columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(7.8, 4.8), dpi=100, facecolor="#f7f9fc")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Run a simulation to populate the chart")
        self.ax.set_xlabel("Lap")
        self.ax.set_ylabel("Lap time (s)")
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.draw()

        output_frame = ttk.LabelFrame(results, text="Strategy Output", padding=12)
        output_frame.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        output_frame.rowconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_frame,
            height=11,
            wrap="word",
            bg="#f7f9fc",
            fg="#0f172a",
            relief="flat",
            font=("Consolas", 10),
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_text.insert("1.0", "Results will appear here after a run.")
        self.output_text.configure(state="disabled")

    def _set_preset(self, preset_name: str) -> None:
        self.preset_var.set(preset_name)
        preset = self._preset_lookup[preset_name]
        self.team_var.set(preset["team"])
        self.driver_var.set(preset["driver"])

    def _on_preset_selected(self, _event: tk.Event) -> None:
        preset_name = self.preset_var.get()
        if preset_name in self._preset_lookup:
            self._set_preset(preset_name)

    def _run_strategy(self) -> None:
        team = self.team_var.get().strip()
        driver = self.driver_var.get().strip()
        tire = self.tire_var.get().strip()

        if not team or not driver:
            messagebox.showerror("Missing selection", "Please choose a team and driver.")
            return

        try:
            fuel = float(self.fuel_var.get())
            laps = int(self.laps_var.get())
            trials = int(self.trials_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid input", "Fuel, laps, and trials must be numeric values.")
            return

        if laps < 1 or trials < 1:
            messagebox.showerror("Invalid input", "Laps and trials must both be at least 1.")
            return

        self.status_var.set("Running strategy search...")
        self.run_button.configure(state="disabled")
        self.update_idletasks()

        try:
            result = find_best_lap(team, driver, tire, fuel, laps, trials=trials)
        except Exception as exc:  # noqa: BLE001 - show the user the failure in the GUI
            messagebox.showerror("Simulation error", str(exc))
            self.status_var.set("Simulation failed.")
            self.run_button.configure(state="normal")
            return

        self._render_output(format_result(result, trials))
        self._render_chart(result.lap_times, result.best_lap_number, result.best_lap_time)
        self.status_var.set(f"Best lap found: {result.best_lap_time:.3f}s on lap {result.best_lap_number}")
        self.run_button.configure(state="normal")

    def _render_output(self, summary: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", summary)
        self.output_text.configure(state="disabled")

    def _render_chart(self, lap_times: list[float], best_lap_number: int, best_lap_time: float) -> None:
        self.ax.clear()
        laps = list(range(1, len(lap_times) + 1))
        self.ax.plot(laps, lap_times, color="#1d4ed8", linewidth=2, marker="o", markersize=3)
        self.ax.scatter([best_lap_number], [best_lap_time], color="#dc2626", s=70, zorder=5, label="Best lap")
        self.ax.set_title("Lap times from the best simulation run")
        self.ax.set_xlabel("Lap")
        self.ax.set_ylabel("Lap time (s)")
        self.ax.grid(True, alpha=0.18)
        self.ax.legend(loc="best")
        self.figure.tight_layout()
        self.canvas.draw()


def launch_app() -> None:
    StrategyApp().mainloop()


if __name__ == "__main__":
    launch_app()