DEFAULT_USERNAME="torvalds"


def query_list_user_by_location(location='Senegal'):
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

def query_all_senegalese(number,after=''):
  return """query GithubSenegaleseUser($query: String = "location:Senegal") {{
  search(query: $query, type: USER, first:{0}, {1}) {{
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
}}""".format(str(number),"after: \"{}\"".format(after) if(after) else '')
  
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
  
  
