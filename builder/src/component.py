import frontmatter
from log import Logger

class Component:
    def __init__(self, contents: str, log: Logger):
        self.contents = contents
        self.body, self.metadata = frontmatter.parse(self.contents)
        log.print(f'Read frontmatter: \n{self.metadata}\n---\n{self.body}')

    def getBody(self):
        return self.body

    def getMetadata(self):
        return self.metadata
