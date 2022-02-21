import requests

from cmath import inf
from flask import Flask, request, jsonify, redirect, url_for
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Go to /login to invoke both the metrics in seperate docker containers'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # if key doesn't exist, returns None
        refreshToken = ""
        authToken = ""
        username = request.form.get('username')
        password = request.form.get('password')
        metric_type = request.form.get('metric_name')
        print(username)
        print(password)
        print(metric_type)
        login = {
            "password": password,
            "type": "normal",
            "username": username
        }
        loginResponse = requests.post('https://api.taiga.io/api/v1/auth', data=login)
        print(loginResponse)
        if loginResponse.status_code != 200:
            print('Error code ' + str(loginResponse.status_code) +
                ' - Login failed. Terminating script!')
            return '''
            <div><label>Error code {} - Login failed. Terminating script!</label></div>'''.format(str(loginResponse.status_code))
        else:
            auth = loginResponse.json()
            refreshToken = auth['refresh']
            authToken = auth['auth_token']
            return redirect(url_for('invoke', authToken=authToken, metric_type=metric_type))
    return '''
        <form method="POST">
            <div><label>Username: <input type="text" name="username"></label></div>
            <div><label>Password: <input type="password" name="password"></label></div>
            </br>
            <div>Choose a metric:</div>
            <input type="checkbox" name="metric_name" value="focus_factor" unchecked>Focus Factor <br>
            <input type="checkbox" name="metric_name" value="work_distribution" unchecked>Work Distribution<br>
            <input type="submit" value="Submit">
        </form>'''

@app.route('/invoke', methods=['GET', 'POST'])
def invoke():
    metric_type = request.args.get('metric_type')

    if request.method == 'POST':
        authToken = request.args.get('authToken')
        headers = {
                "Authorization": "Bearer " + authToken
            }
        
        if metric_type == "focus_factor":
            slug = request.form.get('slug')
            params = {'authToken': authToken, 'slug': slug}
            response = requests.get(
        "http://localhost:5002/focus_factor", params=params)
        elif metric_type == "work_distribution":
            slug = request.form.get('slug')
            sprint_name = request.form.get('sprint_name')
            params = {'authToken': authToken, 'slug': slug, 'sprint_name': sprint_name}
            response = requests.post(
        "http://localhost:5001/work_distribution", params=params)
        
        return response.json()
        
    # otherwise handle the GET request
    if metric_type == "focus_factor":
        return '''
        <form method="POST">
            <div><label>Slug: <input type="text" name="slug"></label></div>
            <input type="submit" value="Submit">
        </form>'''
    elif metric_type == "work_distribution":
        return '''
        <form method="POST">
            <div><label>Slug: <input type="text" name="slug"></label></div>
            <div><label>Sprint name: <input type="text" name="sprint_name"></label></div>
            <input type="submit" value="Submit">
        </form>'''
    

if __name__ == '__main__':
    # run app in debug mode on port 8001
    app.run(debug=True, port=8001,host='0.0.0.0')