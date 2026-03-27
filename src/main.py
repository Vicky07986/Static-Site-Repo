import os
import shutil
from textnode import TextNode, TextType
from gencontent import generate_page, generate_pages_recursive

def copy_directory_recursive(src, dst):
    """
    Recursively copy all contents from src directory to dst directory.
    """
    if os.path.exists(dst):
        print(f"Removing existing destination directory: {dst}")
        shutil.rmtree(dst)

    os.mkdir(dst)
    print(f"Created destination directory: {dst}")

    def _copy(src_dir, dst_dir):
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dst_path = os.path.join(dst_dir, item)

            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
                print(f"Copied file: {src_path} -> {dst_path}")
            else:
                os.mkdir(dst_path)
                print(f"Created directory: {dst_path}")
                _copy(src_path, dst_path)

    _copy(src, dst)

def main():
    copy_directory_recursive("static", "public")
    generate_pages_recursive("content", "template.html", "public")

if __name__ == "__main__":
    main()
