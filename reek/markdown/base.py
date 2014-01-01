from collections import OrderedDict

from .utils import RootNode, Text
from . import parsers, preprocessors, serialisers


class Document:
    def __init__(self):
        self.preprocessors = OrderedDict((
            ('detab', preprocessors.DetabPreprocessor(), ),
        ))
        self.parsers = OrderedDict((
            ('header_setext', parsers.SetextHeaderParser(),),
            ('header_atx', parsers.AtxHeaderParser(),),
            ('blockquote', parsers.BlockquoteParser(),),
            ('codeblock', parsers.CodeBlockParser(),),
            ('unordered_list', parsers.UnorderedListParser(),),
            ('paragraph', parsers.ParagraphParser(),),
        ))
        self.tree_walkers = OrderedDict()

    def convert_string(self, text, serialiser=serialisers.HTML5Serialiser):
        text = self.preprocess(text)
        root = self.generate_tree(text)
        root = self.walk_tree(root)

        return serialiser().serialise(root)

    def preprocess(self, text):
        for processor in self.preprocessors.values():
            text = processor.process(self, text)
        return text

    def generate_tree(self, text):
        return RootNode(self.parse_text(text))

    def parse_text(self, text):
        """
        Parses a full block of text

        Divides the text up in blocks separated by empty lines.
        Resulting blocks keep one blank line attached and get parsed
        """
        return self.parse_blocks(block + "\n\n" for block in text.strip().split('\n\n'))

    def parse_blocks(self, blocks):
        """
        Parse an iterable of blocks
        """
        return (self.parse_block(block) for block in blocks)

    def parse_block(self, block):
        processor = next(filter(lambda l: l.accepts(block), self.parsers.values()), None)
        if processor:
            yield processor.process(self, block)
        else:
            yield Text(block)

    def walk_tree(self, root):
        for walker in self.tree_walkers.values():
            root = walker.walk(self, root)
        return root

