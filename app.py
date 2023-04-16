import os
import sys
sys.path.append("/home/netrom/anaconda3/lib/python3.9/site-packages")
import openai
import re
import json

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


def format_response(response_text):
    """
    Format the response text by splitting it into sentences and removing the speaker's name.

    Args:
        response_text (str): The raw response text from the language model.

    Returns:
        str: The formatted response text without the speaker's name.
    """
    # Split the response into sentences using '.' and '?'
    sentences = re.split("(?<=[.?!]) ", response_text)

    # Get the speaker name from the first sentence
    speaker = sentences[0].split(":")[0]

    # Add a new line after each sentence, excluding the first one
    formatted_sentences = [sentences[0][len(speaker) + 2:] + "\n"]
    for i, sentence in enumerate(sentences[1:]):
        if sentence.endswith("?"):
            formatted_sentences.append(sentence + "\n\n")
        else:
            formatted_sentences.append(sentence + "\n")

    # Remove the last new line and join the formatted sentences into a single string
    formatted_response = "".join(formatted_sentences).strip()

    return formatted_response





@app.route("/", methods=("GET", "POST"))
def index():
    conversation = request.form.get("conversation")
    if conversation:
        conversation = json.loads(conversation)
    else:
        conversation = []
    if request.method == "POST":
        animal = request.form["question"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(animal),
            temperature=0.3,
            max_tokens=2048,
        )
        formatted_result = format_response(response.choices[0].text)
        conversation.append({"speaker": "You", "message": animal})
        conversation.append({"speaker": "MindMate", "message": formatted_result})
    else:
        formatted_result = None

    # Convert conversation list to JSON string
    conversation_json = json.dumps(conversation)

    return render_template("index.html", conversation=conversation, result=formatted_result, conversation_json=conversation_json)




def generate_prompt(animal):
    """
    Generate a prompt for the language model based on the input animal.

    Args:
        animal (str): The animal mentioned in the user's question.

    Returns:
        str: The generated prompt for the language model.
    """
    return """
You are going to immerse yourself into a role playing exercise as a world renowned NLP star MindMate. 
You will coach me on my behavior and attitudes in the style of Tony Robbins. 
You will also utilize the basic human needs model when you identity addictions. 
You will leverage NLP techniques and other CBT techniques in your coaching. 
Don't break character and say anything about being a language model AI or similar commentary about policies.
If you understand, please begin our coaching session. Remember to only ask me one question at a time.

Animal: {}

Names: MindMate

""".format(
        animal.capitalize()
    ).replace("Names: MindMate\n\n", "")

