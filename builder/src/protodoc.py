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

        if "docver" in data:
            self.version: str = data["docver"]
        else:
            log.error("Could not find field 'docver' in protodoc.")
            

        if "lang" in data:
            self.lang: str = data["lang"]
            #lang is str | None val, so no break

        if "themes" in data:
            self.themes: list = data["themes"]
        else:
            log.error("Could not find field 'themes' in protodoc.")

        if "outputDir" in data:
            self.outputDir: str = data["outputDir"]
            if self.outputDir[-1] is not '/': #postappend path trailing directory mark
                self.outputDir += '/'
        else:
            self.outputDIr = "."

        if "layers" in data:
            self.layers: list[dict] = data["layers"]
        else:
            log.error("Could not find field 'layers' in protodoc.")

        if "defaultTitles" in data:
            self.defaultTitles: bool = data["defaultTitles"]
        else:
            self.defaultTitles = False

        if "sectionTitles" in data:
            self.sectionTitles: dict[str, str] = data["sectionTitles"]

        if "headers" in data:
            self.headers: dict = data["headers"]
        
        log.print('Parsed protodoc.')
        log.debugprint(self.getVersion())
        log.debugprint(self.getLang())
        log.debugprint(self.getThemes())
        log.debugprint(self.getLayers())

    def tostring(self):
        print(self.contents)

    def getVersion(self):
        return self.version
    
    def getLang(self):
        if hasattr(self, "lang"):
            return self.lang
        else:
            self.log.debugprint("Lang not set in protodoc. Function getLang() returns None.")
            return None

    def getThemes(self):
        return self.themes

    def getLayers(self):
        return self.layers

    def getOutputDir(self):
        return self.getOutputDir

    def getSectionTitles(self):
        if hasattr(self, "sectionTitles"):
            return self.sectionTitles
        else:
            self.log.debugprint("No section titles defined.")
            return None

    def getSectionTitle(self, section: str):
        pretitles = { #default titles
            "overview": "Brand & Style",
            "colors": "Colors",
            "typography": "Typography",
            "layout": "Layout & Spacing",
            "elevation": "Elevation & Depth",
            "shapes": "Shapes",
            "components": "Components",
        }

        if hasattr(self, "sectionTitles"):
            return self.sectionTitles[section]
        else:
            if self.defaultTitles:
                if section in pretitles.keys():
                    return pretitles[section]
                else:
                    self.log.print(f'Section {section} has no title defined \nsuggestion: write \n---\nsectionTitles:\n\t{section}:"Title for this section"\n---\nin protodoc file.')
            else:
                self.log.print(f'Section {section} has no title defined \nsuggestion: write \n---\nsectionTitles:\n\t{section}:"Title for this section"\n---\nin protodoc file, or enable procdoc field `defaultTitles: True`')
        return None

    def getHeaders(self):
        if hasattr(self, "headers"):
            return self.headers
        else:
            return {}
