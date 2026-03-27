from enum import Enum
import re
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, ParentNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text: {node.text}")

        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                if part:
                    new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text):
    image = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(image, text)
    return matches

def extract_markdown_links(text):
    link = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(link, text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        images = extract_markdown_images(node.text)

        if not images:
            new_nodes.append(node)
            continue

        text = node.text

        for alt, url in images:
            markdown = f"![{alt}]({url})"

            parts = text.split(markdown, 1)

            if parts[0]:
                new_nodes.append(TextNode(parts[0], node.text_type))

            new_nodes.append(TextNode(alt, TextType.IMAGE, url))

            text = parts[1] if len(parts) > 1 else ""

        if text:
            new_nodes.append(TextNode(text, node.text_type))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)

        if not links:
            new_nodes.append(node)
            continue

        text = node.text

        for anchor, url in links:
            markdown = f"[{anchor}]({url})"

            parts = text.split(markdown, 1)

            if parts[0]:
                new_nodes.append(TextNode(parts[0], node.text_type))

            new_nodes.append(TextNode(anchor, TextType.LINK, url))

            text = parts[1] if len(parts) > 1 else ""

        if text:
            new_nodes.append(TextNode(text, node.text_type))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

    return nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    block_strings = [block.strip() for block in blocks if block.strip()]
    return block_strings

class BlockType(Enum):
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    PARAGRAPH = "paragraph"

def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    is_ordered = True
    for i, line in enumerate(lines, start=1):
        if not re.match(rf"^{i}\. ", line):
            is_ordered = False
            break
    if is_ordered:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.HEADING:
            children.append(handle_heading(block))
        elif block_type == BlockType.PARAGRAPH:
            children.append(handle_paragraph(block))
        elif block_type == BlockType.QUOTE:
            children.append(handle_quote(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(handle_unordered_list(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(handle_ordered_list(block))
        elif block_type == BlockType.CODE:
            children.append(handle_code(block))

    return ParentNode(tag="div", children=children)

def handle_heading(block):
    level = len(block.split(" ")[0])
    text = block[level + 1:]
    return ParentNode(
        tag=f"h{level}",
        children=text_to_children(text)
    )


def handle_paragraph(block):
    text = block.replace("\n", " ")
    text = " ".join(text.split())
    return ParentNode(
        tag="p",
        children=text_to_children(text)
    )


def handle_quote(block):
    lines = block.split("\n")
    cleaned = [line.lstrip("> ").strip() for line in lines]
    text = " ".join(cleaned)
    return ParentNode(
        tag="blockquote",
        children=text_to_children(text)
    )


def handle_unordered_list(block):
    items = block.split("\n")
    li_nodes = []

    for item in items:
        text = item.lstrip("- ").strip()
        li_nodes.append(
            ParentNode(
                tag="li",
                children=text_to_children(text)
            )
        )

    return ParentNode(tag="ul", children=li_nodes)


def handle_ordered_list(block):
    items = block.split("\n")
    li_nodes = []

    for item in items:
        text = item.split(". ", 1)[1]
        li_nodes.append(
            ParentNode(
                tag="li",
                children=text_to_children(text)
            )
        )

    return ParentNode(tag="ol", children=li_nodes)


def handle_code(block):
    lines = block.split("\n")
    code_lines = lines[1:-1]
    cleaned_lines = [line.lstrip() for line in code_lines]
    code_text = "\n".join(cleaned_lines) + "\n"

    text_node = TextNode(code_text, TextType.TEXT)
    code_child = text_node_to_html_node(text_node)

    return ParentNode(
        tag="pre",
        children=[
            ParentNode(tag="code", children=[code_child])
        ]
    )

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]

def extract_title(markdown):
    lines = markdown.splitlines()

    for line in lines:
        line = line.strip()

        if line.startswith("# "):
            return line[2:].strip()

    raise Exception("No H1 header found in markdown")
