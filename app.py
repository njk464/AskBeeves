from flask import Flask, render_template, json, request
import json
import sys
from StringIO import StringIO

import requests
from requests.auth import HTTPBasicAuth
app = Flask(__name__)
@app.route("/")
def main():
    return render_template('index.html')
@app.route("/answer", methods=['GET', 'POST'])
def answer():
    answer = ask_question("uta_student3", "nkcGD7qy",request.form['search'])
    return render_template('answer.html', answer=json.dumps(json.loads(answer.content), indent=4), question=request.form['search'])

# method for asking a question to the watson API
# ask_question("uta_student30", "V5iYOgVT", question)
def ask_question(username, password, question):
    authentication = HTTPBasicAuth(username, password)
    headers = {'X-SyncTimeout': '30', 'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {'question': {'questionText': question}}
    # changed the link to the second instance
    response = requests.post('https://dal09-gateway.watsonplatform.net/instance/569/deepqa/v1/question',
                             data=json.dumps(data),
                             auth=authentication,
                             headers=headers)

    return response
if __name__ == "__main__":
    app.run()
