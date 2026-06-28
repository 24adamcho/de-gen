import yaml
from log import Logger

class Protodoc:
    def __init__(self, contents: str, log: Logger):
        self.contents = contents
        self.log = log

        #parse yaml
        log.print("Loading protodoc...")
        data: dict = yaml.safe_load(self.contents)
        log.print("Loaded.")

        if "version" in data:
            self.version: str = data["version"];
        else:
            log.error("Could not find field 'version' in protodoc.")
            

        if "lang" in data:
            self.lang: str = data["lang"];
        else:
            log.print("Could not find field 'lang' in protodoc.")
            #lang is str | None val, so no break

        if "themes" in data:
            self.themes: list = data["themes"];
        else:
            log.error("Could not find field 'themes' in protodoc.")

        if "layers" in data:
            self.layers: list[dict] = data["layers"];
        else:
            log.error("Could not find field 'layers' in protodoc.")
        
        log.print('Parsed protodoc:')
        log.print(self.getVersion())
        log.print(self.getLang())
        log.print(self.getThemes())
        log.print(self.getLayers())

    def tostring(self):
        print(self.contents)

    def getVersion(self):
        return self.version
    
    def getLang(self):
        if hasattr(self, "lang"):
            return self.lang
        else:
            self.log.print("Lang not set in protodoc. Function getLang() returns None.")
            return None

    def getThemes(self):
        return self.themes

    def getLayers(self):
        return self.layers
