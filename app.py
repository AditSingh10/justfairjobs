from flask import Flask, render_template, request, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = 'master'  # Set a secret key for flash mes

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        hiring_or_looking = request.form['hiring_or_looking']
        email = request.form['email']
        password = request.form['password']

        # Perform user registration logic here
        # For this example, we'll just print the data and show a flash message
        print(f"Are you hiring or looking for a job?: {hiring_or_looking}")
        print(f"Email: {email}")
        print(f"Password: {password}")

        # Show a flash message to indicate successful registration
        flash('Registration successful!', 'success')

        # Redirect to the appropriate form based on the user's choice
        if hiring_or_looking == 'looking':
            return redirect(url_for('candidate_profile_form'))
        elif hiring_or_looking == 'hiring':
            return redirect(url_for('job_posting_form'))

    return render_template('register.html')

# Function to load data from JSON files
def load_job_postings():
    with open('job_postings.json', 'r') as file:
        job_postings = json.load(file)
    return job_postings

def load_candidate_profiles():
    with open('candidate_profiles.json', 'r') as file:
        candidate_profiles = json.load(file)
    return candidate_profiles

# Function to extract skills from text using basic NLP
def extract_skills(text):
    words = text.split()
    return [word.lower() for word in words]

# Function to preprocess data and extract skills
def preprocess_data(data):
    for item in data:
        if 'description' in item:
            item['skills'] = extract_skills(item['description'])
        else:
            item['skills'] = extract_skills(item['experience'])

def calculate_match_score(job_posting, candidate):
    # Convert both job posting and candidate skills to sets for faster comparison
    job_skills = set(job_posting['skills'])
    candidate_skills = set(candidate['skills'])
    
    # Calculate the number of matching skills
    matching_skills = job_skills.intersection(candidate_skills)
    
    # Calculate the match score as a percentage of matching skills out of the total required skills
    match_score = len(matching_skills) / len(job_skills) * 100
    return match_score

def find_best_matches(job_postings, candidate_profiles):
    matched_candidates = {}

    for job_posting in job_postings:
        best_match = None
        best_score = 0

        for candidate in candidate_profiles:
            match_score = calculate_match_score(job_posting, candidate)
            if match_score > best_score:
                best_match = candidate
                best_score = match_score

        if best_match is not None:
            matched_candidates[job_posting['job_id']] = {
                'job_posting': job_posting,
                'best_match_candidate': best_match,
                'match_score': best_score
            }

    return matched_candidates

@app.route('/job_posting_form', methods=['GET', 'POST'])
def job_posting_form():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills = request.form['skills'].split(',')

        job_posting = {
            'title': title,
            'description': description,
            'skills': [skill.strip() for skill in skills]
        }

        with open('job_postings.json', 'a') as file:
            json.dump(job_posting, file)
            file.write('\n')  # Add a newline after each job posting

        return redirect(url_for('job_posting_form'))

    return render_template('job_posting_form.html')

@app.route('/candidate_profile_form', methods=['GET', 'POST'])
def candidate_profile_form():
    if request.method == 'POST':
        name = request.form['name']
        experience = request.form['experience']
        skills = request.form['skills'].split(',')

        candidate_profile = {
            'name': name,
            'experience': experience,
            'skills': [skill.strip() for skill in skills]
        }

        with open('candidate_profiles.json', 'a') as file:
            json.dump(candidate_profile, file)
            file.write('\n')  # Add a newline after each candidate profile

        return redirect(url_for('candidate_profile_form'))

    return render_template('candidate_profile_form.html')

@app.route('/best_matches')
def best_matches():
    # Load data from JSON files and preprocess data
    job_postings = load_job_postings()
    candidate_profiles = load_candidate_profiles()
    # Find best matches for each job posting
    matched_candidates = find_best_matches(job_postings, candidate_profiles)

    # Truncate match scores to one decimal point and add percentage
    for match_data in matched_candidates.values():
        match_data['match_score'] = f"{match_data['match_score']:.1f}%"

    return render_template('best_matches.html', matched_candidates=matched_candidates)


if __name__ == '__main__':
    app.run(debug=True)