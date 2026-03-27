import unittest
import re
from enum import Enum
from htmlnode import HTMLNode
from textnode import TextNode, TextType
from inline_markdown import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node, handle_heading, handle_paragraph, handle_quote, handle_unordered_list, handle_ordered_list, handle_code, extract_title

class TestSplitNodesDelimiter(unittest.TestCase):

    def test_single_code_block(self):
        node = TextNode("This is `code` here", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ]

        self.assertEqual(result, expected)

    def test_multiple_code_blocks(self):
        node = TextNode("A `one` and `two` test", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("A ", TextType.TEXT),
            TextNode("one", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("two", TextType.CODE),
            TextNode(" test", TextType.TEXT),
        ]

        self.assertEqual(result, expected)

    def test_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(result, [node])

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This is `broken text", TextType.TEXT)

        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_non_text_node_unchanged(self):
        node = TextNode("already code", TextType.CODE)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(result, [node])

    def test_mixed_nodes(self):
        nodes = [
            TextNode("Start `code`", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
        ]

        result = split_nodes_delimiter(nodes, "`", TextType.CODE)

        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode("already bold", TextType.BOLD),
        ]

        self.assertEqual(result, expected)

    def test_empty_segments_ignored(self):
        node = TextNode("`code`", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("code", TextType.CODE),
        ]

        self.assertEqual(result, expected)

    def test_bold_delimiter(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]

        self.assertEqual(result, expected)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_multiple_images(self):
        text = """
        ![img1](http://a.com/1.png)
        Some text
        ![img2](http://a.com/2.png)
        """
        expected = [
            ("img1", "http://a.com/1.png"),
            ("img2", "http://a.com/2.png")
        ]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_no_images(self):
        text = "This text has no images."
        expected = []
        self.assertEqual(extract_markdown_images(text), expected)

    def test_empty_alt_text(self):
        text = "![](http://example.com/image.png)"
        expected = [("", "http://example.com/image.png")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_image_with_spaces(self):
        text = "![my image](http://example.com/image file.png)"
        expected = [("my image", "http://example.com/image file.png")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_malformed_markdown(self):
        text = "![alt text(http://example.com/image.png"
        expected = []
        self.assertEqual(extract_markdown_images(text), expected)

    def test_mixed_content(self):
        text = """
        Text before
        ![img](http://example.com/img.png)
        Text after
        """
        expected = [("img", "http://example.com/img.png")]
        self.assertEqual(extract_markdown_images(text), expected)

class TestSplitNodes(unittest.TestCase):

    def test_split_nodes_image_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Just plain text")
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_split_nodes_image_single(self):
        node = TextNode("Hello ![alt](img.png) world", TextType.TEXT)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0].text, "Hello ")
        self.assertEqual(result[0].text_type, TextType.TEXT)

        self.assertEqual(result[1].text, "alt")
        self.assertEqual(result[1].text_type, TextType.IMAGE)
        self.assertEqual(result[1].url, "img.png")

        self.assertEqual(result[2].text, " world")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_split_nodes_image_multiple(self):
        node = TextNode(
            "A ![one](1.png) B ![two](2.png) C",
            TextType.TEXT
        )
        result = split_nodes_image([node])

        self.assertEqual(len(result), 5)

        self.assertEqual(result[0].text, "A ")
        self.assertEqual(result[1].text, "one")
        self.assertEqual(result[2].text, " B ")
        self.assertEqual(result[3].text, "two")
        self.assertEqual(result[4].text, " C")

    def test_split_nodes_image_no_empty_nodes(self):
        node = TextNode("![alt](img.png)", TextType.TEXT)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "alt")
        self.assertEqual(result[0].text_type, TextType.IMAGE)

    def test_split_nodes_link_no_links(self):
        node = TextNode("Just plain text", TextType.TEXT)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Just plain text")
        self.assertEqual(result[0].text_type, TextType.TEXT)

    def test_split_nodes_link_single(self):
        node = TextNode("Click [here](example.com) now", TextType.TEXT)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 3)

        self.assertEqual(result[0].text, "Click ")
        self.assertEqual(result[0].text_type, TextType.TEXT)

        self.assertEqual(result[1].text, "here")
        self.assertEqual(result[1].text_type, TextType.LINK)
        self.assertEqual(result[1].url, "example.com")

        self.assertEqual(result[2].text, " now")
        self.assertEqual(result[2].text_type, TextType.TEXT)

    def test_split_nodes_link_multiple(self):
        node = TextNode(
            "A [one](1.com) B [two](2.com) C",
            TextType.TEXT
        )
        result = split_nodes_link([node])

        self.assertEqual(len(result), 5)

        self.assertEqual(result[0].text, "A ")
        self.assertEqual(result[1].text, "one")
        self.assertEqual(result[2].text, " B ")
        self.assertEqual(result[3].text, "two")
        self.assertEqual(result[4].text, " C")

    def test_split_nodes_link_no_empty_nodes(self):
        node = TextNode("[only](link.com)", TextType.TEXT)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "only")
        self.assertEqual(result[0].text_type, TextType.LINK)

class TestTextToTextNodes(unittest.TestCase):

    def test_full_example(self):
        text = (
            "This is **text** with an _italic_ word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "and a [link](https://boot.dev)"
        )

        nodes = text_to_textnodes(text)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]

        self.assertEqual(nodes, expected)

    def test_plain_text(self):
        text = "Just a normal sentence."
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("Just a normal sentence.", TextType.TEXT)
        ]

        self.assertEqual(nodes, expected)

    def test_bold_only(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]

        self.assertEqual(nodes, expected)

    def test_italic_only(self):
        text = "This is _italic_ text"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]

        self.assertEqual(nodes, expected)

    def test_code_only(self):
        text = "Use `print()` here"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("Use ", TextType.TEXT),
            TextNode("print()", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ]

        self.assertEqual(nodes, expected)

    def test_link_only(self):
        text = "Click [here](https://example.com)"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("Click ", TextType.TEXT),
            TextNode("here", TextType.LINK, "https://example.com"),
        ]

        self.assertEqual(nodes, expected)

    def test_image_only(self):
        text = "Look ![alt text](https://img.com/img.png)"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("Look ", TextType.TEXT),
            TextNode("alt text", TextType.IMAGE, "https://img.com/img.png"),
        ]

        self.assertEqual(nodes, expected)

    def test_multiple_same_type(self):
        text = "**one** and **two**"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("one", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("two", TextType.BOLD),
        ]

        self.assertEqual(nodes, expected)

    def test_nested_order_code_protects(self):
        text = "`**not bold**`"
        nodes = text_to_textnodes(text)

        expected = [
            TextNode("**not bold**", TextType.CODE),
        ]

        self.assertEqual(nodes, expected)

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_single_block(self):
        md = "This is a single block"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["This is a single block"])

    def test_multiple_blocks(self):
        md = "Block one\n\nBlock two\n\nBlock three"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["Block one", "Block two", "Block three"])

    def test_strips_whitespace(self):
        md = "  Block one  \n\n   Block two\n\nBlock three   "
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["Block one", "Block two", "Block three"])

    def test_extra_newlines_removed(self):
        md = "Block one\n\n\n\nBlock two\n\n\nBlock three"
        result = markdown_to_blocks(md)
        self.assertEqual(result, ["Block one", "Block two", "Block three"])

    def test_empty_string(self):
        md = ""
        result = markdown_to_blocks(md)
        self.assertEqual(result, [])

    def test_only_newlines(self):
        md = "\n\n\n\n"
        result = markdown_to_blocks(md)
        self.assertEqual(result, [])

class TestBlockToBlockType(unittest.TestCase):

    def test_heading_single_hash(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_heading_multiple_hashes(self):
        self.assertEqual(block_to_block_type("### Heading"), BlockType.HEADING)

    def test_heading_max_hashes(self):
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_code_block(self):
        block = "```\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_block(self):
        block = "> This is a quote\n> Another line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_without_space(self):
        block = ">This is a quote\n>Another line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- item 1\n- item 2\n- item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list_valid(self):
        block = "1. first\n2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_invalid_sequence(self):
        block = "1. first\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_not_starting_at_one(self):
        block = "2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph(self):
        block = "This is just a normal paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_mixed_content(self):
        block = "- item 1\nnot a list item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

class TestMarkdownToHTML(unittest.TestCase):
    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        block = "## Hello world"
        node = handle_heading(block)
        self.assertEqual(node.to_html(), "<h2>Hello world</h2>")

    def test_paragraph(self):
        block = "This is a paragraph\nwith multiple lines"
        node = handle_paragraph(block)
        self.assertEqual(
            node.to_html(),
            "<p>This is a paragraph with multiple lines</p>"
        )

    def test_paragraph_with_inline(self):
        block = "This is **bold** and _italic_ text"
        node = handle_paragraph(block)
        self.assertEqual(
            node.to_html(),
            "<p>This is <b>bold</b> and <i>italic</i> text</p>"
        )

    def test_quote(self):
        block = "> This is a quote\n> second line"
        node = handle_quote(block)
        self.assertEqual(
            node.to_html(),
            "<blockquote>This is a quote second line</blockquote>"
        )

    def test_unordered_list(self):
        block = "- item one\n- item two"
        node = handle_unordered_list(block)
        self.assertEqual(
            node.to_html(),
            "<ul><li>item one</li><li>item two</li></ul>"
        )

    def test_ordered_list(self):
        block = "1. first\n2. second"
        node = handle_ordered_list(block)
        self.assertEqual(
            node.to_html(),
            "<ol><li>first</li><li>second</li></ol>"
        )

    def test_code_block(self):
        block = "```\nprint('hello')\n```"
        node = handle_code(block)
        self.assertEqual(
            node.to_html(),
            "<pre><code>print('hello')\n</code></pre>"
        )

    def test_code_block_no_inline_parsing(self):
        block = "```\n**not bold**\n```"
        node = handle_code(block)
        self.assertEqual(
            node.to_html(),
            "<pre><code>**not bold**\n</code></pre>"
        )

    def test_full_markdown_mixed(self):
        md = """# Title

This is a paragraph

- item 1
- item 2

> quote here

</> """

class TestExtractTitle(unittest.TestCase):

    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_title_with_extra_spaces(self):
        self.assertEqual(extract_title("#    Hello World   "), "Hello World")

    def test_multiline_markdown(self):
        md = """
        Some intro text

        # My Title

        More content here
        """
        self.assertEqual(extract_title(md), "My Title")

    def test_ignores_non_h1_headers(self):
        md = """
        ## Not the title
        ### Still not
        # Actual Title
        """
        self.assertEqual(extract_title(md), "Actual Title")

    def test_no_h1_raises_exception(self):
        md = """
        ## Subtitle
        Some text
        """
        with self.assertRaises(Exception):
            extract_title(md)

    def test_empty_string_raises_exception(self):
        with self.assertRaises(Exception):
            extract_title("")

    def test_hash_without_space_not_valid(self):
        md = "#Title without space"
        with self.assertRaises(Exception):
            extract_title(md)

if __name__ == "__main__":
    unittest.main()
