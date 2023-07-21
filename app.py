import json
import time
from flask import Flask, jsonify, request, send_file
from query import *
from flask_apscheduler import APScheduler
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@scheduler.task('interval', id='do_fetch_senegal_users',
                seconds=3600, misfire_grace_time=900)
def get_senegal_users():
    start_time = time.time()
    print('============================= START JOB =============================')
    all_users = {'users': []}

    all_users['users'] = user_fetcher()
    with open("users.json", "w", encoding="utf-8",) as f:
        json.dump(all_users,
                  f,
                  indent=4,
                  sort_keys=True)
    print('============================= END JOB =============================')
    print(f"JOB TAKEN TIME {time.time()-start_time} seconds")
    return jsonify({"ok": "ok"})


@app.route('/users/contributions/senegal', methods=['GET'])
def fetch_senegal_users():
    json_file = open('users.json', 'r')
    data = json.loads(json_file.read())
    return jsonify(data)


@app.route('/users/search', methods=['GET'])
def list_users_by_location():
    query_args = request.args
    variables = {'query': query_builder_string(query_args)}
    users = []
    data = handle_response(
        user_fetcher(
            query_list_user(
                query_builder_string(query_args),
                query_args.get('after')),
            variables=variables,
            single_fetch=True),
        "search")
    if (data.get('message')):
        return jsonify(data)
    cursor = data['pageInfo']['endCursor']
    users.extend(data['nodes'])
    while (data["pageInfo"]['hasNextPage']):
        data = handle_response(user_fetcher(query_list_user(
            query_builder_string(query_args),
            cursor), variables=variables, single_fetch=True), "search")
        if (data.get('message')):
            return jsonify(data)
        cursor = data["pageInfo"]['endCursor']
        users.extend(data['nodes'])
    return jsonify(users)


@app.route('/get-user-file', methods=['GET'])
def get_user_file():   
    return send_file('users.json')

@app.route('/users/<username>', methods=['GET'])
def get_user_by_user(username):

    data = handle_response(
        user_fetcher(
            query_get_one_user(username),
            single_fetch=True),
        "user")
    if (data.get("message")):
        return jsonify(data)
    return jsonify(format_user(data))


@app.errorhandler(404)
def page_not_found(e):
    return {"message": "Ressource introuvable"}

if __name__ == '__main__':
    app.run(debug=int(os.getenv('FLASK_DEBUG', False)), port=80, host="0.0.0.0")

@app.route('/healthcheck')
def healthcheck():
    return "ok", 200 