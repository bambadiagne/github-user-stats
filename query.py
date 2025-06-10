import asyncio
from python_graphql_client import GraphqlClient
import math
import datetime
import json
import os
import threading
import time
import logging
import re
from collections import defaultdict
import sys
import copy
import concurrent.futures
_logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.INFO)

# --- GraphQL key rotation system ---
GITHUB_TOKENS = os.getenv("TOKENS")  # Comma-separated list of tokens
if GITHUB_TOKENS:
    TOKENS = [t.strip() for t in GITHUB_TOKENS.split(",") if t.strip()]
if not TOKENS:
    raise RuntimeError("No GitHub tokens provided in GITHUB_TOKEN or GITHUB_TOKENS env vars.")
DEFAULT_USERNAME = "torvalds"
BASE_URL = "https://api.github.com/graphql"
MAX_GITHUB_FETCH = 1000
MAX_FETCH= 1000
TARGET_FILES = [
    "package.json",
    "requirements.txt",
    "composer.json",
    "pubspec.yaml",
    "pom.xml",
    "build.gradle",
    "Podfile",
    "project.pbxproj",
    "AndroidManifest.xml",
    "build.gradle.kts",  # Kotlin DSL for Android

]
TECHNO_SIGNATURES = {
    "package.json": {
        "frontend": ["react", "vue", "next", "angular", "vite"],
        "backend": ["express", "nestjs", "koa", "hapi"],
        "mobile": ["react-native", "ionic", "cordova", "expo"]
    },
    "requirements.txt": {
        "backend": ["django", "flask", "fastapi"]
    },
    "composer.json": {
        "backend": ["laravel/framework", "symfony", "symfony/symfony", "symfony/http-foundation", "symfony/console"]
    },
    "pubspec.yaml": {
        "mobile": ["flutter"]
    },
    "pom.xml": {
        "backend": ["spring-boot-starter", "springframework"]
    },
    "build.gradle": {
        "backend": ["spring-boot-starter", "springframework"],
        "mobile": ["com.android.application", "androidx", "kotlin-android"]
    },
    "build.gradle.kts": {  # Kotlin DSL
        "mobile": ["com.android.application", "androidx", "kotlin-android"]
    },
    "AndroidManifest.xml": {
        "mobile": ["manifest", "application"]  # indicator of Android project
    },
    "Podfile": {
        "mobile": ["platform :ios", "use_frameworks!"]  # typical iOS CocoaPods
    },
    "project.pbxproj": {
        "mobile": ["Xcode", "iOS", "macosx"]  # part of iOS/macOS projects
    }
}
IGNORE_PATTERNS = [
    r'(^|/|\\)node_modules(/|\\|$)',      # Node.js dependencies
    r'(^|/|\\)venv(/|\\|$)',              # Python virtual environment
    r'(^|/|\\)\.venv(/|\\|$)',            # Python .venv
    r'(^|/|\\)env(/|\\|$)',               # Python env
    r'(^|/|\\)\.env(/|\\|$)',             # Python .env
    r'(^|/|\\)dist(/|\\|$)',              # Distribution folders
    r'(^|/|\\)build(/|\\|$)',             # Build folders
    r'(^|/|\\)\.git(/|\\|$)',             # Git folder
    r'(^|/|\\)\.idea(/|\\|$)',            # JetBrains IDE config
    r'(^|/|\\)\.vscode(/|\\|$)',          # VSCode config
    r'(^|/|\\)__pycache__(/|\\|$)',       # Python cache
    r'(^|/|\\)migrations(/|\\|$)',        # Django migrations
    r'(^|/|\\)src(/|\\|$)',                # Source code folders
]
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


def get_all_senegalese_users():
    start_time = time.time()

    all_users = {'users': []}

    all_users['users'] = user_fetcher()
    with open("users.json", "w", encoding="utf-8",) as f:
        json.dump(all_users,
                  f,
                  indent=4,
                  sort_keys=True)
    logging.info(f"JOB TAKEN TIME {time.time()-start_time} seconds")


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
          restrictedContributionsCount
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
    location
    twitterUsername
    contributionsCollection {{
          totalCommitContributions
          restrictedContributionsCount
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
    query = "type:user " + query
    try:
        data = handle_response(asyncio.run(
            get_graphql_client().execute_async(
                query=query_all_senegalese(query, 50),
            )), "search")
    except RuntimeError as e:
        pass
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        # return {'users': None, 'message': str(e)}
        pass
    if (data.get('message')):
        return {'users': None, 'message': data.get('message')}
    userCount = data['userCount']
    all_users.extend(data['nodes'])  # remove empty json
    while (data['pageInfo']['hasNextPage']):
        cursor = data['pageInfo']['endCursor']
        try:
            data = handle_response(asyncio.run(
                get_graphql_client().execute_async(
                    query=query_all_senegalese(query, 50, cursor),
                )), "search")
            if (data.get('message')):
                return {'users': None, 'message': data.get('message')}
        except RuntimeError as e:
            pass
        all_users.extend(data['nodes'])
    return {
        'users': all_users,
        'userCount': userCount,
        'message': "SUCCESSFUL"}


def user_fetcher(query=None, variables=None, single_fetch=False):

    if (single_fetch):
        data = asyncio.run(
            get_graphql_client().execute_async(query=query,
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
        # if not users or not users.get('users'):
        #     break
        all_users.extend(users['users'])
        if (users['users'] == []):
            break
        last_joined_user = users['users'][-1]

    return all_users

def get_graphql_client():
    with _token_lock:
        token = TOKENS[_token_index]
        headers = {"Authorization": f"Bearer {token}"}
    return GraphqlClient(
        endpoint=BASE_URL, headers=headers)

def should_ignore(path):
    return any(re.search(pattern, path) for pattern in IGNORE_PATTERNS)
def check_rate_limit():
    query = '''
    {
      rateLimit {
        limit
        cost
        remaining
        resetAt
      }
    }
    '''
    with _token_lock:
        token = TOKENS[_token_index]
        headers = {"Authorization": f"Bearer {token}"}
    try:
        result = get_graphql_client().execute(query=query, headers=headers)    
        rate = result["data"]["rateLimit"]
        return rate
    except Exception as e:
        _logger.warning(f"Could not check rate limit: {e}")
        return None
# Load previously collected users
def load_users(file="users.json"):
    with open(file, "r") as f:
        return json.load(f)['users']

def save_checkpoint(results, last_user, filename="user_technos.json"):
    with open(filename, "w") as f:
        json.dump({"results": results, "last_user": last_user}, f, indent=2)

def load_checkpoint(filename="user_technos.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
            return data.get("results", []), data.get("last_user")
    return [], None

_token_index = 0
_token_lock = threading.Lock()

def get_next_token():
    global _token_index
    with _token_lock:
        token = TOKENS[_token_index]
        _token_index = (_token_index + 1) % len(TOKENS)
    return token

def graphql_query(query):
    global _token_index
    last_error = None
    for _ in range(len(TOKENS)):
        try:
            rate = check_rate_limit()
            graphql_client=get_graphql_client()
            if rate and rate['remaining'] < 200:
                 _logger.warning(f"Approaching rate limit, sleeping for 60 seconds remaining {rate['remaining']}...")
                 with _token_lock:
                    _token_index = (_token_index + 1) % len(TOKENS)    
                 time.sleep(60)  
            result = asyncio.run(graphql_client.execute_async(query=query))
           
            if "errors" in result:
                for error in result["errors"]:
                    if error.get("type") == "RATE_LIMITED":
                        _logger.warning(f"API rate limit exceeded for token  {_token_index}. Rotating token.")
                        _logger.info(f'Error: {str(result["errors"])}')
                        # with _token_lock:
                        #     _token_index = (_token_index + 1) % len(TOKENS)
                        # break
                else:
                    return result
            else:
                return result
        except Exception as e:
            last_error = e
            _logger.warning(f"GraphQL query failed with token {_token_index}. Rotating token.")
            time.sleep(2)  # Wait before retrying with the next token
            # with _token_lock:
            #     _token_index = (_token_index + 1) % len(TOKENS)
    _logger.error("All tokens exhausted or failed. Exiting program.")
    sys.exit(1)
    if last_error:
        raise last_error
    pass
def graphql_query_with_retry(query, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return graphql_query(query)
        except Exception as e:
            _logger.warning(f"GraphQL query failed (attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
def get_user_repos(username):
    # affiliations:OWNER,
    query = f'''
    query {{
      user(login: "{username}") {{
        repositories(ownerAffiliations:OWNER,first: 100, privacy: PUBLIC, isFork: false, orderBy: {{field: STARGAZERS, direction: DESC}}) {{
          nodes {{
            name
          }}
        }}
      }}
    }}
    '''
    result = graphql_query_with_retry(query)
    # _logger.info('My result: %s %s', result,len(result))
    try:
        return result["data"]["user"]["repositories"]["nodes"]
    except (TypeError, KeyError):
        _logger.error(f"Could not fetch repositories for user '{username}'. Response: {result}")
        return []

def list_repo_files(owner, repo_name):
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        object(expression: "HEAD:") {{
          ... on Tree {{
            entries {{
              name
              type
              object {{
                ... on Tree {{
                  entries {{
                    name
                    type
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    try:
        result = graphql_query_with_retry(query)
    except Exception as e:
        _logger.info(f"Erreur lors de la récupération des fichiers du dépôt {repo_name}: {str(e)} {query}")
        print('error GET FILES REPO', str(e))
        return []
    paths = []

    def walk_entries(entries, prefix="", depth=1):
        if depth > 2 or not entries:
            return
        for entry in entries:
            path = f"{prefix}{entry['name']}"
            if should_ignore(path) or should_ignore(prefix):
                # _logger.info(f"Ignoring path: {path}")
                continue
            if entry["type"] == "blob" and any(path.endswith(f) for f in TARGET_FILES):
                paths.append(path)
            elif entry["type"] == "tree":
                obj = entry.get("object")
                if obj:
                    walk_entries(obj.get("entries", []), prefix=path + "/", depth=depth + 1)

    tree = None
    if (
        result.get("data")
        and result["data"].get("repository")
        and result["data"]["repository"].get("object")
    ):
        tree = result["data"]["repository"]["object"]
    if tree:
        walk_entries(tree.get("entries", []), "")

    return paths

def get_file_content(owner, repo_name, filepath):
    expression = f"HEAD:{filepath}"
    query = f'''
    query {{
      repository(owner: "{owner}", name: "{repo_name}") {{
        object(expression: "{expression}") {{
          ... on Blob {{
            text
          }}
        }}
      }}
    }}
    '''
    try:
        result = graphql_query_with_retry(query)
        return result["data"]["repository"]["object"]["text"] if result["data"]["repository"]["object"] else None
    except Exception as e:
        _logger.warning(f"Erreur fichier {filepath} dans {repo_name}: {e}")
        print('error GET FILE CONTENT', e)
        return None


def detect_technologies(file_name, content,repo=None):
    detected = []
    try:
        match file_name:
            case "package.json":
                deps = json.loads(content).get("dependencies", {})
                deps.update(json.loads(content).get("devDependencies", {}))
                for cat, keys in TECHNO_SIGNATURES[file_name].items():
                    for key in keys:
                        if any(key.lower() in dep.lower() for dep in deps):
                            detected.append((cat, key))
                        

            case "requirements.txt":
                lines = content.lower().split("\n")
                for cat, libs in TECHNO_SIGNATURES[file_name].items():
                    for lib in libs:
                        if any(lib in line for line in lines):
                            detected.append((cat, lib))

            case "composer.json":
                deps = json.loads(content).get("require", {})
                for cat, keys in TECHNO_SIGNATURES[file_name].items():
                    for key in keys:
                        if key in deps:
                            detected.append((cat, key))
                            break
            case "pubspec.yaml":
                if "flutter" in content.lower():
                    detected.append(("mobile", "flutter"))

            case "pom.xml" | "build.gradle" | "build.gradle.kts":
                content_lower = content.lower()
                for cat, libs in TECHNO_SIGNATURES[file_name].items():
                    for lib in libs:
                        if lib.lower() in content_lower:
                            detected.append((cat, lib))

            case "AndroidManifest.xml":
                content_lower = content.lower()
                for key in TECHNO_SIGNATURES[file_name]["mobile"]:
                    if key in content_lower:
                        detected.append(("mobile", "android"))
                        break

            case "Podfile":
                content_lower = content.lower()
                for key in TECHNO_SIGNATURES[file_name]["mobile"]:
                    if key in content_lower:
                        detected.append(("mobile", "ios"))
                        break

            case "project.pbxproj":
                content_lower = content.lower()
                for key in TECHNO_SIGNATURES[file_name]["mobile"]:
                    if key in content_lower:
                        detected.append(("mobile", "ios"))
                        break

    except Exception as e:
        _logger.warning(f"Erreur détection techno pour {file_name}: {e}")
    return detected

def analyze_user(username):
    repos = get_user_repos(username)
    technos = {
        'backend':{},
         'frontend':{},
         'mobile':{}
    }
    for repo in repos:
        repo_name = repo["name"]
        filepaths = list_repo_files(username, repo_name)
        for path in filepaths:
            content = get_file_content(username, repo_name, path)
            if content:
                base_name = os.path.basename(path)
                categories = detect_technologies(base_name, content,repo)
                for cat in categories:
                    techno_type, techno_name = cat
                    technos[techno_type][techno_name] = technos[techno_type].get(techno_name, 0) + 1
    return {
        "username": username,
        "technologies": technos,
        "repos_analyzed": len(repos)
    }

def process_user_technos(user):
    _logger.info(f"Analyzing {user['login']}...")
    try:
        result = analyze_user(user["login"])
        return result
    except SystemExit:
        _logger.error("Stopped due to rate limit. Saving progress and exiting.")
        return None
            
    except Exception as e:
        _logger.error(f"Error analyzing {user['login']}: {e}")
        return None
def get_all_senegalese_technos():
    checkpoint_file = "checkpoint.json"
    last_user = None
    results = []
    USERS=load_users()
    users = copy.deepcopy(USERS)
    
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            checkpoint_data = json.load(f)
            last_user = checkpoint_data.get("last_user")
            results = checkpoint_data.get("results", [])
            if last_user:
                try:
                    last_user_index = next(i for i, user in enumerate(users) if user["login"] == last_user)
                    users = users[last_user_index + 1:last_user_index + MAX_FETCH + 2] 
                except StopIteration:
                    users = users[:MAX_FETCH + 1]
    else:
        _logger.info("No checkpoint found, starting fresh.")
        users = users[:MAX_FETCH + 1]
    start_time = time.time()
    _logger.info(f"Début de l'analyse des utilisateurs à {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=17) as executor:
        future_to_user = {executor.submit(process_user_technos, user): user for user in users}
        for future in concurrent.futures.as_completed(future_to_user):
            res = future.result()
            if res is not None and (not isinstance(res, dict) or not res.get("errors")):
                results.append(res)
            time.sleep(2)  # pour éviter les rate limits
    _logger.info(f"Analyse terminée pour {len(results)} utilisateurs sur {len(USERS)}")
    if len(USERS) == len(results): 
        with open("techno_stats.json", "w") as f:
            _logger.info(f"Saving results to techno_stats.json {results}")
            json.dump(results, f, indent=2)
        os.remove(checkpoint_file)
    else:
        with open(checkpoint_file, "w") as f:
            checkpoint_data = {
                "last_user": users[-1]["login"] if users else last_user,
                "results": results
            }
            json.dump(checkpoint_data, f, indent=2)
    end_time = time.time()
    _logger.info(f"Analyse terminée en {end_time - start_time:.2f} secondes")

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
    user['most_used_languages'] = list(map(lambda x: x[0], sorted(
        languages_dict.items(), key=lambda item: item[1], reverse=True)[:5]))
    user['most_starred_repo'] = user['repositories']['edges'][0]['node'] if (
        user['repositories']['edges']) else None
    if (len(user['repositories']['edges']) > 0):
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
