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
from src.openai import call_openai_api, get_text_response, get_command, CACHE_DIR
from src.prompts import GET_COMMAND_PROMPT

from dotenv import load_dotenv

try:
    load_dotenv()
except:
    print("Couldn't load .env file, but just goin' for it anyway")



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


    proffered_command = get_command(args_string).command
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

