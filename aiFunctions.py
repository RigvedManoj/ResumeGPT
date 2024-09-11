import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def generate_text(prompt):
    api_key = ''
    endpoint = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7,
        'top_p': 0.5,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        'n': 1
    }
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print("Error:", response.text)
        return None


def compare_scores(job_point, resume_point, new_resume_point):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    job_embedding = model.encode(job_point).reshape(1, -1)
    resume_embedding = model.encode(resume_point).reshape(1, -1)
    new_resume_embedding = model.encode(new_resume_point).reshape(1, -1)
    score = cosine_similarity(resume_embedding, job_embedding)
    new_score = cosine_similarity(new_resume_embedding, job_embedding)
    return [score, new_score]


def check_similarity(resume_points, job_points):
    similarity_scores = []
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # get 2nd column from 2d list resume_points
    resume = [row[1] for row in resume_points]

    resume_embeddings = model.encode(resume)
    job_embeddings = model.encode(job_points)
    cosine_sim = cosine_similarity(resume_embeddings, job_embeddings)

    for i in range(len(resume_points)):
        for j in range(len(job_points)):
            similarity_scores.append([resume_points[i][0], resume_points[i][1], job_points[j], cosine_sim[i][j]])
    similarity_scores = sorted(similarity_scores, key=lambda x: x[3], reverse=True)
    return similarity_scores
