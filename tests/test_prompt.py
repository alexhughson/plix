import sys


import pytest

def test_commands():
    from plix import get_command, init
    init()
    matchups = [
        ["list ALL files in this directory with their permissions, including hidden files", "ls -la"],
        ["Show the disk usage of the system", "df -h"],
        ["edit git config to automatically set the remote branch to the branch with the same name on origin, and only push the current branch", "git config --global push.default current"],
        ["create a new python virtual environment in the folder venv", "python3 -m venv venv"]
    ]

    for [request, response] in matchups:
        code_response = get_command(request)
        assert code_response == response, f"Expected {response} but got {code_response} for the prompt: {request}"
