from component import Component
from log import Logger
from protodoc import Protodoc
import yaml

def assemble(log: Logger, refs: dict[str, Component], protodoc: Protodoc):
            
    metadata = {}
    body: dict[str, list[str]] = {}
    sectionobjs = []
    sectionseen= []

    #map sections to dict for orderless ingestion
    for c in refs.values():
        section = "undefined"
        if c.getSection() is not None:
            section: str = str(c.getSection())
        # otherwise section remains the dump bucket 'undefined'

        log.debugprint(f'Section object: {yaml.dump(protodoc.getSectionObject(section))}')

        if protodoc.getSectionField(section, "use") == False: #if disabled, just skip it entirely
            continue

        if section not in sectionseen: #init section vars if new section
            sectionseen.append(section)
            sectionobjs.append(protodoc.getSectionObject(section))
            sectionobjs[-1]['__nameref__'] = section
            metadata[section] = {}
            body[section] = []

        if protodoc.getSectionField(section, "useBody") == False:
            pass
        else:
            body[section].append(c.getBody())

        log.debugprint(protodoc.getSectionObject(section))
        log.debugprint(protodoc.getSectionField(section, "useMetadata"))
        if protodoc.getSectionField(section, "useMetadata") is not None:

            metadataFlag = protodoc.getSectionField(section, "useMetadata")
            if metadataFlag == "True":
                metadata.update(c.getMetadata())
            elif metadataFlag == "Layered":
                metadata[section].update(c.getMetadata())
            elif metadataFlag == "Child":
                metadata[section][c.getName()] = c.getMetadata()
            elif metadataFlag == "False":
                pass
            else:
                log.error(f'Unknown useMetadata flag: {metadataFlag}')

    log.debugprint(yaml.dump(metadata))

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

    orderedsections = sorted(sectionobjs, key=lambda d: d['order'])

    endmeta = metadata #aggregate metadata block
    endbody: list[str] = [] #aggregate body block

    for sectionobj in orderedsections:
        section = sectionobj['__nameref__']

        if protodoc.getSectionField(section, "useBody") == False:
            pass
        else:
            if protodoc.getSectionField(section, "title") is not None:
                endbody.append(str(protodoc.getSectionField(section, "title")))

        if protodoc.getSectionField(section, "prelude") is not None:
            preludefile = str(protodoc.getSectionField(section, "prelude"))
            with open(preludefile) as f:
                filename = preludefile.rpartition('/')[-1].rpartition('.')[0]
                preluderef = Component(f.read(), log, "", "", filename) 

                if protodoc.getSectionField(section, "useBody") == False:
                    pass
                else:
                    endbody.append(preluderef.getBody()) #append prelude body

                if protodoc.getSectionField(section, "usePreludeMetadata") == True:

                    metadataFlag = protodoc.getSectionField(section, "usePreludeMetadata")
                    if metadataFlag == "True":
                        endmeta.update(preluderef.getMetadata())
                    elif metadataFlag == "Layered":
                        endmeta.update({f'{section}': preluderef.getMetadata()})
                    elif metadataFlag == "Child":
                        endmeta.update({f'{preluderef.getName()}': preluderef.getMetadata()})
                    elif metadataFlag == "False":
                        pass
                    else:
                        log.error(f'Unknown usePreludeMetadata flag: {metadataFlag}')

        if protodoc.getSectionField(section, "useBody") == False:
            pass
        else:
            if protodoc.getSectionField(section, "memberPrefix") is not None:
                body[section].insert(0, str(protodoc.getSectionField(section, "memberPrefix")))
            if protodoc.getSectionField(section, "memberPostfix") is not None:
                body[section].insert(0, str(protodoc.getSectionField(section, "memberPostfix")))

            if body[section] is not None:
                if protodoc.getSectionField(section, "memberSplit") is not None:
                    endbody.append(str(protodoc.getSectionField(section, "memberSplit")).join(body[section]))
                else:
                    endbody.append('\n\n'.join(body[section]))

    #final concatenation
    finalmeta = {k:v for k,v in endmeta.items() if v} #squash to remove empty values
    finalbody = ""
    if protodoc.getTitle() is not None:
        finalbody += str(protodoc.getTitle())
    finalbody = '\n'.join(endbody)
    log.debugprint(endmeta)
    log.debugprint(endbody)
    
    finalmeta.update(protodoc.getHeaders()) #hoist headers. the output gets scrambled but it's yaml anyway so order doesn't matter. probably.

    merged = '---\n' + yaml.dump(finalmeta) + '---\n\n' + finalbody

    log.print('Output:' + merged)

    return merged
