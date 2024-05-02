# from InquirerPy import prompt, get_style


# options = ["Multi-Stage", "Multi-Stage / No Docs", "Minimal"]
# style = get_style(
#     {
#         "questionmark": "#00FFFF",
#         "input": "#00FFFF",
#         "pointer": "#00FFFF",
#         "question": "#00FFFF",
#         "answered_question": "#00FFFF",
#         "pointer": "#00FFFF",
#         "answer": "white",
#         "answermark": "#00FFFF",
#     },
#     style_override=True,
# )

# def get_user_input():
#     questions = [
#         {
#             'type': 'input',
#             'name': 'color',
#             'message': 'What\'s your favorite hex color?',
#             'style': {
#         "questionmark": "#00FFFF",
#         "input": "#00FFFF",
#         "pointer": "#00FFFF",
#         "question": "#00FFFF",
#         "answered_question": "#00FFFF",
#         "pointer": "#00FFFF",
#         "answer": "white",
#         "answermark": "#00FFFF",
#     }
#         }
#     ]

#     answers = prompt(questions)
#     print(f"Your favorite color in uppercase hex is: {answers['color']}")

# if __name__ == "__main__":
#     get_user_input()

import click

click.echo()
style = click.style('Repository Name', fg=(0, 255, 255))
repo_name = click.prompt(style, type=str)
