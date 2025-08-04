import os
import subprocess

GITHUB_TOKEN = "ваш токен"

GITHUB_API_URL = "https://api.github.com"


def run_command(command):
    """Выполнение команды в терминале"""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Ошибка: {result.stderr}")
        raise Exception(result.stderr)
    return result.stdout


def list_repositories():
    """Список репозиториев пользователя"""
    print("Ваши репозитории:")
    command = f"curl -H \"Authorization: token {GITHUB_TOKEN}\" {GITHUB_API_URL}/user/repos"
    output = run_command(command)

    import json
    repos = json.loads(output)

    repo_dict = {}
    for i, repo in enumerate(repos, start=1):
        print(f"{i}. {repo['name']} - {repo.get('description', 'Нет описания')}")
        repo_dict[i] = repo

    return repo_dict

def clone_or_open_repo(repo):
    """Клонирование или открытие локального репозитория"""
    local_path = os.path.join("./repos", repo['name'])
    if not os.path.exists(local_path):
        print(f"Клонирование репозитория {repo['name']}...")
        run_command(f"git clone {repo['clone_url']} {local_path}")
    else:
        print(f"Открытие локального репозитория {repo['name']}...")
    return local_path


def check_repo_status(local_path):
    """Проверка состояния репозитория"""
    print("Проверка изменений...")
    os.chdir(local_path)
    status = run_command("git status --short")
    if status:
        print("Есть несохранённые изменения!")
        print(status)
    else:
        print("Нет несохранённых изменений.")
    os.chdir("../../")


def commit_and_push(local_path):
    """Добавление изменений, коммит и пуш"""
    os.chdir(local_path)
    if input("Добавить все изменения и закоммитить? (y/n): ").lower() == 'y':
        run_command("git add .")
        message = input("Введите сообщение для коммита: ")
        run_command(f"git commit -m \"{message}\"")
        print("Изменения закоммичены!")
        if input("Запушить изменения? (y/n): ").lower() == 'y':
            run_command("git push")
            print("Изменения успешно запушены!")
    os.chdir("../../")


def create_pull_request(repo):
    """Создание Pull Request"""
    if input("Создать Pull Request? (y/n): ").lower() == 'y':
        branch_name = run_command("git branch --show-current").strip()
        data = {
            "title": "Новый Pull Request",
            "body": "Описание изменений",
            "head": branch_name,
            "base": "main"
        }
        import json
        command = f"curl -X POST -H \"Authorization: token {GITHUB_TOKEN}\" -H \"Content-Type: application/json\" -d '{json.dumps(data)}' {repo['url']}/pulls"
        run_command(command)
        print("Pull Request успешно создан!")


if __name__ == "__main__":
    repos = list_repositories()
    repo_id = int(input("Выберите репозиторий по ID: "))
    selected_repo = repos[repo_id]

    local_repo_path = clone_or_open_repo(selected_repo)
    check_repo_status(local_repo_path)
    commit_and_push(local_repo_path)
    create_pull_request(selected_repo)