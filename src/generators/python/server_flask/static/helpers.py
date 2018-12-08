import json
from flask import request

def run_method(method_arguments_names, interface_function):
    request_args = request.get_data()

    try:
        request_args = json.loads(request_args)
    except json.JSONDecodeError:
        return "Error: Could not parse request data"

    assert isinstance(request_args, dict)

    arguments = request_args.get("arguments")

    assert isinstance(arguments, dict)
    assert method_arguments_names == list(arguments.keys())

    exec_result = interface_function(**arguments)
    str_json = json.dumps(exec_result)

    return str_json
