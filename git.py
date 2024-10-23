import requests

class TextColor:
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    END = '\033[0m'

text = """                                   
     _ _   _____ _____ _____ _____ 
 ___|_| |_|   __| __  |  _  | __  |
| . | |  _|  |  |    -|     | __ -|
|_  |_|_| |_____|__|__|__|__|_____| 1.0
|___|                              
"""

colored_text = TextColor.YELLOW + text + TextColor.END

bold_text = TextColor.BOLD + "Created by: " + TextColor.END + "AnkhCorp"

print(colored_text)
print(bold_text)

# Ainda precisa pegar as informações do usuário e etc.
# https://api.github.com/
# https://raw.githubusercontent.com/wahlflo/showExposedGitHubEmails/refs/heads/master/github_exposed_email_crawler/script.py

def get_user_repositories(user):
    url = f"https://api.github.com/users/{user}/repos"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao obter repositórios: {response.status_code}")
        return []
    
    repos = response.json()
    return [repo for repo in repos if not repo['fork']]  # Filtra os repositórios fork

def get_commit_emails(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/commits"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao obter commits do repositório {repo}: {response.status_code}")
        return None

    emails = set()
    commits = response.json()
    for commit in commits:
        try:
            email = commit['commit']['author']['email']
            if 'noreply' not in email:  # Filtra e-mails genéricos
                emails.add(email)
        except KeyError:
            pass
    return emails

def main():
    user = "orvituhgo"  # Substitua pelo nome do usuário desejado
    repos = get_user_repositories(user)

    if not repos:
        print("Nenhum repositório encontrado.")
        return

    print(f"Repositórios de {user}:")
    for repo in repos:
        print(f"- {repo['name']}")
        emails = get_commit_emails(user, repo['name'])
        if emails:
            print(f"  E-mails encontrados: {', '.join(emails)}")
        else:
            print("  Nenhum e-mail encontrado.")

if __name__ == "__main__":
    main()