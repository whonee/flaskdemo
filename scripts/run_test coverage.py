import subprocess

if __name__ == "__main__":
    subprocess.run(["uv", "run", "coverage", "run", "-m", "pytest"], shell=True)
    subprocess.run(["coverage", "report"], shell=True)
    subprocess.run(["coverage", "html"], shell=True)
