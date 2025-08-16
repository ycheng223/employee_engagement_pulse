import unittest

# The implementation to test
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

class TestGenerateTeamInsights(unittest.TestCase):

    def setUp(self):
        """Set up a standard team data list for use in multiple tests."""
        self.standard_team_data = [
            {'name': 'Alice', 'tasks_completed': 10, 'hours_worked': 40, 'satisfaction_score': 8},
            {'name': 'Bob', 'tasks_completed': 15, 'hours_worked': 45, 'satisfaction_score': 7},
            {'name': 'Charlie', 'tasks_completed': 8, 'hours_worked': 35.5, 'satisfaction_score': 9}
        ]

    def test_normal_case_with_multiple_members(self):
        """
        Test the function with a typical list of team members.
        """
        insights = generate_team_insights(self.standard_team_data)
        
        # Expected calculations
        # total_tasks = 10 + 15 + 8 = 33
        # total_hours = 40 + 45 + 35.5 = 120.5
        # total_satisfaction = 8 + 7 + 9 = 24
        # avg_tasks = 33 / 3 = 11.0
        # avg_hours = 120.5 / 3 = 40.166...
        # avg_satisfaction = 24 / 3 = 8.0
        # productivity = 33 / 120.5 = 0.2738...
        
        expected_insights = {
            'team_size': 3,
            'total_tasks_completed': 33,
            'total_hours_worked': 120.5,
            'average_tasks_per_member': 11.00,
            'average_hours_per_member': 40.17,
            'average_satisfaction_score': 8.00,
            'team_productivity_tasks_per_hour': 0.27,
            'top_performer_by_tasks': 'Bob',
            'most_engaged_by_hours': 'Bob',
            'member_with_lowest_satisfaction': 'Bob'
        }
        self.assertEqual(insights, expected_insights)

    def test_empty_team_data(self):
        """
        Test the function with an empty list, expecting an empty dictionary.
        """
        insights = generate_team_insights([])
        self.assertEqual(insights, {})

    def test_single_member_team(self):
        """
        Test the function with a list containing only one team member.
        """
        single_member_team = [
            {'name': 'Dana', 'tasks_completed': 25, 'hours_worked': 40.0, 'satisfaction_score': 10}
        ]
        insights = generate_team_insights(single_member_team)
        expected_insights = {
            'team_size': 1,
            'total_tasks_completed': 25,
            'total_hours_worked': 40.0,
            'average_tasks_per_member': 25.0,
            'average_hours_per_member': 40.0,
            'average_satisfaction_score': 10.0,
            'team_productivity_tasks_per_hour': 0.63, # 25 / 40
            'top_performer_by_tasks': 'Dana',
            'most_engaged_by_hours': 'Dana',
            'member_with_lowest_satisfaction': 'Dana'
        }
        self.assertEqual(insights, expected_insights)

    def test_tie_breaker_behavior(self):
        """
        Test how ties are handled, expecting the first member in the list to be chosen.
        """
        team_data_with_ties = [
            {'name': 'Eve', 'tasks_completed': 20, 'hours_worked': 50, 'satisfaction_score': 5},
            {'name': 'Frank', 'tasks_completed': 20, 'hours_worked': 40, 'satisfaction_score': 6},
            {'name': 'Grace', 'tasks_completed': 10, 'hours_worked': 50, 'satisfaction_score': 5}
        ]
        insights = generate_team_insights(team_data_with_ties)
        # max() and min() return the first item found in case of a tie.
        self.assertEqual(insights['top_performer_by_tasks'], 'Eve')
        self.assertEqual(insights['most_engaged_by_hours'], 'Eve')
        self.assertEqual(insights['member_with_lowest_satisfaction'], 'Eve')

    def test_zero_hours_worked(self):
        """
        Test case where total hours worked is zero to ensure no division errors.
        """
        team_with_zero_hours = [
            {'name': 'Heidi', 'tasks_completed': 5, 'hours_worked': 0, 'satisfaction_score': 8},
            {'name': 'Ivan', 'tasks_completed': 3, 'hours_worked': 0, 'satisfaction_score': 7}
        ]
        insights = generate_team_insights(team_with_zero_hours)
        self.assertEqual(insights['total_hours_worked'], 0)
        # The implementation's ternary operator should result in 0 for productivity.
        self.assertEqual(insights['team_productivity_tasks_per_hour'], 0)
        self.assertEqual(insights['average_hours_per_member'], 0)
        # Verify other metrics are still calculated correctly.
        self.assertEqual(insights['team_size'], 2)
        self.assertEqual(insights['total_tasks_completed'], 8)
        self.assertEqual(insights['average_satisfaction_score'], 7.5)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)