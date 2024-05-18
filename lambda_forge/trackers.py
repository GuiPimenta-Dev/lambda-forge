import inspect
import json
from functools import wraps


def invoke(service, resource_id, function, extra=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Get the signature of the function
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Map argument names to their values
            args_dict = bound_args.arguments

            # Extract values based on provided names
            invoked_value = args_dict.get(resource_id)
            function_value = args_dict.get(function)
            extra_values = {key: args_dict.get(key) for key in extra}

            cdk = json.load(open("cdk.json"))
            functions = json.load(open("functions.json"))

            project = cdk["context"]["name"]
            function_name = function_value._physical_name.split(f"{project}-")[1]
            for fc in functions:
                if fc["name"] == function_name:
                    fc["invocations"].append({"service": service, "resource_id": invoked_value, **extra_values})
                    break

            cdk["context"]["functions"] = functions

            with open("functions.json", "w") as file:
                json.dump(functions, file, indent=4)

            # Call the original function with its arguments
            return func(*args, **kwargs)

        return wrapper

    return decorator


def trigger(service, trigger, function, extra=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Map argument names to their values
            args_dict = bound_args.arguments

            # Extract values based on provided names
            trigger_value = args_dict.get(trigger)
            function_value = args_dict.get(function)
            extra_values = {key: args_dict.get(key) for key in extra}

            cdk = json.load(open("cdk.json"))
            functions = json.load(open("functions.json"))

            project = cdk["context"]["name"]
            function_name = function_value._physical_name.split(f"{project}-")[1]
            for fc in functions:
                if fc["name"] == function_name:
                    fc["triggers"].append({"service": service, "trigger": trigger_value, **extra_values})
                    break

            with open("functions.json", "w") as file:
                json.dump(functions, file, indent=4)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        functions = json.load(open("functions.json"))
        path = kwargs["path"]
        directory = kwargs.get("directory")
        path = f"{path}/{directory}" if directory else path
        timeout = int(kwargs.get("timeout", 1)) * 60
        name = kwargs["name"]
        functions.append(
            {
                "name": name,
                "path": path,
                "description": kwargs["description"],
                "timeout": timeout,
                "triggers": [],
                "invocations": [],
            }
        )

        with open("functions.json", "w") as file:
            json.dump(functions, file, indent=4)

        return func(*args, **kwargs)

    return wrapper


def reset(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with open("functions.json", "w") as file:
            json.dump([], file, indent=4)

        return func(*args, **kwargs)

    return wrapper
