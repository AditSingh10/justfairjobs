# Importing necessary libraries
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from aif360.algorithms.preprocessing import Reweighing
from aif360.metrics import BinaryLabelDatasetMetric
from aif360.datasets import BinaryLabelDataset

# Load the dataset containing job postings and candidate profiles
job_postings = pd.read_csv('job_postings.csv')  # Replace 'job_postings.csv' with the actual file name
candidate_profiles = pd.read_csv('candidate_profiles.csv')  # Replace 'candidate_profiles.csv' with the actual file name

# Preprocess the text data (e.g., skills and qualifications)
vectorizer = CountVectorizer()
job_skills_matrix = vectorizer.fit_transform(job_postings['skills'].values.astype('U'))
candidate_skills_matrix = vectorizer.transform(candidate_profiles['skills'].values.astype('U'))

# Compute cosine similarity between job skills and candidate skills
similarity_matrix = cosine_similarity(candidate_skills_matrix, job_skills_matrix)

# Find the best-matching job for each candidate
best_matches = []
for i in range(len(candidate_profiles)):
    candidate_name = candidate_profiles.iloc[i]['name']
    best_match_index = similarity_matrix[i].argmax()
    best_match_score = similarity_matrix[i].max()
    best_match_job = job_postings.iloc[best_match_index]['job_title']
    best_matches.append((candidate_name, best_match_job, best_match_score))

# Convert the similarity scores to binary labels (e.g., 1 for a match, 0 for no match)
binary_labels = [1 if score >= 0.5 else 0 for _, _, score in best_matches]

# Create a BinaryLabelDataset
dataset = pd.DataFrame({'label': binary_labels})
candidate_data = candidate_profiles.drop(columns='name')
dataset = BinaryLabelDataset(df=candidate_data, label_names=['label'], protected_attribute_names=None)

# Calculate the fairness metrics before bias mitigation
metric_orig = BinaryLabelDatasetMetric(dataset, unprivileged_groups=[{'label': 0}], privileged_groups=[{'label': 1}])
print("Fairness metrics before bias mitigation:")
print("Disparate Impact Ratio: ", metric_orig.disparate_impact())
print("Mean Difference: ", metric_orig.mean_difference())

# Apply reweighing to mitigate bias
reweighing = Reweighing(unprivileged_groups=[{'label': 0}], privileged_groups=[{'label': 1}])
dataset_transf = reweighing.fit_transform(dataset)

# Calculate the fairness metrics after bias mitigation
metric_transf = BinaryLabelDatasetMetric(dataset_transf, unprivileged_groups=[{'label': 0}], privileged_groups=[{'label': 1}])
print("Fairness metrics after bias mitigation:")
print("Disparate Impact Ratio: ", metric_transf.disparate_impact())
print("Mean Difference: ", metric_transf.mean_difference())

# Display the results
print("\nBest Job Matches:")
for candidate_name, best_match_job, best_match_score in best_matches:
    print(f"Candidate: {candidate_name}, Best Match: {best_match_job}, Similarity Score: {best_match_score:.2f}")
