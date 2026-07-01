import os
from log import Logger
from component import Component

class ThemeRef:
    def __init__(self, path: str, name: str, log: Logger):
        self.themeparts: dict[str, Component]= {}
        self.name = name
        for root, dir, files in os.walk(path):
            for file in files:
                log.debugprint(f'File root: {root}, dir: {dir}, file: {file}')
                with open(f'{root}/{file}', "r") as f:
                    parent = root.rpartition('/')[-1]
                    filenoext = file.rpartition('.')[0]
                    qualifiedname = f'{parent}-{filenoext}'
                    log.debugprint(qualifiedname)
                    self.themeparts[f'{root}/{file}'] = Component(f.read(), log, qualifiedname, parent, filenoext) #wacky hack to match the theme keyes to the flattened rules
                log.print(f'Read {root}/{file}')
        pass

    def getThemeParts(self):
        return self.themeparts
