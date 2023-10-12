import subprocess

# Buat fungsi untuk menginstal paket dari requirements.txt
def install_requirements():
    try:
        subprocess.call(["pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Error installing requirements: {e}")

if __name__ == "__main__":
    install_requirements()