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


def query_builder_string(query: dict):
    grapqhql_query = ""
    if (query['user']):
        grapqhql_query += f"user:{query['user']}"
    if (len(query['location']) > 0):
        for location in query['location']:
            grapqhql_query += f" location:{location}"
    if (query['bio']):
        grapqhql_query += f"{query['bio']} in:bio"

    return grapqhql_query


def query_list_user(location='Senegal'):
    return """query ListUsers($query: String = "location: {}") {{
  search(type: USER, query: $query, first: 100) {{
    userCount
    nodes {{
      ... on User {{
        name
        login
      	avatarUrl
      }}
    }}
    pageInfo {{
      endCursor
      hasNextPage
    }}
  }}
}}""".format(location)


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
