from cmath import inf
import requests
from flask import Flask, request, jsonify, redirect, url_for
app = Flask(__name__)

@app.route('/work_distribution', methods=['GET', 'POST'])
def work_distribution():
    authToken = request.args.get('authToken')
    headers = {
            "Authorization": "Bearer " + authToken
        }

    slug = request.args.get('slug')
    sprint_name = request.args.get('sprint_name')
    
    response = requests.get(
    "https://api.taiga.io/api/v1/projects/by_slug?slug=" + slug, headers=headers)

    if response.status_code != 200:
        data = {}
        data['Error code'] = str(response.status_code) + 'Project not found. Terminating script!'
        json_data = jsonify(data)
        return json_data
    else:
        project = response.json()
        members = {}
        result_json = {"sprint_names": [], "roles": [], "summary": [], "number_of_sprints": 0}

        for member in project["members"]:
            members[member["full_name_display"]] = {}
            members[member["full_name_display"]]["Total"] = 0
            members[member["full_name_display"]]["In progress"] = 0
            members[member["full_name_display"]]["Ready for test"] = 0
            members[member["full_name_display"]]["user_stories"] = []
            result_json["roles"].append({
                "name": member["full_name_display"],
                "role": member["role_name"]
            })

        sprints = requests.get("https://api.taiga.io/api/v1/milestones?project=" + str(project["id"]), headers=headers).json()
        result_json["number_of_sprints"] = str(len(sprints))
        i = 0
        sprint_id = float('inf')
        for sprint in range(len(sprints)-1,-1,-1):
            result_json["sprint_names"].append({
                "name": sprints[sprint]["name"],
                "total_points": str(sprints[sprint]["total_points"]),
                "closed_points": str(sprints[sprint]["closed_points"])
            })
            i += 1
            if sprint_name == sprints[sprint]["name"]:
                sprint_id = sprints[sprint]["id"]
        
        if sprint_id == inf:
            data = {}
            data['Error'] = 'Sprint name is not found. Recheck sprint name'
            json_data = jsonify(data)
            return json_data
        
        elif sprint_id != inf:

            tasks = requests.get('https://api.taiga.io/api/v1/tasks?project=' + str(
                project["id"]) + '&milestone=' + str(sprint_id), headers=headers).json()

            for task in tasks:
                print(task)
                user_story = requests.get('https://api.taiga.io/api/v1/userstories/' + str(task["user_story"]), headers=headers).json()
                if task["assigned_to_extra_info"] is None:
                    name = "None"
                else:
                    name = task["assigned_to_extra_info"]["full_name_display"]
                    status = task["status_extra_info"]["name"]
                    members[name]['Total'] += 1
                    members[name]['user_stories'] += str(user_story["ref"])
                    if status == "In progress" or status == "Ready for test":
                        members[name][status] += 1

            for key in members:
                user_stories = str(members[key]['user_stories'])
                if members[key]['Total'] != 0:
                    result_json["summary"].append({"name": key, "total_assigned": str(members[key]['Total']), "user_stories": str(user_stories)[1:-1], "in_progress": str(members[key]['In progress']), "ready_for_test": str(members[key]['Ready for test'])})
                else:
                    result_json["summary"].append({"name": key, "total_assigned": 0})

            return jsonify(result_json)

if __name__ == '__main__':
    # run app in debug mode on port 8001
    app.run(debug=True, port=5001,host='0.0.0.0')