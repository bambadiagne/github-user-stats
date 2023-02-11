import json
import os
from flask import Flask, jsonify, request
from python_graphql_client import GraphqlClient
import asyncio
from query import *
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

BASE_URL = "https://api.github.com/graphql"

GRAPHQL_SERVEUR = GraphqlClient(
    endpoint=BASE_URL, headers={
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"})


@scheduler.task('cron', id='do_fetch_senegal_users',
                hour='*', misfire_grace_time=900)
def fetch_senegal_users():
    pass


@app.route('/users/contributions/senegal', methods=['GET'])
def get_dakar_users():
    all_users = {'users': []}

    data = asyncio.run(
        GRAPHQL_SERVEUR.execute_async(
            query=query_all_senegalese(10),
        ))['data']['search']

    all_users['users'].extend(data['nodes'])

    while (data['pageInfo']['hasNextPage']):
        cursor = data['pageInfo']['endCursor']
        data = asyncio.run(
            GRAPHQL_SERVEUR.execute_async(
                query=query_all_senegalese(
                    50,
                    cursor),
            ))['data']['search']
        all_users['users'].extend(data['nodes'])
    with open("users.json", "w", encoding="utf-8",) as f:
        json.dump(all_users,
                  f,
                  indent=4,
                  sort_keys=True)
    return jsonify({"message": "Every nice"})


@app.route('/users/search', methods=['GET'])
def list_users_by_location():
    query_args = request.args
    variables = {'query': query_builder_string(query_args)}
    data = asyncio.run(
        GRAPHQL_SERVEUR.execute_async(
            query=query_list_user(
                query_builder_string(query_args),
                query_args.get('after')),
            variables=variables))['data']
    return jsonify(data)


@app.route('/users/<username>', methods=['GET'])
def get_user_by_user(username):

    data = asyncio.run(
        GRAPHQL_SERVEUR.execute_async(
            query=query_get_one_user(username)))
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
