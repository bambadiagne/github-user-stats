# Github Users Stats

<b>An API with (Flask+GraphQL+cron) to retrieve statistics from github users according to defined criteria.
Data is updated using github actions cron job</b>


[![Made-In-Senegal](https://github.com/GalsenDev221/made.in.senegal/blob/master/assets/badge.svg)](https://github.com/GalsenDev221/made.in.senegal)


## Project stack 
| Stack | Logo |
| ----- | ---- |
| Docker| <a href="https://www.docker.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="40" height="40"/> </a>     |
| Flask | <a href="https://flask.palletsprojects.com/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/pocoo_flask/pocoo_flask-icon.svg" alt="flask" width="40" height="40"/> </a> |
| GraphQL |<a href="https://www.postgresql.org" target="_blank" rel="noreferrer"> <img src="https://graphql.org/_next/static/media/logo.ad338028.svg" alt="postgresql" width="40" height="40"/> </a> |

## Installation

<b>You must generate github token from your account to make requests.
After that add that token to the environments variable of your OS.</b>
And also set env variable ```FLASK_DEBUG``` to 0 for dev and 1 for prod

```bash
pip install -r requirements.txt
python3 app.py
```

<b>Also you can run the docker image with these commands</b>

```bash
docker build . -t flask-graphql-github
docker run -e GITHUB_TOKEN=YOUR_TOKEN -e FLASK_DEBUG=1 -dp 5000:5000 flask-graphql-github
```

## Usage

<br><b>With this tool, you will be able to know for example who uses a certain language (go, python, java,...), retrieve all users from a location for your dataset for example, it can also help recruiters...</b>

## Project endpoints

<br><b>The API endpoints are listed below:

- [Fetch all senegalese github contributions](#senegalese_contributions) : `GET /users/contributions/senegal`
- [Search users by filter](#search_users) : `GET /users/search`
- [Retrieve user's info by this username](#fetch_user) : `GET /users/:username`
  </b>

## Examples

<br><b>There are some examples below:</b>

<div id="senegalese_contributions">

<b>Some senegalese stats</b>

```bash
   GET /users/contributions/senegal
     {
            "avatarUrl": "https://avatars.githubusercontent.com/u/32209399?u=6737dbfd36f70ed8a089125de748b0de134d0e44&v=4",
            "contributionsCollection": {
                "contributionCalendar": {
                    "totalContributions": 1581
                },
                "restrictedContributionsCount": 1581,
                "totalCommitContributions": 0
            },
            "createdAt": "2017-09-22T22:31:30Z",
            "location": "Senegal",
            "login": "ibrahima92",
            "name": "Ibrahima Ndaw"
        },
       {
            "avatarUrl": "https://avatars.githubusercontent.com/u/29026887?u=4c054c103f1388717423287186dcbff94dfecec7&v=4",
            "contributionsCollection": {
                "contributionCalendar": {
                    "totalContributions": 248
                },
                "restrictedContributionsCount": 56,
                "totalCommitContributions": 86
            },
            "createdAt": "2017-05-28T21:46:10Z",
            "location": "Dakar, Senegal",
            "login": "ManuSquall",
            "name": "Charles Emmanuel S. Ndiaye"
        },
         {
            "avatarUrl": "https://avatars.githubusercontent.com/u/45278724?u=8d5129d655e9eafebcd725944bf401ca0ba93feb&v=4",
            "contributionsCollection": {
                "contributionCalendar": {
                    "totalContributions": 358
                },
                "restrictedContributionsCount": 0,
                "totalCommitContributions": 292
            },
            "createdAt": "2018-11-23T03:55:39Z",
            "location": "Senegal,Dakar",
            "login": "bambadiagne",
            "name": "Ahmadou Bamba Diagne"
        },

     }
```

<b>Complete users(Senegal) is available on: [users.json](users.json)</b>

</div>
<div id="search_users">

<b>This query retrieve all users based on senegal and who have written python</b>

```bash
   GET /users/search?location=Senegal&language=python
     {
       {
        "avatarUrl": "https://avatars.githubusercontent.com/u/84446?v=4",
        "bio": "Codito ergo sum",
        "login": "dofbi",
        "name": "dofbi.eth"
      },
      {
        "avatarUrl": "https://avatars.githubusercontent.com/u/122930?v=4",
        "bio": null,
        "login": "wilane",
        "name": "Ousmane Wilane"
      },
      {
        "avatarUrl": "https://avatars.githubusercontent.com/u/65301551?u=84efa9fad441e3af6117cb25aada2428429c7611&v=4",
        "bio": "Software Developer Consultant",
        "login": "EdgarEmmanuel",
        "name": "Emmanuel Edgar"
      },
       {
        "avatarUrl": "https://avatars.githubusercontent.com/u/61096522?u=a9d5b1e47e155662af2c733d6e946f825d7099d1&v=4",
        "bio": "Full Stack Dev - Entrepreneur - Tutor\r\n#theycallmeX\r\n\r\n\r\n\r\nhttp://mrmbengue.rf.gd\r\nhttps://www.pinpaya.com/tutor/5578/\r\n#code\r\n#imjustaletter\r\n@Tek-Tech  ",
        "login": "dev0ps221",
        "name": "El Hadji Seybatou Mbengue"
      },

     }
```

If you want to fetch more,you must add the _after_ field

</div>
<div id="fetch_user">

<b>We fetch an user with login :bambadiagne and we get informations like(most starred projet,profilePicture,website,...</b>

```bash
   GET /users/bambadiagne
 {
  "avatarUrl": "https://avatars.githubusercontent.com/u/45278724?u=8d5129d655e9eafebcd725944bf401ca0ba93feb&v=4",
  "bio": "Full-stack Developper Python-JS  | Devops Enthusiast | CTF player",
  "contributionsCollection": {
    "contributionCalendar": {
      "totalContributions": 359
    },
    "restrictedContributionsCount": 0,
    "totalCommitContributions": 293
  },
  "email": "diagne.bambahmadou@gmail.com",
  "location": "Senegal,Dakar",
  "login": "bambadiagne",
  "most_starred_repo": {
    "forkCount": 0,
    "name": "github-user-stats",
    "stargazerCount": 9
  },
  "most_used_languages": [
    "JavaScript",
    "HTML",
    "CSS",
    "Java",
    "Python"
  ],
  "name": "Ahmadou Bamba Diagne",
  "twitterUsername": "AhmadouElkha",
  "websiteUrl": "https://ahmadoubambadiagne.tech/"
}
```
# Authors
<a href="https://github.com/bambadiagne/github-user-stats/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=bambadiagne/github-user-stats" />
</a>

## Contributing

1. Click on the "Fork" button at the top right to create a copy   of the repository in your own GitHub account.

2. Clone the forked repository to your local machine:
3. Create branch from master, make changes and start PR   


## License

[MIT](LICENSE.md)
