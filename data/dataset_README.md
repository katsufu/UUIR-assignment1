---
dataset_info:
  features:
    - name: recruitment_date
      dtype: string
    - name: opening_position
      dtype: string
    - name: description
      dtype: string
    - name: requirement
      dtype: string
    - name: keywords_for_recruitment
      sequence: string
    - name: cv
      dtype: string
    - name: experience_years
      dtype: int64
    - name: keywords_from_applicants
      sequence: string
    - name: result
      dtype: string
    - name: reason_for_result
      dtype: string
  splits:
    - name: train
      num_bytes: 0
      num_examples: 10000
configs:
  - config_name: default
    data_files:
      - split: train
        path: recruitment_data.json
---

# Fictional IT Recruitment Dataset

This dataset contains 10,000 synthetically generated recruitment records for a fictional IT company from 2020 to 2026. It is designed to be used for Information Retrieval and Classification tasks, such as predicting candidate acceptance based on their CV embeddings.

## Dataset Structure

Each record contains the following fields:
- `recruitment_date`: Date the recruitment took place (YYYY-MM-DD).
- `opening_position`: The title of the job position (e.g., Software Engineer, Data Scientist).
- `description`: A brief description of the job role.
- `requirement`: The minimum requirements for the position.
- `keywords_for_recruitment`: A list of required skills/keywords.
- `cv`: A synthetic candidate's curriculum vitae (CV) summary text.
- `experience_years`: The number of years of experience the candidate has.
- `keywords_from_applicants`: A list of skills/keywords found in the candidate's CV.
- `result`: The final recruitment decision ("Accepted" or "Rejected").
- `reason_for_result`: A brief explanation of why the candidate was accepted or rejected.

## Potential Use Cases
- Semantic Search: Finding candidates whose CVs closely match the job description.
- Text Classification: Training models to predict the `result` given the `cv` text.

## Generation
The data was generated using a custom Python script that pairs job requirements with randomized candidate profiles, introducing variations in experience and skill overlap.
