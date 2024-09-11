import os
import time
import subprocess
from aiFunctions import *

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


def get_job_points(job_description):
    soft_prompt = """
    Job Description: {} 
    INSTRUCTIONS: "Given the job description, give me atmost 10 requirements the company is looking for, ignoring degree, 
    location , years of experience and visa requirements. Give the requirements as bullet points. Give only the requirements and nothing else."
    """.format(job_description)
    generated_text = generate_text(soft_prompt).split('\n')
    job = [text.lstrip('- ').strip() for text in generated_text]
    return job


def get_keywords(job_description):
    soft_prompt = """
    Job Description: {} 
    INSTRUCTIONS: "Given the job description, give me around 10 keywords (skills,technologies, expertise) the company is 
    looking for, which i can put in the Skills section of my resume. Give the keywords as a list. Give only the keywords 
    and nothing else."
    """.format(job_description)
    generated_text = generate_text(soft_prompt).split('\n')
    job = [text.lstrip('- ').strip() for text in generated_text]
    return job


def get_job_description():
    file_path = 'temp_file.txt'
    with open(file_path, 'w') as f:
        pass

    notepad_process = subprocess.Popen(['notepad.exe', file_path])
    notepad_process.wait()

    while True:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            break
        except IOError:
            time.sleep(1)
    file_content = content
    os.remove(file_path)
    return file_content
