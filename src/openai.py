import requests
import os
import json
import hashlib


OPENAI_DOMAIN = "https://api.openai.com/v1/"
CACHE_DIR = '.openai_cache'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def call_openai_api(question, use_cache=True):
    cache_key = question

    cache_result = check_openai_cache(cache_key)
    if cache_result and use_cache:
        return cache_result.get('response')
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body={
        "model": "gpt-4",
        "messages": [{
            "role": "user",
            "content": question
        }
        ]
    }
    response = requests.post(OPENAI_DOMAIN + "chat/completions", json=body, headers=headers)

    return_data = {
        "question": question,
        "request": body,
        "response": response.json()
    }
    set_openai_cache(cache_key, return_data)
    return return_data.get('response')

def get_text_response(openai_response):
    return openai_response['choices'][0]['message']['content']



def generate_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def check_openai_cache(cache_string):
    cache_key = generate_hash(cache_string)

    cache_path = f"{CACHE_DIR}/{cache_key}.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r") as cache_file:
            cache_data = json.load(cache_file)
            return cache_data
    return None

def set_openai_cache(cache_string, cache_data):
    cache_key = generate_hash(cache_string)
    cache_path = f"{CACHE_DIR}/{cache_key}.json"
    with open(cache_path, "w") as cache_file:
        json.dump(cache_data, cache_file, indent=2)


