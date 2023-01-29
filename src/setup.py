import shutil
import os

USER_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(USER_DIR, ".config/anteater/")


def make_brushes():
    brushes_dir = os.path.join(CONFIG_DIR, "brushes")
    if not os.path.exists(brushes_dir):
        os.makedirs(brushes_dir)
        for brush in os.listdir("brushes"):
            shutil.copy(f"brushes/{brush}", f"{brushes_dir}/{brush}")


def main():
    make_brushes()
    # TODO Add more setup and config options


if __name__ == "__main__":
    main()
