GET_COMMAND_PROMPT = """
Acting as a unix sysadmin, please help this user with their task.  

They have asked: '{prompt_question}'

Please express the response inside of a JSON object, with the key 'response' and the value being the command you would run to help the user.

Only include the command, not the explanation.  An explanation can be included in the 'explanation' key of the json object if needed
"""

EXPLAIN_COMMAND_PROMPT = """
Please explain the command '{command}' in a way that a beginner can understand. 

Please include the explanation inside of a JSON object, with the key 'explanation' and the value being the explanation of the command.

If the command is potentially destrutive, set the "destructive" key to true.  If the command is not destructive, set the "destructive" key to false.
"""