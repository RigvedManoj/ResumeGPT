import os
import re
import sys

import pandas as pd
from aiFunctions import *

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


class Resume:
    def __init__(self, res_type, company, role, description, date=None):
        self.type = res_type
        self.company = company
        self.role = role
        self.description = description
        self.date = 'Aug 2024'
        if date:
            self.date = date


def get_resource_path(relative_path):
    """ Get the absolute path to the resource, works for both development and for PyInstaller. """
    # If running in a PyInstaller bundle, use _MEIPASS to find the resources
    if getattr(sys, 'frozen', False):
        # The application is frozen
        base_path = sys._MEIPASS
    else:
        # The application is not frozen
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_resume_points():
    resume_path = get_resource_path('metadata/Resume.csv')
    df = pd.read_csv(resume_path)
    columns_to_extract = ['id', 'description']
    resume_points = df[columns_to_extract].values.tolist()
    return resume_points


def get_best_resume_points(similarity_scores):
    dict_map = {}
    best_resume_points = []
    for score in similarity_scores:
        if score[0] not in dict_map:
            dict_map[score[0]] = True
            best_resume_points.append(score)
    return best_resume_points


def get_new_resume_point(job_point, resume_point):
    soft_prompt = """
    INSTRUCTIONS: Given below job description and a resume bullet point, rewrite the resume bullet point in XYZ format 
    to align more closely with the job description. Follow the below instructions strictly while rewriting the point:
    
    1. Generate a single bullet point (Do not mention X, Y, Z).
    2. Do not hallucinate any new information or add any embellishment to the resume bullet point.
    3. Wrap any numeric or skill in the bullet point with a latex textbf tag.
    4. Use synonyms of Developed instead of Developed.
    
    The XYZ format in resumes is a structured way to describe accomplishments and responsibilities. It focuses on three elements:
    X: What you did (action or task)
    Y: How you did it (method or approach)
    Z: The result or impact (outcome or benefit)
    
    JobDescription: {} 
    ResumeBulletPoint: {}
    """.format(job_point, resume_point)
    new_resume_point = generate_text(soft_prompt)
    [score, new_score] = compare_scores(job_point, resume_point, new_resume_point)
    # print("Old:", job_point, resume_point, score)
    # print("New:", job_point, new_resume_point, new_score)
    return new_resume_point


def escape_latex_characters(original_string):
    special_characters = ['#', '%', '&', '$', '_']
    for char in special_characters:
        # Use a regular expression to only escape characters that are not already escaped
        original_string = re.sub(r'(?<!\\)' + re.escape(char), r'\\' + char, original_string)
    return original_string


def aggregate_best_points(df2):
    resumes = []
    df = pd.read_csv('metadata/Resume.csv')
    df = pd.merge(df, df2, on='id')
    df = df.sort_values(by='score', ascending=False)

    agg_by_type = df.groupby('type')['score'].mean().reset_index()
    agg_by_type_sorted = agg_by_type.sort_values(by='score', ascending=False).reset_index(drop=True)

    for type_value in agg_by_type_sorted['type']:
        filtered_df = df[df['type'] == type_value]
        agg_by_role = filtered_df.groupby('role')['score'].mean().reset_index()
        agg_by_role_sorted = agg_by_role.sort_values(by='score', ascending=False).reset_index(drop=True)
        for role_value in agg_by_role_sorted['role']:
            filtered_df = df[(df['role'] == role_value) & (df['type'] == type_value)]
            description = ''
            count = 0
            for index, row in filtered_df.iterrows():
                value = "\\" + "item " + str(row['resume_point'])
                description += value + '\n'
                count += 1
                if count > 3:
                    break
            description = description[:-1]
            description = escape_latex_characters(description)
            resume_section = Resume(filtered_df.iloc[0]['type'], filtered_df.iloc[0]['company'],
                                    filtered_df.iloc[0]['role'], description, filtered_df.iloc[0]['date'])
            resumes.append(resume_section)
    return resumes
