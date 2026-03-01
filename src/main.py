from textnode import *
from splitnodes import *
from htmlnode import *
import os
import shutil
import sys

def main():
    refresh_public()
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    generate_pages_recursive("content", "template.html", "docs", basepath)
    return

def refresh_public():
    if os.path.exists("./docs"):
        full_path_public = os.path.abspath("./docs")
        try:
            shutil.rmtree(full_path_public)
            print(f"Removed '{full_path_public}'.")
        except OSError as e:
            print(f"Error: {e.strerror}")
        except PermissionError as e:
            print(f"Permission denied: {e}")

    os.makedirs("./docs", exist_ok=True)
    full_path_public = os.path.abspath("./docs")
    print(f"Created new directory '{full_path_public}'.")

    full_static_dir = os.path.abspath("./static")
    copy_files_recursive(full_static_dir, full_path_public)

def copy_files_recursive(source, destination):
    to_copy = os.listdir(source)
    for content in to_copy:
        src_path = os.path.join(source, content)
        dst_path = os.path.join(destination, content)

        if os.path.isdir(src_path):
            os.makedirs(dst_path, exist_ok=True)
            print(f"Created directory '{dst_path}'.")
            copy_files_recursive(src_path, dst_path)
        
        elif os.path.isfile(src_path):
            print(f"Found file '{content}'")
            try:
                shutil.copy(src_path, dst_path)
                print(f"Copied '{content}' to '{destination}'.")
            except FileNotFoundError as e:
                print(f"Error: {e}")
            except PermissionError as e:
                print(f"Permission denied: {e}")
    
    print(f"...completed...")

def generate_page(from_path, tempalte_path, dest_path, base_path):
    print(f"Generating page from {from_path} to {dest_path} using {tempalte_path}")

    try:
        with open(from_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{from_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        with open(tempalte_path, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{tempalte_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    processed_md = markdown_to_html_node(content)
    html_content = processed_md.to_html()
    title = extract_title(content)
    template_title = template.replace("{{ Title }}", title)
    template_title_content = template_title.replace("{{ Content }}", html_content)
    template_title_content = template_title_content.replace('href="/', f'href="{base_path}')
    template_title_content = template_title_content.replace('src="/', f'src="{base_path}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(template_title_content)

def generate_pages_recursive(dir_path_content, tempalte_path, dest_dir_path, base_path):
    current_ls = os.listdir(dir_path_content)

    for item in current_ls:
        src_path = os.path.join(dir_path_content, item)
        dst_path = os.path.join(dest_dir_path, item)

        if os.path.isdir(src_path):
            os.makedirs(dst_path, exist_ok=True)
            generate_pages_recursive(src_path, tempalte_path, dst_path, base_path)

        elif os.path.isfile(src_path):
            if item.endswith(".md"):
                generate_page(src_path, tempalte_path, os.path.join(os.path.dirname(dst_path), "index.html"), base_path)

main()
