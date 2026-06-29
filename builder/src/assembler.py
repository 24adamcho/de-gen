from component import Component
from log import Logger
from protodoc import Protodoc
import yaml

def assemble(log: Logger, refs: dict[str, Component], protodoc: Protodoc):
            
    metadata = {}
    body: dict[str, list[str]] = {}
    sections = []

    #map sections to dict for orderless ingestion
    for c in refs.values():
        section = "undefined"
        if c.getSection() is not None:
            section: str = str(c.getSection())
        # otherwise section remains the dump bucket 'undefined'

        if section not in sections: #init section vars if new
            sections.append(section)
            metadata[section] = {}
            body[section] = []

        if section == "overview": #overview cannot contain metadata
            body["overview"].append(c.getBody())

        elif section == "colors": #colors include and overwrite their metadata
            metadata["colors"].update(c.getMetadata())
            body["colors"].append(c.getBody())

        elif section == "components": #components include themselves but do not interfere with other components
            metadata["components"][c.getName()] = c.getMetadata()
            body["components"].append(c.getBody())

        elif section == "typography":
            metadata["typography"][c.getName()] = c.getMetadata()
            body["typography"].append(c.getBody())

        elif section == "footer": #footer cannot contain metadata
            body["footer"].append(c.getBody())

        else: #misc section, either we don't know it or it's undefined
            metadata[section].update(c.getMetadata())
            body[section].append(c.getBody())

    #log.debugprint(yaml.dump(metadata))

    ## ordered output
    # design.md structure:
    #
    #   Overview
    #   Colors
    #   Typography
    #   Layout
    #   Elevation
    #   Shapes
    #   Components
    #   Do's and Don'ts (footer)

    endmeta = [] #aggregate metadata block
    endbody: list[str] = [] #aggregate body block
    endtitles: list[str | None] = []

    if "overview" in sections:
        endbody.append('\n\n'.join(body["overview"]))
        endtitles.append(protodoc.getSectionTitle("overview"))
        sections.remove("overview")
    if "colors" in sections:
        endmeta.append(metadata["colors"])
        endbody.append('\n\n'.join(body["colors"]))
        endtitles.append(protodoc.getSectionTitle("colors"))
        sections.remove("colors")
    if "typography" in sections:
        endmeta.append(metadata["typography"])
        endbody.append('\n\n'.join(body["typography"]))
        endtitles.append(protodoc.getSectionTitle("typography"))
        sections.remove("typography")
    if "layout" in sections:
        endmeta.append(metadata["layout"])
        endbody.append('\n\n'.join(body["layout"]))
        endtitles.append(protodoc.getSectionTitle("layout"))
        sections.remove("layout")
    if "elevation" in sections:
        endmeta.append(metadata["elevation"])
        endbody.append('\n\n'.join(body["elevation"]))
        endtitles.append(protodoc.getSectionTitle("elevation"))
        sections.remove("elevation")
    if "shapes" in sections:
        endmeta.append(metadata["shapes"])
        endbody.append('\n\n'.join(body["shapes"]))
        endtitles.append(protodoc.getSectionTitle("shapes"))
        sections.remove("shapes")
    if "components" in sections:
        endmeta.append(metadata["components"])
        endbody.append('\n\n'.join(body["components"]))
        endtitles.append(protodoc.getSectionTitle("components"))
        sections.remove("components")
    if "footer" in sections:
        endmeta.append(metadata["footer"])
        endbody.append('\n\n'.join(body["footer"]))
        endtitles.append(protodoc.getSectionTitle("footer"))
        sections.remove("footer")

    #loop over remaining unknown sections
    for section in sections:
        endmeta.append(metadata[section])
        endbody.append('\n\n'.join(body[section]))
        endtitles.append(protodoc.getSectionTitle(section))

    #final concatenation
    finalmeta = {}
    finalbody = ""
    
    for index in range(len(endmeta)):
        finalmeta.update(endmeta[index])
        if endtitles[index] is not None:
            finalbody += "## " + str(endtitles[index]) + '\n\n'
        finalbody += endbody[index] + '\n'

    finalmeta.update(protodoc.getHeaders()) #hoist headers. the output gets scrambled but it's yaml anyway so order doesn't matter. probably.

    merged = '---\n' + yaml.dump(finalmeta) + '---\n' + finalbody

    log.print(merged)

    return merged
