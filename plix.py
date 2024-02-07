import requests
import click
import sys
import termios
import tty
import subprocess
import subprocess
import sys
import json
import re
import os
import hashlib

from dotenv import load_dotenv

try:
    load_dotenv()
except:
    print("Couldn't load .env file, but just goin' for it anyway")

CACHE_DIR = '.openai_cache'
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

OPENAI_DOMAIN = "https://api.openai.com/v1/"

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

def call_openai_api(question):
    cache_key = question

    cache_result = check_openai_cache(cache_key)
    if cache_result:
        return cache_result.get('response')

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

def get_command_explanation(request, command):
    question = f"Explain what the command '{command}' does."
    response = call_openai_api(question)
    response_output = get_text_response(response)
    return response_output

def get_keystroke():
    # Save the current terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        # Set the terminal to raw mode
        tty.setraw(sys.stdin.fileno())
        # Read a single character from the user
        keystroke = sys.stdin.read(1)
        return keystroke
    finally:
        # Restore the terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def find_json_object(text):
    try:
        json_object = json.loads(text)
        return json_object
    except:
        pass
    json_match = re.search(r'\{.*?\}', text)
    if json_match:
        json_object = json.loads(json_match.group())
        return json_object
    else:
        return None

def get_command(prompt_question):
    PROMPT = f"""
    Acting as a unix sysadmin, please help this user with their task.  
    
    They have asked: '{prompt_question}'

    Please express the response inside of a JSON object, with the key 'response' and the value being the command you would run to help the user.

    Only include the command, not the explanation.  An explanation can be included in the 'explanation' key of the json object if needed
    """
    response = call_openai_api(PROMPT)
    response_output = get_text_response(response)
    json_object = find_json_object(response_output)
    if json_object:
        return json_object['response']
    else:
        print("We were unable to generate a response.  Please try again.")
        print(json.dumps(response, indent=4))
        return "FAILED"

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
        sys.stdout.flush()

    return process.poll()

def init():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


@click.command()
@click.argument('args', nargs=-1)
def main(args):
    init()
    # Merge non-named arguments into a string
    args_string = ' '.join(arg for arg in args if not arg.startswith('--'))


    proffered_command = get_command(args_string)
    while True:
        print(f"{proffered_command} ([R]un/[C]ancel/[E]xplain/[A]lter)")
        keystroke = get_keystroke()

        if keystroke.lower() == 'r':
            run_command(proffered_command)
            break
        elif keystroke.lower() == 'c':
            print("Canceling the command...")
        elif keystroke.lower() == 'e':
            print("Getting Explanation...")
            print(get_command_explanation(request=args_string, command=proffered_command))
        elif keystroke.lower() == 'a':  
            print("Altering the command...")
        elif keystroke.lower() == 'q':

            break



if __name__ == "__main__":
    main()

