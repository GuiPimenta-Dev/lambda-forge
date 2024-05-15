import json
import os
from functools import wraps

from dotenv import load_dotenv

load_dotenv()


def track(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cdk = json.load(open("cdk.json"))
        data = cdk["context"].get("functions", [])
        function_name = func.__name__

        if function_name == "create_function":
            path = kwargs["path"]
            directory = kwargs.get("directory")
            path = f"{path}/{directory}" if directory else path
            name = kwargs["name"]
            data.append(
                {
                    "name": name,
                    "path": path,
                    "description": kwargs["description"],
                }
            )

        elif function_name == "create_endpoint":
            name = args[3]._physical_name.split("-")[-1]
            for i in data:
                if i["name"] == name:
                    i.update({"method": args[1], "endpoint": args[2]})
                    break

        cdk["context"]["functions"] = data
        with open("cdk.json", "w") as file:
            json.dump(cdk, file, indent=4)

        return func(*args, **kwargs)

    return wrapper


def reset(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cdk = json.load(open("cdk.json"))
        cdk["context"]["functions"] = []
        with open("cdk.json", "w") as file:
            json.dump(cdk, file, indent=4)

        return func(*args, **kwargs)

    return wrapper