import requests
import pandas as pd
import time

token = '' #i put my token here  
hdrs = {
    "Authorization": f"token {token}",
    "User-Agent": "GitHub-Data-Scraper"
}

def fetch_json(url):
    while True:
        res = requests.get(url, headers=hdrs)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 403:
            reset_time = int(res.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait_time = reset_time - int(time.time())
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            res.raise_for_status()

def get_users():
    users = []
    p = 1
    max_p = 2

    while p <= max_p:
        url = f"https://api.github.com/search/users?q=location:Sydney+followers:>100&page={p}&per_page=30"
        res = fetch_json(url)
        items = res.get('items', [])
        if not items:
            break
        users.extend(items)
        p += 1

    return users[:5]  

def get_user_details(user):
    data = fetch_json(f"https://api.github.com/users/{user['login']}")
    return {
        'login': data.get('login', ''),
        'name': data.get('name', ''),
        'company': (data.get('company', '') or '').replace('@', '').strip().upper(),
        'location': data.get('location', ''),
        'email': data.get('email', ''),
        'hireable': data.get('hireable', ''),
        'bio': data.get('bio', ''),
        'public_repos': data.get('public_repos', 0),
        'followers': data.get('followers', 0),
        'following': data.get('following', 0),
        'created_at': data.get('created_at', '')
    }

def get_user_repos(login):
    repos = []
    p = 1
    max_r = 500  

    while len(repos) < max_r:
        url = f"https://api.github.com/users/{login}/repos?page={p}&per_page=100"
        res = fetch_json(url)
        if not res:
            break
        repos.extend(res)
        if len(res) < 100:
            break
        p += 1
    return [{
        'login': login,
        'full_name': repo.get('full_name', ''),
        'created_at': repo.get('created_at', ''),
        'stargazers_count': repo.get('stargazers_count', 0),
        'watchers_count': repo.get('watchers_count', 0),
        'language': repo.get('language', ''),
        'has_projects': repo.get('has_projects', False),
        'has_wiki': repo.get('has_wiki', False),
        'license_name': repo.get('license')['key'] if repo.get('license') else ''
    } for repo in repos]

def save_csv(users_data, repos_data):
    users_df = pd.DataFrame(users_data)
    repos_df = pd.DataFrame(repos_data)
    users_df.to_csv('./data/users.csv', index=False)
    repos_df.to_csv('./data/repositories.csv', index=False)
    print("Data saved to users.csv and repositories.csv")

def main():

    users = get_users()
    users_data = []
    repos_data = []

    for user in users:
        user_details = get_user_details(user)
        users_data.append(user_details)

        user_repos = get_user_repos(user['login'])
        repos_data.extend(user_repos)

    print("Saving data to CSV files.")
    save_csv(users_data, repos_data)
    print("Data saved successfully.")


main()
