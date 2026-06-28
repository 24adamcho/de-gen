import frontmatter
from log import Logger

class Component:
    def __init__(self, contents: str, log: Logger, name: str):
        self.contents = contents
        self.metadata, self.body= frontmatter.parse(self.contents)
        self.name = name
        log.print(f'Read frontmatter: \n{self.metadata}\n---\n{self.body}')

    def getBody(self):
        return self.body

    def getMetadata(self):
        return self.metadata

    def getName(self):
        return self.name

    def modify(self, key, value):
        self.metadata[key] = value
