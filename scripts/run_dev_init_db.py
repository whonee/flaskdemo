import subprocess

if __name__ == "__main__":
    cmd_init_db = "flask --app app init-db"
    cmd_run_app = "flask --app app run --debug"

    subprocess.run(cmd_init_db, shell=True)
    subprocess.run(cmd_run_app, shell=True)
