import requests
import sys
from datetime import datetime


class Colors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    END = '\033[0m'


class GitHubScraper:
    def __init__(self):
        self.api_base = "https://api.github.com"
        self.banner = f"""{Colors.YELLOW}                                   
     _ _   _____ _____ _____ _____ 
 ___|_| |_|   __| __  |  _  | __  |
| . | |  _|  |  |    -|     | __ -|
|_  |_|_| |_____|__|__|__|__|_____| 1.0
|___|                              
{Colors.END}"""

    def display_banner(self):
        print(self.banner)
        print(f"{Colors.BOLD}Created by:{Colors.END} AnkhCorp\n")

    def get_user_info(self, username):
        url = f"{self.api_base}/users/{username}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            user_data = response.json()
            
            if user_data.get("created_at"):
                created_date = datetime.strptime(user_data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                user_data["created_at"] = created_date.strftime("%Y-%m-%d %H:%M:%S")
            
            if user_data.get("updated_at"):
                updated_date = datetime.strptime(user_data["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                user_data["updated_at"] = updated_date.strftime("%Y-%m-%d %H:%M:%S")
                
            filtered_data = {
                "Username": user_data.get("login"),          
                "ID": user_data.get("id"),      
                "Name": user_data.get("name"),    
                "Location": user_data.get("location"),  
                "Email": user_data.get("email"),    
                "Biography": user_data.get("bio"),
                "Public repos": user_data.get("public_repos"),
                "Followers": user_data.get("followers"),
                "Following": user_data.get("following"),
                "Created on": user_data.get("created_at"),  
                "Updated on": user_data.get("updated_at")
            }
            
            return {k: v for k, v in filtered_data.items() if v is not None}
            
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                print(f"{Colors.RED}Error: User '{username}' not found{Colors.END}")
            else:
                print(f"{Colors.RED}Error fetching user data: {err}{Colors.END}")
            return None
        except Exception as err:
            print(f"{Colors.RED}Unexpected error: {err}{Colors.END}")
            return None

    def get_repositories(self, username):
        url = f"{self.api_base}/users/{username}/repos"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            repos = [repo for repo in response.json() if not repo.get('fork')]
            
            repos.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            return repos
        except requests.exceptions.HTTPError as err:
            print(f"{Colors.RED}Error retrieving repositories: {err}{Colors.END}")
            return []
        except Exception as err:
            print(f"{Colors.RED}Unexpected error: {err}{Colors.END}")
            return []

    def get_commit_emails(self, username, repo_name):
        url = f"{self.api_base}/repos/{username}/{repo_name}/commits"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            emails = set()
            for commit in response.json():
                try:
                    email = commit['commit']['author']['email']
                    name = commit['commit']['author']['name']
                    
                    if 'noreply' not in email and '@users.noreply.github.com' not in email:
                        emails.add((name, email))
                except (KeyError, TypeError):
                    continue
                    
            return emails
            
        except requests.exceptions.HTTPError:
            return set()
        except Exception as err:
            print(f"{Colors.RED}Error with commit data: {err}{Colors.END}")
            return set()
            
    def get_public_ssh_keys(self, username):
        url = f"{self.api_base}/users/{username}/keys"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            keys = response.json()
            return keys
        except requests.exceptions.HTTPError as err:
            print(f"{Colors.RED}Error retrieving SSH keys: {err}{Colors.END}")
            return []
        except Exception as err:
            print(f"{Colors.RED}Unexpected error: {err}{Colors.END}")
            return []

    def display_user_info(self, user_info):
        if not user_info:
            return
            
        print(f"\n{Colors.GREEN}📊 User Information{Colors.END}")
        print("─" * 50)
        
        for key, value in user_info.items():
            if key in ["Username", "Name", "ID"]:
                print(f"{Colors.BOLD}{key}:{Colors.END} {value}")
            elif key in ["Email"]:
                print(f"{Colors.BLUE}{key}:{Colors.END} {value}")
            else:
                print(f"{key}: {value}")

    def display_repositories(self, username, repos):
        if not repos:
            print(f"\n{Colors.YELLOW}No repositories found for {username}{Colors.END}")
            return
            
        print(f"\n{Colors.GREEN}📁 Repositories ({len(repos)}){Colors.END}")
        print("─" * 50)
        
        for idx, repo in enumerate(repos[:10], 1):
            print(f"{idx}. {Colors.BOLD}{repo['name']}{Colors.END}")
            if repo.get('description'):
                print(f"   {repo['description']}")
            
            emails = self.get_commit_emails(username, repo['name'])
            if emails:
                print(f"   {Colors.BLUE}Emails in commits:{Colors.END}")
                for name, email in emails:
                    print(f"   → {name}: {email}")
            print()
            
        if len(repos) > 10:
            print(f"...and {len(repos) - 10} more repositories")

    def display_ssh_keys(self, username, ssh_keys):
        if not ssh_keys:
            print(f"\n{Colors.YELLOW}No public SSH keys found for {username}{Colors.END}")
            return
            
        print(f"\n{Colors.GREEN}🔑 Public SSH Keys ({len(ssh_keys)}){Colors.END}")
        print("─" * 50)
        
        for idx, key in enumerate(ssh_keys, 1):
            print(f"{idx}. {Colors.BOLD}ID:{Colors.END} {key['id']}")
            
            # Display the complete key
            print(f"   {Colors.BLUE}Key:{Colors.END}")
            print(f"   {key['key']}")
            
            # Add a separator between keys
            if idx < len(ssh_keys):
                print("\n" + "·" * 40 + "\n")

    def run(self):
        self.display_banner()
        
        username = input(f"{Colors.BOLD}GitHub Username:{Colors.END} ").strip()
        if not username:
            print(f"{Colors.RED}Error: Username cannot be empty{Colors.END}")
            return

        print(f"\n{Colors.YELLOW}Searching for {username}...{Colors.END}")
        
        user_info = self.get_user_info(username)
        if not user_info:
            return
            
        self.display_user_info(user_info)
        
        repos = self.get_repositories(username)
        self.display_repositories(username, repos)
        
        ssh_keys = self.get_public_ssh_keys(username)
        self.display_ssh_keys(username, ssh_keys)


if __name__ == "__main__":
    try:
        scraper = GitHubScraper()
        scraper.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Program terminated by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.END}")
        sys.exit(1)
