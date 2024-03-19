import json
from functools import wraps
import os


def track(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        file_path = os.path.join("lambda_forge", "functions.json")
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except:
            data = []

        function_name = func.__name__

        if function_name == "create_function":
            path = kwargs["path"]
            directory = kwargs.get("directory")
            full_path = (
                f"{path}/{directory}/main.lambda_handler"
                if directory
                else f"{path}/main.lambda_handler"
            )
            name = kwargs["name"]
            existent_function = next((i for i in data if i["name"] == name), None)
            if not existent_function:
                data.append(
                    {
                        "name": name,
                        "file_path": full_path,
                        "description": kwargs["description"],
                    }
                )

        elif function_name == "create_endpoint":
            name = args[3]._physical_name.split("-")[-1]
            for i in data:
                if i["name"] == name:
                    i.update({"method": args[1], "endpoint": args[2]})
                    break

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        return func(*args, **kwargs)

    return wrapper


def release(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        file_path = os.path.join("lambda_forge", "functions.json")
        if os.path.exists(file_path):
            os.remove(file_path)

        return func(*args, **kwargs)

    return wrapper
