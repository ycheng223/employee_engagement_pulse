def generate_team_insights(team_data):
    """
    Analyzes a list of team member data to generate team-level insights.

    Args:
        team_data (list): A list of dictionaries, where each dictionary
                          represents a team member. Expected keys are 'name',
                          'tasks_completed', 'hours_worked', and
                          'satisfaction_score'.

    Returns:
        dict: A dictionary containing aggregated team metrics and insights.
              Returns an empty dictionary if the input data is empty.
    """
    if not team_data:
        return {}

    num_members = len(team_data)
    total_tasks = sum(member['tasks_completed'] for member in team_data)
    total_hours = sum(member['hours_worked'] for member in team_data)
    total_satisfaction_score = sum(member['satisfaction_score'] for member in team_data)

    # Find top and lowest performers on key metrics
    top_performer_by_tasks = max(team_data, key=lambda x: x['tasks_completed'])
    most_engaged_by_hours = max(team_data, key=lambda x: x['hours_worked'])
    lowest_satisfaction_member = min(team_data, key=lambda x: x['satisfaction_score'])

    # Calculate average and overall metrics
    avg_tasks = total_tasks / num_members if num_members > 0 else 0
    avg_hours = total_hours / num_members if num_members > 0 else 0
    avg_satisfaction = total_satisfaction_score / num_members if num_members > 0 else 0
    team_productivity = total_tasks / total_hours if total_hours > 0 else 0

    insights = {
        'team_size': num_members,
        'total_tasks_completed': total_tasks,
        'total_hours_worked': round(total_hours, 2),
        'average_tasks_per_member': round(avg_tasks, 2),
        'average_hours_per_member': round(avg_hours, 2),
        'average_satisfaction_score': round(avg_satisfaction, 2),
        'team_productivity_tasks_per_hour': round(team_productivity, 2),
        'top_performer_by_tasks': top_performer_by_tasks['name'],
        'most_engaged_by_hours': most_engaged_by_hours['name'],
        'member_with_lowest_satisfaction': lowest_satisfaction_member['name']
    }

    return insights