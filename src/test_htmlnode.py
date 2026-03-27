import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

from textnode import TextNode, TextType, text_node_to_html_node

class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_multiple(self):
        node = HTMLNode(
            tag="a",
            props={"href": "https://example.com", "target": "_blank"}
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://example.com" target="_blank"'
        )

    def test_props_to_html_single(self):
        node = HTMLNode(
            tag="img",
            props={"src": "image.png"}
        )
        self.assertEqual(
            node.props_to_html(),
            ' src="image.png"'
        )

    def test_props_to_html_none(self):
        node = HTMLNode(tag="p")
        self.assertEqual(node.props_to_html(), "")

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_b(self):
        node = LeafNode("b", "Hello, world!")
        self.assertEqual(node.to_html(), "<b>Hello, world!</b>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_node_no_tag(self):
        node = LeafNode(None, "Hello world")
        self.assertEqual(node.to_html(), "Hello world")

    def test_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_single_child(self):
        child = LeafNode("p", "Hello")
        node = ParentNode("div", [child])
        self.assertEqual(node.to_html(), "<div><p>Hello</p></div>")

    def test_missing_tag_raises_error(self):
        child = LeafNode("p", "Hello")
        node = ParentNode(None, [child])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_missing_children_raises_error(self):
        node = ParentNode("div", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_nested_parent_nodes(self):
        child = LeafNode("span", "text")
        inner = ParentNode("p", [child])
        outer = ParentNode("div", [inner])

        self.assertEqual(
            outer.to_html(),
            "<div><p><span>text</span></p></div>"
        )

    def test_parent_with_multiple_children(self):
        node = ParentNode("p", [
            LeafNode("b", "Bold"),
            LeafNode(None, " normal "),
            LeafNode("i", "italic"),
        ])
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold</b> normal <i>italic</i></p>"
        )

    def test_parent_with_props(self):
        node = ParentNode("div", [LeafNode("span", "x")], {"class": "box"})
        self.assertEqual(node.to_html(), '<div class="box"><span>x</span></div>')


if __name__ == "__main__":
    unittest.main()
