import os
import subprocess
import csv
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
MAIN = os.path.join(ROOT, 'main.py')

class TelemetryTest(unittest.TestCase):
    def test_sim_outputs(self):
        # Run the simulator for 3 laps to produce outputs
        cmd = ['python', MAIN, '--laps', '3', '--timestamp-mode', 'local', '--report-format', 'both']
        subprocess.check_call(cmd)

        # Check for main telemetry
        rt = os.path.join(ROOT, 'race_telemetry.csv')
        self.assertTrue(os.path.exists(rt), 'race_telemetry.csv missing')
        with open(rt, newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected = ['Lap','Driver','Tire','LapTime','TrackWetness','RaceTime','Fuel','Pit','Timestamp']
            self.assertEqual(headers, expected)

        # Check per-driver files
        kf = os.path.join(ROOT, 'Kimi_Antonelli_telemetry.csv')
        mf = os.path.join(ROOT, 'Max_Verstappen_telemetry.csv')
        self.assertTrue(os.path.exists(kf))
        self.assertTrue(os.path.exists(mf))

        # Check report files
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'race_report.txt')))
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'race_report.md')))

if __name__ == '__main__':
    unittest.main()
