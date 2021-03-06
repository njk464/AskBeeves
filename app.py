from flask import Flask, render_template, json, request
from requests.auth import HTTPBasicAuth
from flask.ext.mysql import MySQL
from sets import Set
import json
import sys
import requests

app = Flask(__name__)
# uncomment for debugging
app.debug = True
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'sql398426'
app.config['MYSQL_DATABASE_PASSWORD'] = 'lM9!dV5!'
app.config['MYSQL_DATABASE_DB'] = 'sql398426'
app.config['MYSQL_DATABASE_HOST'] = 'sql3.freemysqlhosting.net'
mysql.init_app(app)

@app.route("/")
def main():
    rec = most_recent(10)
    freq = most_frequent(10)
    comb = Set(rec) | Set(freq)
    return render_template('index.html',comb=comb, freq=freq, rec=rec)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route("/answer", methods=['GET', 'POST'])
def answer():
    question = request.form['search']
    answer = ask_question("uta_student3", "nkcGD7qy", question)
    result = update(question)

    parsed_json = json.loads(answer.content)['question']['evidencelist']

    count = 0
    # Don't parse this way folks.
    for x in parsed_json:
        if 'text' not in x and 'title' not in x:
            del parsed_json[count]

        if 'id' in x:
            del parsed_json[count]['id']
        if 'document' in x:
            del parsed_json[count]['document']
        if 'copyright' in x:
            del parsed_json[count]['copyright']
        if 'termsOfUse' in x:
            del parsed_json[count]['termsOfUse']
        if 'metadataMap' in x:
            del parsed_json[count]['metadataMap']
        if 'value' in x:
            del x['value']
        if count > 3:
            del parsed_json[count]

        count += 1

    try:
        return render_template('answer.html', answer=parsed_json, question=question)
    except Exception as e:
        return render_template("500.html", error = str(e))


    # return render_template('answer.html', answer=parsed_json, question=question)

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

# totally open to a SQL injection, but it can't do that much harm and I could not fix the error that kept coming up while trying to prevent it.
def update(question):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * from QUESTIONS where question='" + question + "';")
    data = cursor.fetchone()
    if data is None:
        #  working
        cursor.execute("INSERT INTO QUESTIONS (question, frequency) values ('" + question + "', 1);")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    else:
        # working, on update the date is set to NOW() so we don't have to manually update that
        cursor.execute("UPDATE QUESTIONS SET frequency = " + str(int(data[2])+1) + " WHERE question='" + question + "';")
        conn.commit()
        cursor.close()
        conn.close()
        return False

def most_frequent(amount):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT question from QUESTIONS ORDER BY frequency DESC LIMIT " + str(amount) + ";")
    data = []
    for (question) in cursor:
        data.append(question)
    cursor.close()
    conn.close()
    return data

def most_recent(amount):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT question from QUESTIONS ORDER BY last_asked DESC LIMIT " + str(amount) + ";")
    data = []
    for (question) in cursor:
        data.append(question)
    cursor.close()
    conn.close()
    return data

if __name__ == "__main__":
    app.run()
