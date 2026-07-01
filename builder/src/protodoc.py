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

        self.sections: dict[str, dict] = {}

        if "defaultTitles" in data:
            self.defaultTitles: bool = data["defaultTitles"]

            pretitles = { #default titles
                "overview": {
                    "title": "Brand & Style",
                    "order": 0,
                    "useMetadata": "False",
                },
                "colors": {
                    "title": "Colors",
                    "order": 1,
                    "useMetadata": "Layered",
                },
                "typography": {
                    "title": "Typography",
                    "order": 2,
                    "referenceFormat": "file",
                    "useMetadata": "Child",
                },
                "layout": {
                    "title": "Layout & Spacing",
                    "order": 3,
                },
                "elevation": {
                    "title": "Elevation & Depth",
                    "order": 4,
                },
                "shapes": {
                    "title": "Shapes",
                    "order": 5,
                    "useMetadata": "Layered",
                },
                "components": {
                    "title": "Components",
                    "order": 6,
                    "useMetadata": "Child",
                },
                "footer": {
                    "order": 7,
                    "useMetadata": "False",
                }
            }
            if self.defaultTitles is True:
                self.sections.update(pretitles)
        else:
            self.defaultTitles = False

        if "sections" in data:
            self.sections.update(data["sections"])
        log.debugprint(f'Sections: \n{self.sections}')

        if "headers" in data:
            self.headers: dict = data["headers"]

        if "title" in data:
            self.title:str = data["title"]
        
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

    def getSectionField(self, section: str, field: str, failOk: bool = True):
        if section in self.sections.keys():
            if self.sections[section].get(field) is not None:
                self.log.debugprint(f'Section {section} field {field} was value {self.sections[section][field]}')
                return self.sections[section][field]
            else:
                self.log.debugprint(f'Couldn\'t find field {field} in {section}.')
        if failOk == False:
            self.log.error(f'Section {section}\'s field {field} is undefined \nsuggestion: write \n---\nsections:\n\t{section}:{"{"}\n\t\ttitle:"Title for this section"{"}"}\n---\nin protodoc file, or enable procdoc field `defaultTitles: True`')
        return None

    def getSectionObject(self, section: str) -> dict | None:
        if section in self.sections.keys():
            return self.sections[section]
        self.log.print(f'Section {section} is undefined \nsuggestion: write \n---\nsections:\n\t{section}:{"{"}\n\t\ttitle:"Title for this section"{"}"}\n---\nin protodoc file, or enable procdoc field `defaultTitles: True`')
        return None

    def getHeaders(self):
        if hasattr(self, "headers"):
            return self.headers
        else:
            return {}

    def getTitle(self):
        if hasattr(self, "title"):
            return self.title
