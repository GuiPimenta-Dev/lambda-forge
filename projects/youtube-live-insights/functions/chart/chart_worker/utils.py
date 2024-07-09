import json
import os
import sm_utils
from openai import OpenAI


def analyse_with_openai(author_summary, messages):
    OPENAPI_KEY_SECRET_NAME = os.environ.get("OPENAPI_KEY_SECRET_NAME", "OPEN_API_KEY")
    api_key = sm_utils.get_secret(OPENAPI_KEY_SECRET_NAME)
    client = OpenAI(api_key=api_key)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    prompt = open(f"{current_dir}/prompt.txt").read()

    items = {"author_summary": author_summary, "chat": messages}

    full_prompt = f"""{prompt}
    
    {json.dumps(items)}
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=1,
            max_tokens=4096,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        response = json.loads(completion.choices[0].message.content)

    except Exception as e:
        print(e)
        response = {
            "rating": "0",
            "reason": "N/A",
            "chat_summary": "N/A",
        }

    return response
