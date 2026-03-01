import unittest

from textnode import *
from splitnodes import *


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
        node3 = TextNode("This is a text node", TextType.TEXT, "https://google.com")
        node4 = TextNode("This is a text node", TextType.TEXT, "https://google.com")
        self.assertEqual(node3, node4)

    def test_noteq(self):
        node = TextNode("This is a text node", TextType.ITALIC, "https://google.com")
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
        node3 = TextNode("This is a text node", TextType.TEXT, "https://google.com")
        node4 = TextNode("This is a text node", TextType.CODE, "https://google.com")
        self.assertNotEqual(node3, node4)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def split_text(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        new_nodes_check = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, new_nodes_check)
        node2 = TextNode("This is code with a **bold** word", TextType.CODE)
        new_nodes2 = split_nodes_delimiter([node2], "**", TextType.BOLD)
        new_nodes_check2 = [TextNode("This is code with a **bold** word", TextType.CODE)]
        self.assertEqual(new_nodes2, new_nodes_check2)
        node3 = TextNode("This is text with _italic at the end_", TextType.TEXT)
        new_node3 = split_nodes_delimiter([node3], "_", TextType.ITALIC)
        new_nodes_check3 = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("italic at the end", TextType.ITALIC)
        ]
        self.assertEqual(new_node3, new_nodes_check3)

    def extract_images_test(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
        matches2 = extract_markdown_images(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual([("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")], matches2)
        matches3 = extract_markdown_images(
            "This is just text without images (but has some features out of order [to test])"
        )
        self.assertListEqual([], matches3)
        matches4 = extract_markdown_images(
            "This is a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches4)
        matches5 = extract_markdown_links(
            "![Search](https://www.google.com/search?q=boot.dev&rlz=1C1CHBF_en)"
        )
        self.assertListEqual([("Search", "https://www.google.com/search?q=boot.dev&rlz=1C1CHBF_en")], matches5)
        matches6 = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png"), ("second image", "https://i.imgur.com/3elNhQu.png")], matches6)

    def extract_links_test(self):
        matches = extract_markdown_links(
            "This is a link to [Google](https://www.google.com)"
        )
        self.assertListEqual([("Google", "https://www.google.com")], matches)
        matches2 = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches2)
        matches3 = extract_markdown_links(
            "This is just text without images (but has some features out of order [to test])"
        )
        self.assertListEqual([], matches3)
        matches4 = extract_markdown_images(
            "This is a [link](https://boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("link", "https://boot.dev")], matches4)
        matches5 = extract_markdown_links(
            "[Search](https://www.google.com/search?q=boot.dev&rlz=1C1CHBF_en)"
        )
        self.assertListEqual([("Search", "https://www.google.com/search?q=boot.dev&rlz=1C1CHBF_en")], matches5)
    
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
        node2 = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.CODE,
        )
        new_nodes2 = split_nodes_image([node2])
        self.assertListEqual(
            [TextNode("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)", TextType.CODE,)],
            new_nodes2,
        )
        node3 = TextNode(
            "This is text with an ![](https://i.imgur.com/zjjcJKZ.png) and another ![second image]()",
            TextType.TEXT,
        )
        new_nodes3 = split_nodes_image([node3])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, ""
                ),
            ],
            new_nodes3,
        )
        node4 = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another [link this time](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes4 = split_nodes_image([node4])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another [link this time](https://i.imgur.com/3elNhQu.png)", TextType.TEXT),
            ],
            new_nodes4,
        )
        node5 = TextNode(
            "This is just text without an image as a test",
            TextType.TEXT,
        )
        new_nodes5 = split_nodes_image([node5])
        self.assertListEqual(
            [TextNode("This is just text without an image as a test", TextType.TEXT),],
            new_nodes5
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
        node2 = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.CODE,
        )
        new_nodes2 = split_nodes_link([node2])
        self.assertListEqual(
            [TextNode("This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)", TextType.CODE,)],
            new_nodes2,
        )
        node3 = TextNode(
            "This is text with an ![](https://i.imgur.com/zjjcJKZ.png) and another [second link]()",
            TextType.TEXT,
        )
        new_nodes3 = split_nodes_link([node3])
        self.assertListEqual(
            [
                TextNode("This is text with an ![](https://i.imgur.com/zjjcJKZ.png) and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, ""),
            ],
            new_nodes3,
        )
        node4 = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another [link this time](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes4 = split_nodes_link([node4])
        self.assertListEqual(
            [
                TextNode("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ", TextType.TEXT),
                TextNode("link this time", TextType.LINK, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes4,
        )
        node5 = TextNode(
            "This is just text without a link as a test",
            TextType.TEXT,
        )
        new_nodes5 = split_nodes_image([node5])
        self.assertListEqual(
            [TextNode("This is just text without a link as a test", TextType.TEXT),],
            new_nodes5
        )

    def test_text_to_TextNodes(self):
        node = text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        self.assertListEqual(
            [
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
            ],
            node
        )
        node2 = text_to_textnodes("This is **** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        self.assertListEqual(
            [
                TextNode("This is **** with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            node2
        )
    
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
            md2 = """
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
                    "This is **bolded** paragraph\nThis is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line\n- This is a list\n- with items",
                ],
            )
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
                    "This is another paragraph with _italic_ text and `code` here"
                    "This is the same paragraph on a new line",
                    "- This is a list"
                    "- with items",
                ],
            )

    def test_BlockType(self):
        md = "## This is a heading"
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.HEADING, blocks)
        md = """```
This is a code block
and more code here
and more code below```"""
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.CODE, blocks)
        md = """>quote here
> more quote
> this is long
>end quote"""
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.QUOTE, blocks)
        md = """- list
- list
- list"""
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.UNORDERED_LIST, blocks)
        md = """1. ordered
2. ordered
3. ordered"""
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.ORDERED_LIST, blocks)
        md = """1. ordered
2. ordered
5. ordered"""
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.PARAGRAPH, blocks)
        md = """- list
- list
-list"""
        blocks = block_to_block_type(md)
        self.assertEqual(BlockType.PARAGRAPH, blocks)

    def test_extract_title(self):
        md = "# this is a test "
        title = extract_title(md)
        self.assertEqual("this is a test", title)
        md = """#    some other thing there    
 this is a test     
more after
"""
        title = extract_title(md)
        self.assertEqual("some other thing there", title)
        md = """    some other thing there    
 this is a test     
# more after
"""
        title = extract_title(md)
        self.assertEqual("more after", title)

if __name__ == "__main__":
    unittest.main()
