import sys

import pyperclip

from resumeFunctions import *
from latexFunctions import *
from jobFunctions import *
import pandas as pd


def get_resume(job_description):
    #job_description = get_job_description()
    job_points = get_job_points(job_description)
    keywords = get_keywords(job_description)
    print(keywords)
    print(job_points)
    resume_points = get_resume_points()
    similarity_scores = check_similarity(resume_points, job_points)
    best_resume_points = get_best_resume_points(similarity_scores)
    revised_resume_points = []

    for i in range(len(best_resume_points)):
        new_resume_point = get_new_resume_point(best_resume_points[i][2], best_resume_points[i][1])
        row = [best_resume_points[i][0], new_resume_point, best_resume_points[i][2], best_resume_points[i][3]]
        revised_resume_points.append(row)

    df = pd.DataFrame(revised_resume_points, columns=['id', 'resume_point', 'job_description', 'score'])
    resumes = aggregate_best_points(df)
    fill_template('latexTemplates/DSTemplate.tex', resumes, 'DS.tex')


if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        # Read from clipboard instead of a file
        corpus = pyperclip.paste()
        if corpus:
            get_resume(corpus)
        else:
            print("Clipboard is empty.")
    except Exception as e:
        print(f"An error occurred: {e}")
