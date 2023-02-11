DEFAULT_USERNAME = "torvalds"

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
    grapqhql_query = ""
    if (query.get('username')):
        grapqhql_query += f" user:{query['username']}"
    if (query.get('user')):
        grapqhql_query += f"user:{query['user']}"
    if (query.get('location')):
        query['location'] = query.getlist('location')
        for location in query['location']:
            grapqhql_query += f" location:{location}"
    if (query.get("language")):
        for language in query.getlist("language"):
            grapqhql_query += f" language:{language}"
    if (query.get('bio')):
        grapqhql_query += f" {query['bio']} in:bio"

    print(grapqhql_query)
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


def query_all_senegalese(number, after=''):
    return """query GithubSenegaleseUser($query: String = "{0}") {{
  search(query: $query, type: USER, first:{1}, {2}) {{
    userCount
    nodes {{
      ... on User {{
        name
        login
        contributionsCollection {{
          totalCommitContributions
          contributionCalendar {{
            totalContributions
          }}
        }}
        location
      }}
    }}
     pageInfo {{
      endCursor
      hasNextPage
    }}
  }}
}}""".format(LOCATIONS_FOR_SENEGAL, str(number), "after: \"{}\"".format(after) if (after) else '')


def query_get_one_user(login=DEFAULT_USERNAME):
    return """query GithubSingleUser {{
  user(login:"{}") {{
    bio
    name
    login
    websiteUrl
    twitterUsername
    repositories(
      orderBy: {{field: STARGAZERS, direction: DESC}}
      affiliations: OWNER
      first: 1
    ) {{
      edges {{
        node {{
          forkCount
          name
          stargazerCount
        }}
      }}
    }}
    avatarUrl
    email
  }}
  }}""".format(login)


def count_user_in_json(json_array, login):
    count = 0
    for user in json_array:
        if (user == {}):
            continue
        print(user)
        if (user['login'] == login):
            count += 1
    return count


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
