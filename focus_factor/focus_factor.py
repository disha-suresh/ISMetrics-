import requests
from flask import Flask, request, jsonify, redirect, url_for
app = Flask(__name__)

@app.route('/focus_factor')
def focus_factor():
    authToken = request.args.get('authToken')
    headers = {
            "Authorization": "Bearer " + authToken
        }

    slug = request.args.get('slug')
    
    response = requests.get(
    "https://api.taiga.io/api/v1/projects/by_slug?slug=" + slug, headers=headers)

    if response.status_code != 200:
        data = {}
        data['Error code'] = str(response.status_code) + 'Project not found. Terminating script!'
        json_data = jsonify(data)
        return json_data
    else:
        project = response.json()
        result_json = {"number_of_sprints": 0, "sprints": []}

        sprints = requests.get("https://api.taiga.io/api/v1/milestones?project=" + str(project["id"]), headers=headers).json()
        result_json["number_of_sprints"] = str(len(sprints))
        
        work_capacity = 0
        focus_factor = 0
        
        for sprint in range(len(sprints)-1,-1,-1):
            user_stories = sprints[sprint]["user_stories"]
            user_story_points = 0
        
            if user_stories != []:
                for user_story in user_stories:
                    user_story_id = user_story["id"]
        
                    user_story = requests.get("https://api.taiga.io/api/v1/userstories/" + str(user_story_id), headers=headers).json()
                    tasks = requests.get("https://api.taiga.io/api/v1/tasks?project=" + str(project["id"]) + "&milestone=" + str(user_story["milestone"]), headers=headers).json()            
        
                    indices = [x["user_story"] for i, x in enumerate(tasks) if x["user_story"] == user_story["id"]]
                    indices_2 = [x["user_story"] for i, x in enumerate(tasks) if x["user_story"] == user_story["id"] and x["status_extra_info"]["is_closed"] == True]
        
                    if indices == indices_2:
                        user_story_points += user_story["total_points"]
                    elif indices_2 != []:
                        user_story_points += (user_story["total_points"]/len(indices) * len(indices_2))
        
                    work_capacity = user_story_points
        
                focus_factor = (int(sprints[sprint]["total_points"])/work_capacity * 100)
            
            result_json["sprints"].append({
                "name": sprints[sprint]["name"],
                "velocity": sprints[sprint]["total_points"],
                "work_capacity": work_capacity,
                "focus_factor (%)": round(focus_factor, 2)
            })
            work_capacity = 0
            focus_factor = 0
        return jsonify(result_json)
    

if __name__ == '__main__':
    # run app in debug mode on port 8001
    app.run(debug=True, port=5002,host='0.0.0.0')