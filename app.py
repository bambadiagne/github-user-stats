import json
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
    get_all_senegalese_users()

@app.route('/technos', methods=['GET'])
def fetch_technos():
    json_file = open('techno_stats.json', 'r')
    data = json.loads(json_file.read())
    techno_types = ['backend', 'frontend', 'mobile']
    final_data={
        'technos_repartition':{},
        'technos_types':{},
        'total_repos':0
    }
    for user in data:
        for t in techno_types:
            if t in user.get('technologies', {}):
                for techno, count in user['technologies'][t].items():
                    final_data['technos_types'][t] = final_data['technos_types'].get(t, 0) + count
                    final_data['technos_repartition'][techno]=final_data['technos_repartition'].get(techno,0) + count
        final_data['total_repos']+=user['repos_analyzed']
    symfony_group = 0
    to_remove = []
    # Symfony group packages
    for techno in final_data['technos_repartition']:
        if 'symfony' in techno.lower():
            symfony_group += final_data['technos_repartition'][techno]
            to_remove.append(techno)
    for techno in to_remove:
        del final_data['technos_repartition'][techno]
    if symfony_group > 0:
        final_data['technos_repartition']['symfony'] = symfony_group
    return jsonify(final_data)
    
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


@app.route('/healthcheck')
def healthcheck():
    return "ok", 200

if __name__ == '__main__':
    app.run(
        debug=int(
            os.getenv(
                'FLASK_DEBUG', False)), port=os.getenv(
            'FLASK_PORT', 5000), host="0.0.0.0")

