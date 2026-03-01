from textnode import *
from splitnodes import *
from htmlnode import *
import os
import shutil

def main():
    refresh_public()
    generate_pages_recursive("content", "template.html", "public")
    return

def refresh_public():
    if os.path.exists("./public"):
        full_path_public = os.path.abspath("./public")
        try:
            shutil.rmtree(full_path_public)
            print(f"Removed '{full_path_public}'.")
        except OSError as e:
            print(f"Error: {e.strerror}")
        except PermissionError as e:
            print(f"Permission denied: {e}")

    os.mkdir("./public")
    full_path_public = os.path.abspath("./public")
    print(f"Created new directory '{full_path_public}'.")

    full_static_dir = os.path.abspath("./static")
    copy_files_recursive(full_static_dir, full_path_public)

def copy_files_recursive(source, destination):
    to_copy = os.listdir(source)
    for content in to_copy:
        src_path = os.path.join(source, content)
        dst_path = os.path.join(destination, content)

        if os.path.isdir(src_path):
            os.mkdir(dst_path)
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

def generate_page(from_path, tempalte_path, dest_path):
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

    dest_parts = dest_path.split("/")

    if not os.path.exists(dest_parts[0]):
        os.mkdir(dest_parts[0])
    if os.path.isdir(dest_path):
        print(f"Error: '{dest_path}' is a directory, a file path is needed.")
    else:
        if not dest_path.endswith(".html"):
            dest_path = os.path.splitext(dest_path)[0] + ".html"
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(template_title_content)

def generate_pages_recursive(dir_path_content, tempalte_path, dest_dir_path):
    current_ls = os.listdir(dir_path_content)

    for item in current_ls:
        src_path = os.path.join(dir_path_content, item)
        dst_path = os.path.join(dest_dir_path, item)

        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
            generate_pages_recursive(src_path, tempalte_path, dst_path)

        elif os.path.isfile(src_path):
            if item.endswith(".md"):
                generate_page(src_path, tempalte_path, dst_path)

main()
