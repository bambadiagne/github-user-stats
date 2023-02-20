# Github Users Stats

<b>An API with (Flask+GraphQL+cron) to retrieve statistics from github users according to defined criteria</b>

## Installation

<b>You must generate github token from your account to make requests.
After that add that token to the environments variable of your OS.</b>

```bash
pip install -r requirements.txt
python3 app.py
```

<b>Also you can run the docker image with these commands</b>

```bash
docker build . -t flask-graphql-github
docker run --env GITHUB_TOKEN=YOUR_TOKEN -dp 5000:5000 flask-graphql-github
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
           {
            "contributionsCollection": {
                "contributionCalendar": {
                    "totalContributions": 1287
                },
                "totalCommitContributions": 0
            },
            "location": "Senegal",
            "login": "ibrahima92",
            "name": "Ibrahima Ndaw"
        },
        {
            "contributionsCollection": {
                "contributionCalendar": {
                    "totalContributions": 316
                },
                "totalCommitContributions": 124
            },
            "location": "Dakar, Senegal",
            "login": "ManuSquall",
            "name": "Charles Emmanuel S. Ndiaye"
        },
         {
            "contributionsCollection": {
                "contributionCalendar": {
                    "totalContributions": 396
                },
                "totalCommitContributions": 326
            },
            "location": "Senegal,Dakar",
            "login": "bambadiagne",
            "name": "Ahmadou Bamba Diagne"
        },

     }
```

<b>Complete users is available on: [users.json](users.json)</b>

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
   GET /users/contributions/senegal
 {
  "avatarUrl": "https://avatars.githubusercontent.com/u/45278724?u=8d5129d655e9eafebcd725944bf401ca0ba93feb&v=4",
  "bio": "Full-stack Developper Python-JS  | Devops Enthusiast | CTF player",
  "email": "diagne.bambahmadou@gmail.com",
  "login": "bambadiagne",
  "most_starred_repo": {
    "forkCount": 0,
    "name": "github-user-stats",
    "stargazerCount": 9
  },
  "most_used_anguages": [
    "JavaScript",
    "HTML",
    "CSS",
    "Java",
    "Python"
  ],
  "name": "Ahmadou Bamba Diagne",
  "twitterUsername": "ahmadou_elkha",
  "websiteUrl": "https://ahmadoubambadiagne.tech/"
}
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](LICENSE.md)
