import os
import subprocess

GITHUB_TOKEN = "ваш токен"

GITHUB_API_URL = "https://api.github.com"


def run_command(cmd):
    res = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if res.returncode:
        raise Exception(res.stderr)
    return res.stdout


def list_repositories():
    out = run_command(
        f'curl -H "Authorization: token {GITHUB_TOKEN}" {GITHUB_API_URL}/user/repos'
    )
    import json

    repos = json.loads(out)
    choices = {}
    for i, r in enumerate(repos, 1):
        print(i, r["name"] if r.get("name") else "(no name)")
        choices[i] = r
    return choices


def main():
    cwd = os.getcwd()
    repos = list_repositories()
    idx = int(input("Выберите номер: "))
    repo = repos[idx]
    path = os.path.join("repos", repo["name"])
    if not os.path.exists(path):
        print("Клонирую", repo["name"])
        run_command(f'git clone {repo["clone_url"]} {path}')
    else:
        print("Открываю", repo["name"])
    os.chdir(path)
    status = run_command("git status --short")
    if status:
        print("Изменения:\n", status)
        if input("Закоммитить? y/n: ").lower() == "y":
            run_command("git add .")
            msg = input("Сообщение: ")
            run_command(f'git commit -m "{msg}"')
            if input("Пуш? y/n: ").lower() == "y":
                run_command("git push")
    else:
        print("Нет изменений")
    if input("Создать PR? y/n: ").lower() == "y":
        branch = run_command("git branch --show-current").strip()
        import json

        data = {"title": "PR", "body": "", "head": branch, "base": "main"}
        run_command(
            f'curl -X POST -H "Authorization: token {GITHUB_TOKEN}" '
            f'-H "Content-Type: application/json" '
            f'-d \'{json.dumps(data)}\' {repo["url"]}/pulls'
        )
        print("PR создан")
    os.chdir(cwd)


if __name__ == "__main__":
    main()