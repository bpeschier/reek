from .utils import TagNode, Text


class Parser:
    def accepts(self, block):
        raise NotImplementedError

    def process(self, document, block):
        raise NotImplementedError


class BlockParser(Parser):
    def accepts(self, block):
        return block.endswith('\n\n') and self.accepts_block(self.clean_block(block))

    def accepts_block(self, block):
        raise NotImplementedError

    def process(self, document, block):
        return self.process_block(document, self.clean_block(block))

    def process_block(self, document, clean_block):
        raise NotImplementedError

    @staticmethod
    def unindent(block):
        return '\n'.join(
            line[4:] for line in block.split('\n')
        )

    @staticmethod
    def strip_prefix(block, prefix):
        return '\n'.join(
            line[len(prefix):] if line.startswith(prefix.strip()) else line for line in block.split('\n')
        )

    def is_indented_block(self, block):
        """
        Check if all lines are indented with at least four spaces
        Empty lines are ignored
        """
        return self.check_lines(
            lambda line: line.startswith(' ' * 4),
            block
        )

    def is_prefixed_block(self, block, prefix):
        """
        Check if all lines start with prefix or space + prefix
        """
        return self.check_lines(
            lambda line: line.startswith(prefix) or line.startswith(' ' + prefix),
            block
        )

    @staticmethod
    def check_lines(check, block):
        return all(map(
            check,
            (line for line in block.split('\n') if line.strip(' '))
        ))

    @staticmethod
    def clean_block(block):
        return block.rstrip('\n')


class ParagraphParser(BlockParser):
    def accepts_block(self, block):
        return True

    def process_block(self, document, clean_block):
        return TagNode('p', document.parse_block(clean_block))


class BlockquoteParser(BlockParser):
    def accepts_block(self, block):
        return block.startswith('> ')

    def process(self, document, block):
        inside_block = self.strip_prefix(block, '> ')
        return TagNode('blockquote', document.parse_text(inside_block))


class CodeBlockParser(BlockParser):
    def accepts_block(self, block):
        return self.is_indented_block(block)

    def process_block(self, document, clean_block):
        inside_block = self.unindent(clean_block)
        return TagNode('pre', [Text(inside_block)])


class SetextHeaderParser(BlockParser):
    def accepts_block(self, block):
        lines = block.split('\n')
        last_line = lines[-1]
        return len(lines) > 1 and last_line[0] in '-=' and all(l == last_line[0] for l in last_line)

    def process_block(self, document, clean_block):
        lines = clean_block.split('\n')
        last_line = lines[-1]
        level_tag = 'h1' if last_line[0] == '=' else 'h2'
        title = '\n'.join(lines[:-1])
        return TagNode(level_tag, document.parse_block(title))


class AtxHeaderParser(BlockParser):
    def accepts_block(self, block):
        return len(block.split('\n')) == 1 and self.is_prefixed_block(block, '#')

    def process_block(self, document, clean_block):
        hashes = len(clean_block.split(' ')[0])
        level_tag = 'h{count}'.format(count=hashes)
        inside_block = clean_block[hashes:].lstrip(' ').rstrip('# ')
        return TagNode(level_tag, document.parse_block(inside_block))


class UnorderedListParser(BlockParser):
    def accepts_block(self, block):
        return block[0] in '*-+'

    def process(self, document, block):
        item_prefix = block[0] + ' '
        return TagNode('ul', (TagNode('li', document.parse_block(inside.strip())) for inside in
                              self.strip_prefix(self.clean_block(block), item_prefix).split('\n')))
