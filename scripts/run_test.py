import subprocess

if __name__ == "__main__":
    subprocess.run(["uv", "run", "pytest"], shell=True)
