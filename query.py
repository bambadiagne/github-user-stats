import asyncio
import os
from python_graphql_client import GraphqlClient
import math

DEFAULT_USERNAME = "torvalds"
BASE_URL = "https://api.github.com/graphql"
MAX_GITHUB_FETCH = 1000

GRAPHQL_SERVEUR = GraphqlClient(
    endpoint=BASE_URL, headers={
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"})


# Thanks to https://github.com/daoodaba975/galsenify for
SENEGAL_REGIONS = [
    'Senegal', 'Sénégal',
    'Dakar', 'Diourbel',
    'Fatick', 'Kaffrine',
    'Kaolack', 'Kédougou',
    'Kolda', 'Louga',
    'Matam', 'Sédhiou',
    'Tambacounda', 'Thies',
    'Ziguinchor', 'SN'
]

LOCATIONS_FOR_SENEGAL = " ".join(
    f'location:{region}' for region in SENEGAL_REGIONS)


def query_builder_string(query: dict,):
    query = query.copy()
    grapqhql_query = "type:user "

    # if (query.get('bio')):
    #     grapqhql_query += f"{query['bio']} in:bio"
    if (query.get('user')):
        grapqhql_query += f"user:{query['user']}"
    if (query.get('location')):
        query['location'] = query.getlist('location')
        for location in query['location']:
            grapqhql_query += f" location:{location}"
    if (query.get("language")):
        for language in query.getlist("language"):
            grapqhql_query += f" language:{language}"
    return grapqhql_query


def query_list_user(location='Senegal', after=''):
    return """query ListUsers($query: String = "location: {}") {{
  search(type: USER, query: $query, first: 100, {}) {{
    userCount
    nodes {{
      ... on User {{
        name
        login
      	avatarUrl
        bio
      }}
    }}
    pageInfo {{
      endCursor
      hasNextPage
    }}
  }}
}}""".format(location, "after: \"{}\"".format(after) if (after) else '')


def query_all_senegalese(query, number, after=''):
    return """query GithubSenegaleseUser($query: String = "{0}") {{
  search(query: $query, type: USER, first:{1}, {2}) {{
    userCount
    nodes {{
      ... on User {{
        name
        login
        avatarUrl
        contributionsCollection {{
          totalCommitContributions
          contributionCalendar {{
            totalContributions
          }}
        }}
        createdAt
        location
      }}
    }}
     pageInfo {{
      endCursor
      hasNextPage
    }}
  }}
}}""".format(query, str(number), "after: \"{}\"".format(after) if (after) else '')


def query_get_one_user(login=DEFAULT_USERNAME):
    return """query GithubSingleUser {{
  user(login:"{}") {{
    bio
    name
    login
    websiteUrl
    twitterUsername
    contributionsCollection {{
          totalCommitContributions
          contributionCalendar {{
            totalContributions
          }}
        }}
    repositories(
      orderBy: {{field: STARGAZERS, direction: DESC}}
      first: 100
      isFork: false
      ownerAffiliations: OWNER

    ) {{
      edges {{
        node {{
          forkCount
          name
          stargazerCount
          languages(first: 10) {{
          edges {{
            node {{
              name
            }}
            size
          }}
        }}
        }}
      }}
    }}
    avatarUrl
    email
  }}
  }}""".format(login)


def fetchAllSenegalese(query):
    all_users = []
    try:
        data = handle_response(asyncio.run(
            GRAPHQL_SERVEUR.execute_async(
                query=query_all_senegalese(query, 50),
            )), "search")
    except RuntimeError as e:
        pass
    if (data.get('message')):
        return {'users': None, 'message': data.get('message')}
    userCount = data['userCount']
    all_users.extend(
        user for user in data['nodes'] if (
            user != {}))  # remove empty json
    while (data['pageInfo']['hasNextPage']):
        cursor = data['pageInfo']['endCursor']
        try:

            data = handle_response(asyncio.run(
                GRAPHQL_SERVEUR.execute_async(
                    query=query_all_senegalese(query, 50, cursor),
                )), "search")
            if (data.get('message')):
                return {'users': None, 'message': data.get('message')}
        except RuntimeError as e:
            pass
        all_users.extend(user for user in data['nodes'] if (user != {}))
    return {
        'users': all_users,
        'userCount': userCount,
        'message': "SUCCESSFUL"}


def user_fetcher(query=None, variables=None, single_fetch=False):

    if (single_fetch):
        data = asyncio.run(
            GRAPHQL_SERVEUR.execute_async(query=query,
                                          variables=variables
                                          ))
        return data
    fetched_result = fetchAllSenegalese(LOCATIONS_FOR_SENEGAL + " sort:joined")
    last_joined_user = fetched_result['users'][-1]
    all_users = list(fetched_result['users'])
    remaining_requests = math.ceil(
        fetched_result['userCount'] /
        MAX_GITHUB_FETCH)
    for i in range(remaining_requests):
        users = fetchAllSenegalese(
            LOCATIONS_FOR_SENEGAL +
            f" sort:joined created:<{last_joined_user['createdAt']}")
        all_users.extend(users['users'])
        if (users['users'] == []):
            break
        last_joined_user = users['users'][-1]

    return all_users


def count_user_in_json(json_array, login):
    count = 0
    for user in json_array:
        if (user == {}):
            continue
        if (user['login'] == login):
            count += 1
    return count


def format_user(user):
    languages_dict = {}
    for node in user['repositories']['edges']:
        for language in node['node']['languages']['edges']:
            language_type = language['node']['name']
            if (languages_dict.get(language_type)):
                languages_dict[language_type] += language['size']
            else:
                languages_dict[language_type] = language['size']
    user['most_used_anguages'] = list(map(lambda x: x[0], sorted(
        languages_dict.items(), key=lambda item: item[1], reverse=True)[:5]))
    user['most_starred_repo'] = user['repositories']['edges'][0]['node'] if (
        user['repositories']['edges']) else None
    del user['most_starred_repo']['languages']
    del user['repositories']
    return user


def handle_response(response: dict, data_type):
    if (response.get('message')):
        return {'message': response.get('message')}
    if (response.get('errors')):
        return {'message': response['errors'][-1]['message']}
    return response['data'][data_type]


def intersection(arr1, arr2):
    users = []
    if (len(arr1) > len(arr2)):
        for element in arr2:
            if (element in arr1):
                users.append(element)
        return users
    for element in arr1:
        if (element in arr2):
            users.append(element)
        return users
