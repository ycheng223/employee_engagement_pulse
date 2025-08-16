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