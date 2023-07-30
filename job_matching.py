import json

# Function to load data from JSON files
def load_job_postings():
    with open('job_postings.json', 'r') as file:
        job_postings = json.load(file)
    return job_postings

def load_candidate_profiles():
    with open('candidate_profiles.json', 'r') as file:
        candidate_profiles = json.load(file)
    return candidate_profiles

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

# Example usage:
if __name__ == "__main__":
    # Load data from JSON files
    job_postings = load_job_postings()
    candidate_profiles = load_candidate_profiles()

    # Find best matches for each job posting
    matched_candidates = find_best_matches(job_postings, candidate_profiles)

    # Print the best matches and match scores
    for job_id, match_data in matched_candidates.items():
        job_title = match_data['job_posting']['title']
        candidate_name = match_data['best_match_candidate']['name']
        match_score = match_data['match_score']
        print(f"Job Posting: {job_title}")
        print(f"Best Match Candidate: {candidate_name}")
        print(f"Match Score: {match_score:.2f}%")
        print("--------")
