from enum import Enum
from textnode import *
from htmlnode import *
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered list"
    ORDERED_LIST = "ordered list"

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text.count(delimiter) % 2 != 0:
            raise Exception(f'Markdown syntax error: "{delimiter}" needs to have a start and end point to be valid.')
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
        else:
            nested_nodes = []
            split_nodes = old_node.text.split(delimiter)
            for i in range(len(split_nodes)):
                inner_node = split_nodes[i]
                if inner_node == "":
                    continue
                elif i % 2 == 0:
                    nested_nodes.append(TextNode(inner_node, TextType.TEXT))
                else:
                    nested_nodes.append(TextNode(inner_node, text_type))
            new_nodes.extend(nested_nodes)
    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        images_extract = extract_markdown_images(old_node.text)
        if images_extract == []:
            new_nodes.append(old_node)
            continue
        else:
            for i in range(len(images_extract)):
                image_alt = images_extract[i][0]
                image_link = images_extract[i][1]
                split_nodes = old_node.text.split(f"![{image_alt}]({image_link})", 1)
                old_node.text = split_nodes[1]
                if split_nodes[0] != "":
                    new_nodes.append(TextNode(split_nodes[0], TextType.TEXT))
                new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
        if old_node.text:
            new_nodes.append(TextNode(old_node.text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        links_extract = extract_markdown_links(old_node.text)
        if links_extract == []:
            new_nodes.append(old_node)
            continue
        else:
            for i in range(len(links_extract)):
                link_text = links_extract[i][0]
                url = links_extract[i][1]
                split_nodes = old_node.text.split(f"[{link_text}]({url})", 1)
                old_node.text = split_nodes[1]
                if split_nodes[0] != "":
                    new_nodes.append(TextNode(split_nodes[0], TextType.TEXT))
                new_nodes.append(TextNode(link_text, TextType.LINK, url))
        if old_node.text:
            new_nodes.append(TextNode(old_node.text, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    lines = [TextNode(text, TextType.TEXT)]
    if re.findall(r"\*\*([^*]+)\*\*", text):
        lines = split_nodes_delimiter(lines, "**", TextType.BOLD)
    if re.findall(r"\_([^_])+\_", text):
        lines = split_nodes_delimiter(lines, "_", TextType.ITALIC)
    if re.findall(r"\`([^`])+\`", text):
        lines = split_nodes_delimiter(lines, "`", TextType.CODE)
    if extract_markdown_images(text):
        lines = split_nodes_image(lines)
    if extract_markdown_links(text):
        lines = split_nodes_link(lines)
    return lines

#def markdown_to_blocks(markdown):
    #blocks = []
    #if re.findall(r"\n{2}", markdown):
        #blocks = [block.strip() for block in markdown.split("\n\n")]
    #for i in range(len(blocks)):
        #if re.findall(r"\n{1}", blocks[i]):
            #block = blocks[i].replace("\n", "\\n")
            #blocks[i] = block
    #return blocks
def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks

def block_to_block_type(md_block):
    if re.match(r"^#{1,6} ", md_block):
        return BlockType.HEADING
    
    if re.match(r"^(`{3}\n)[\s\S]+(`{3})$", md_block):
        return BlockType.CODE
    
    if re.match(r"^> ?", md_block):
        if not re.findall(r"\n(?!> ?)", md_block):
            return BlockType.QUOTE
        
    if re.match(r"^- ", md_block):
        if not re.findall(r"\n(?!- )", md_block):
            return BlockType.UNORDERED_LIST
        
    if re.match(r"^1. ", md_block):
        lines = md_block.split("\n")
        for i in range(len(lines)):
            if lines[i].startswith(f"{i + 1}. "):
                continue
            else:
                return BlockType.PARAGRAPH
            
        return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for tn in text_nodes:
        children.append(text_node_to_html_node(tn))
    return children

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            paragraph = " ".join(block.split("\n"))
            html_node = ParentNode("p", text_to_children(paragraph))
        if block_type == BlockType.HEADING:
            heading_check = block[:6]
            match = re.findall(r"#+", heading_check)
            level = max(len(m) for m in match)
            html_node = ParentNode(f"h{level}", text_to_children(block[level + 1:]))
        if block_type == BlockType.CODE:
            lines = block.split("\n")
            code_text = "\n".join(lines[1:-1]) + "\n"
            html_node = ParentNode("pre", [ParentNode("code", [LeafNode(None, code_text)])])
        if block_type == BlockType.QUOTE:
            quote = []
            for line in block.split("\n"):
                match = re.findall(r"^> ?", line)
                start = max(len(m) for m in match)
                quote.append(line[start:])
            sentence = " ".join(quote)
            html_node = ParentNode("blockquote", text_to_children(sentence))
        if block_type == BlockType.UNORDERED_LIST:
            li_nodes = []
            items = []
            items = block.split("\n")
            for item in items:
                item_text = item[2:]
                li_nodes.append(ParentNode("li", text_to_children(item_text)))
            html_node = ParentNode("ul", li_nodes)
        if block_type == BlockType.ORDERED_LIST:
            li_nodes = []
            items = []
            items = block.split("\n")
            for item in items:
                item_text = item.split(". ", 1)
                li_nodes.append(ParentNode("li", text_to_children(item_text[1])))
            html_node = ParentNode("ol", li_nodes)
        html.append(html_node)
    return ParentNode("div", html)

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        lines = block.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
    return None
