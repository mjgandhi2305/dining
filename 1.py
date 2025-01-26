import csv
import random
import string

# Function to generate a random username
def generate_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

# Function to generate a random team name
def generate_team_name():
    teams = ['TeamAlpha', 'TeamBeta', 'TeamGamma', 'TeamDelta', 'TeamEpsilon']
    return random.choice(teams)

# Create the CSV file
def create_csv(filename, num_users):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'TeamName'])  # Write the header row

        for _ in range(num_users):
            username = generate_username()
            team_name = generate_team_name()
            writer.writerow([username, team_name])

# Generate the users.csv file with 150 participants
create_csv('users.csv', 150)
