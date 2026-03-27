import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_false(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        node2 = TextNode("This is another text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_eq_code(self):
        node = TextNode("This is a code text test", TextType.CODE)
        node2 = TextNode("This is a code text test", TextType.CODE)
        self.assertEqual(node, node2)

    def test_eq_url(self):
        node = TextNode("This is a url link test", TextType.LINK)
        node2 = TextNode("This is a url link test", TextType.LINK)
        self.assertEqual(node, node2)

    def test_eq_image(self):
        node = TextNode("This is an image test", TextType.IMAGE)
        node2 = TextNode("This is an image test", TextType.IMAGE)
        self.assertEqual(node, node2)

    def test_eq_url_with_link(self):
        node = TextNode("Click here", TextType.LINK, "https://boot.dev")
        node2 = TextNode("Click here", TextType.LINK, "https://boot.dev")
        self.assertEqual(node, node2)

    def test_eq_url_different(self):
        node = TextNode("Click here", TextType.LINK, "https://boot.dev")
        node2 = TextNode("Click here", TextType.LINK, "https://other.com")

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code(self):
        node = TextNode("print('hello')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('hello')")

    def test_link(self):
        node = TextNode("Click me", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click me")
        self.assertEqual(html_node.props["href"], "https://example.com")

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props["src"], "https://example.com/image.png")
        self.assertEqual(html_node.props["alt"], "Alt text")

    def test_invalid_type(self):
        node = TextNode("Invalid", "not_a_type")
        with self.assertRaises(Exception):
            text_node_to_html_node(node)

if __name__ == "__main__":
    unittest.main()
