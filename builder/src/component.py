import frontmatter
from log import Logger

class Component:
    def __init__(self, contents: str, log: Logger, name: str):
        self.log = log
        self.contents = contents
        self.metadata, self.body= frontmatter.parse(self.contents)
        self.name = name
        self.unique = False
        log.print(f'Read frontmatter: \n{self.metadata}\n---\n{self.body}')

    def getBody(self):
        return self.body

    def getMetadata(self):
        return self.metadata

    def getName(self):
        return self.name

    def modify(self, key, value):
        self.metadata[key] = value

    def markUnique(self):
        self.unique = True

    def isUnique(self):
        return self.unique

    def rename(self, s):
        self.name = s

    def changerefs(self, sfrom: str, sto: str):
        for k, v in self.metadata.items():
            if v == sfrom:
                self.log.debugprint(f'Set {self.metadata}[{k}] to {sto}')
                self.metadata[k] = sto
        self.log.debugprint(self.metadata)
