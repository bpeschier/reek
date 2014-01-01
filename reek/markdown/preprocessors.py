class Preprocessor:
    def process(self, document, lines):
        raise NotImplementedError


class DetabPreprocessor(Preprocessor):
    def process(self, document, lines):
        return lines.replace('\t', ' ' * 4)