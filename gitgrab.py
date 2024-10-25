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

USER_NAME = input("Qual o nome de usuário: ")

def get_user_repositories(user):
    url = f"https://api.github.com/users/{user}/repos"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao obter repositórios: {response.status_code}")
        return []
    return [repo for repo in response.json() if not repo['fork']]  # Filtra repositórios fork

def get_user_info(user):
    url = f"https://api.github.com/users/{user}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao obter detalhes do usuário: {response.status_code}")
        return None

    user_data = response.json()
    filtered_data = {
        "Usuario": user_data.get("login"),          
        "ID": user_data.get("id"),      
        "Nome completo": user_data.get("name"),    
        "localizacao": user_data.get("location"),  
        "Email pessoal": user_data.get("email"),    
        "Biografia": user_data.get("bio"),          
        "Criado em": user_data.get("created_at"),  
        "Atualizado em": user_data.get("updated_at")
    }
    filtered_data = {k: v for k, v in filtered_data.items() if v is not None}
    return filtered_data if filtered_data else None


def get_commit_emails(user, repo):
    url = f"https://api.github.com/repos/{user}/{repo}/commits"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erro ao obter commits do repositório {repo}: {response.status_code}")
        return None

    emails = set()
    for commit in response.json():
        try:
            email = commit['commit']['author']['email']
            if 'noreply' not in email:  # Filtra e-mails genéricos
                emails.add(email)
        except KeyError:
            pass
    return emails

def main():
    user_info = get_user_info(USER_NAME)
    if user_info:
        print(f"\n{TextColor.GREEN}Informações do usuário {USER_NAME}:{TextColor.END}")
        for key, value in user_info.items():
            print(f"{key}: {value}")

    repos = get_user_repositories(USER_NAME)
    if not repos:
        print("Nenhum repositório encontrado.")
        return

    print(f"\nRepositórios com email de {USER_NAME}:")
    for repo in repos:
        print(f"- {repo['name']}")
        emails = get_commit_emails(USER_NAME, repo['name'])
        if emails:
            print(f"  E-mails encontrados: {', '.join(emails)}")
        else:
            print("  Nenhum e-mail encontrado.")

if __name__ == "__main__":
    main()
