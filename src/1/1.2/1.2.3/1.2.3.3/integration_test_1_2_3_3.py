import unittest

# Implementation from Subtask 1.2.3.3.2
def detect_burnout_warnings(weekly_data):
    warnings = []
    lookback_period = 4
    
    if len(weekly_data) < lookback_period:
        return warnings

    recent_weeks = weekly_data[-lookback_period:]
    
    try:
        hours = [week['hours_worked'] for week in recent_weeks]
        tasks = [week['tasks_completed'] for week in recent_weeks]
        stress = [week['self_reported_stress'] for week in recent_weeks]
    except KeyError as e:
        return [f"Data format error: Missing key {e} in weekly record."]

    avg_hours = sum(hours) / lookback_period
    avg_stress = sum(stress) / lookback_period
    
    half_period = lookback_period // 2
    
    first_half_hours_avg = sum(hours[:half_period]) / half_period
    second_half_hours_avg = sum(hours[half_period:]) / half_period
    
    first_half_stress_avg = sum(stress[:half_period]) / half_period
    second_half_stress_avg = sum(stress[half_period:]) / half_period
    
    first_half_tasks_avg = sum(tasks[:half_period]) / half_period
    second_half_tasks_avg = sum(tasks[half_period:]) / half_period
    
    # Rule 1: Sustained high workload
    if avg_hours > 48:
        warnings.append(f"Sustained high workload: Average of {avg_hours:.1f} hours/week.")
        
    # Rule 2: Increasing workload trend
    if second_half_hours_avg > first_half_hours_avg and avg_hours > 42:
        warnings.append("Increasing trend in hours worked.")

    # Rule 3: Sustained high stress levels
    if avg_stress > 7:
        warnings.append(f"Sustained high stress: Average level is {avg_stress:.1f}/10.")
        
    # Rule 4: Increasing stress trend
    if second_half_stress_avg > first_half_stress_avg and avg_stress > 5:
        warnings.append("Increasing trend in self-reported stress.")
        
    # Rule 5: Decreased productivity despite high hours
    if second_half_tasks_avg < first_half_tasks_avg and avg_hours > 40:
        warnings.append("Productivity may be decreasing while hours remain high.")
        
    return warnings

class TestBurnoutWarningSystemIntegration(unittest.TestCase):
    """
    Integration tests for the burnout warning detection system.
    These tests simulate a continuous flow of weekly data to test how the detection
    function behaves over time, reflecting a more realistic use case.
    """

    def _create_week(self, hours, tasks, stress):
        """Helper function to create a weekly data dictionary."""
        return {'hours_worked': hours, 'tasks_completed': tasks, 'self_reported_stress': stress}

    def test_progressive_burnout_scenario_over_time(self):
        """
        Simulates an employee's data over several weeks, transitioning from a
        healthy state to a state of burnout, and verifies that the system
        raises the correct warnings at each stage.
        """
        # Initial data for several weeks - all healthy
        all_data = [
            self._create_week(40, 15, 3), # Week 1
            self._create_week(38, 14, 4), # Week 2
            self._create_week(41, 16, 3), # Week 3
        ]

        # Stage 1: Not enough data
        self.assertEqual(detect_burnout_warnings(all_data), [], "Should be no warnings with less than 4 weeks of data")

        # Stage 2: Baseline healthy state
        all_data.append(self._create_week(40, 15, 4)) # Week 4
        self.assertEqual(detect_burnout_warnings(all_data), [], "Should be no warnings for a healthy baseline")

        # Stage 3: Workload starts increasing
        all_data.append(self._create_week(45, 15, 5)) # Week 5
        # Recent data: [W2, W3, W4, W5] -> [38, 41, 40, 45]. Avg hours = 41.0. No warnings yet.
        self.assertEqual(detect_burnout_warnings(all_data), [], "A single high-hour week should not trigger warnings yet")

        # Stage 4: Workload trend becomes apparent, stress increases
        all_data.append(self._create_week(48, 14, 7)) # Week 6
        # Recent data: [W3, W4, W5, W6] -> [41, 40, 45, 48]. Avg hours = 43.5. Stress avg = 4.75.
        # Hours: first half avg=40.5, second half avg=46.5 -> Increasing trend.
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Increasing trend in hours worked.", warnings)
        
        # Stage 5: Sustained high workload, stress continues to rise, productivity drops
        all_data.append(self._create_week(50, 12, 8)) # Week 7
        # Recent data: [W4, W5, W6, W7] -> [40, 45, 48, 50]. Avg hours = 45.75. Stress avg = 6.0.
        # Stress: first half avg=4.5, second half avg=7.5 -> Increasing trend.
        # Tasks: first half avg=15, second half avg=13 -> Decreasing trend.
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 3)
        self.assertIn("Increasing trend in hours worked.", warnings)
        self.assertIn("Increasing trend in self-reported stress.", warnings)
        self.assertIn("Productivity may be decreasing while hours remain high.", warnings)

        # Stage 6: Full burnout state
        all_data.append(self._create_week(52, 10, 9)) # Week 8
        # Recent data: [W5, W6, W7, W8] -> [45, 48, 50, 52]. Avg hours = 48.75. Stress avg = 7.25.
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 5, "All burnout indicators should be active")
        self.assertIn("Sustained high workload: Average of 48.8 hours/week.", warnings)
        self.assertIn("Increasing trend in hours worked.", warnings)
        self.assertIn("Sustained high stress: Average level is 7.2/10.", warnings)
        self.assertIn("Increasing trend in self-reported stress.", warnings)
        self.assertIn("Productivity may be decreasing while hours remain high.", warnings)

    def test_recovery_scenario_over_time(self):
        """
        Simulates an employee recovering from a burnout state, verifying
        that warnings are gradually cleared as conditions improve.
        """
        # Stage 1: Start in a state of burnout (from previous test)
        all_data = [
            self._create_week(45, 15, 6), # Week 1
            self._create_week(48, 14, 7), # Week 2
            self._create_week(50, 12, 8), # Week 3
            self._create_week(52, 10, 9), # Week 4
        ]
        # Avg hours = 48.75, Avg stress = 7.5
        self.assertEqual(len(detect_burnout_warnings(all_data)), 5, "Should start with all 5 warnings")

        # Stage 2: Intervention begins - hours and stress reduce slightly
        all_data.append(self._create_week(44, 13, 6)) # Week 5
        # Recent data: [W2, W3, W4, W5] -> [48, 50, 52, 44]. Avg hours = 48.5. Stress avg = 7.5.
        # Trends for hours/tasks/stress are now decreasing, but sustained levels are high.
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 2, "Trend warnings should disappear, but sustained warnings remain")
        self.assertIn("Sustained high workload: Average of 48.5 hours/week.", warnings)
        self.assertIn("Sustained high stress: Average level is 7.5/10.", warnings)
        
        # Stage 3: Continued improvement
        all_data.append(self._create_week(41, 14, 5)) # Week 6
        # Recent data: [W3, W4, W5, W6] -> [50, 52, 44, 41]. Avg hours = 46.75. Stress avg = 7.0.
        # High workload warning should disappear as avg is now < 48. High stress is at the threshold, so it should also disappear.
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(warnings, [], "Sustained warnings should be cleared as averages drop below thresholds")

        # Stage 4 & 5: Fully recovered state
        all_data.append(self._create_week(40, 15, 4)) # Week 7
        all_data.append(self._create_week(39, 15, 4)) # Week 8
        # The lookback window is now entirely composed of healthy or improving data.
        self.assertEqual(detect_burnout_warnings(all_data), [], "System should report no warnings after full recovery")
        
    def test_system_resilience_to_bad_data_entry(self):
        """
        Tests the system's response to malformed data within the processing window
        and its ability to recover once the bad data is outside the lookback period.
        """
        # A stream of healthy data
        all_data = [
            self._create_week(40, 15, 4), # Week 1
            self._create_week(41, 14, 5), # Week 2
        ]
        
        # A malformed entry is added (missing 'self_reported_stress')
        all_data.append({'hours_worked': 40, 'tasks_completed': 12}) # Week 3
        all_data.append(self._create_week(42, 13, 5)) # Week 4

        # The system should report the data format error
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Data format error: Missing key 'self_reported_stress' in weekly record.", warnings)

        # Add another week of good data. The bad data is still in the lookback window.
        all_data.append(self._create_week(40, 15, 4)) # Week 5
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Data format error: Missing key 'self_reported_stress' in weekly record.", warnings)

        # Add one more week. The malformed entry from Week 3 is now outside the 4-week window.
        all_data.append(self._create_week(39, 16, 3)) # Week 6
        # Recent data: [W3(bad), W4, W5, W6] -> Still errors
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Data format error: Missing key 'self_reported_stress' in weekly record.", warnings)
        
        # Add one more week. The malformed entry is now definitely out of the window [W4, W5, W6, W7]
        all_data.append(self._create_week(40, 15, 4)) # Week 7
        warnings = detect_burnout_warnings(all_data)
        self.assertEqual(warnings, [], "System should recover and process normally once bad data is out of scope")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)