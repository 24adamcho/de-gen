import argparse
import re
from log import Logger
from log import LogLevel
from log import DebugLevel
from protodoc import Protodoc
from themerefs import ThemeRef
from assembler import assemble

log = Logger()

def initProtodoc():
    with open("test/protodoc.yaml", "r") as file:
        content = file.read()
        log.print(f'Read protodoc: {content}')
        return Protodoc(content, log)

def flatten(v: object, path: str, rules: list[dict[str, object]]):
    if isinstance(v, dict):
        d: dict = v
        nextrules = []
        for dk, dv in d.items():
            log.debugprint(f'dk: {dk}, dv:{dv}', DebugLevel.MORE)
            nextrules.extend(flatten(dv, f'{path}/{dk}', []))
        for rule in nextrules:
            rules.append(rule)
    else:
        log.debugprint('direct value transcribed', DebugLevel.MORE)
        rules.append({path: v})
    log.debugprint(f'rules contains: {rules}', DebugLevel.MORE)
    return rules

def main():
    log.setLogLevel(LogLevel.INFO)
    log.setDebugLevel(DebugLevel.SOME)
    log.print("Start", LogLevel.INFO)
    protodoc = initProtodoc()

    themerefs = []
    for theme in protodoc.getThemes():
        log.debugprint(f'Reading for {theme}')
        ref = ThemeRef(f'test/themes/{theme}', theme, log)
        themerefs.append(ref)

    for ref in themerefs:
        parts = ref.getThemeParts()
        for k, v in parts.items():
            log.debugprint(f'k:{k}')

    
    layers = protodoc.getLayers()
    rules = flatten(layers, 'test/themes', []) #wacky hack to match the flattened keys to the file paths in themerefs
    for k in rules:
        log.debugprint(f'k:{k}')

    ruleregex = []
    for e in rules:
        k = next(iter(e))

        #remove the final part of the key string, since it's a key object in the yaml dict
        split = k.rpartition('/') #splits string from last slash into a three-element list (before, '/', after)
        path = split[0] #string head before slash, append to regex
        rule = split[-1] #string tail after slash
        log.debugprint(split)

        #regex match against theme refs
        regex = re.compile(f'^{re.escape(path)}*')
        log.debugprint(path)

        ruleregex.append((regex, rule, e[k]))


    #    #iterate over theme refs and match
    #    for theme in themerefs:
    #        for ref in theme.getThemeParts().keys():
    #            log.debugprint(f'attempting {ref} to {regex}')
    #            match = regex.match(ref)
    #            if match is not None:
    #                log.debugprint(f'matched ref {ref}')
    #                userefs.append(ref)

    refs= {}
    for theme in themerefs:
        for ref in theme.getThemeParts().keys():
            for regex, rule, value in ruleregex:
                if regex.match(ref) is not None:
                    log.debugprint(f'matched {ref} to {rule}:{value}')
                    component = theme.getThemeParts()[ref]
                    alreadyDefined = component.getName() in refs.keys()

                    #`use` replaces previous reference
                    if rule == "use":
                        if value == True:
                            if alreadyDefined:
                                if refs[component.getName()].isUnique():
                                    log.error(f'Cannot apply rule for {component.getName()}: Previously defined as `unique`.')
                                log.debugprint(f'{component.getName()} overloaded.')
                                refs[component.getName()] = component
                            else:
                                log.debugprint(f'Ref added: {component.getName()}', DebugLevel.SOME)
                                refs[component.getName()] = component
                        elif value == False:
                            if refs[component.getName()] == component:
                                refs.pop(component.getName())
                    elif rule == "unique":
                        log.debugprint(f'{component.getName()} set unique.')
                        if alreadyDefined:
                            refs[component.getName()].markUnique() #mark the reference, not the original
                        else:
                            log.error(f'Cannot mark undefined component unique: {component.getName()}. Did you set `use: True`?')
                    elif rule == "reroute":
                        sfrom, sto = value.split(':')
                        log.debugprint(f'Rerouting {sfrom} to {sto}')
                        component.changerefs(sfrom, sto) #modify the original prototype object rather than the export data source, so order of operations is not a factor
                    elif rule == "name":
                        log.debugprint(f'{component.getName()} renamed to {value}')
                        if alreadyDefined:
                            component.rename(value)
                        else:
                            log.error(f'Cannot rename undefined component: {component.getName()}')
                    elif rule == "section":
                        log.debugprint(f'{component.getName()} should be put in {value} section')
                        component.setSection(value)

                        ## some sections modify component names
                        sectionobj = protodoc.getSectionObject(value)
                        if sectionobj is not None:
                            referenceFormat = protodoc.getSectionField(value, "referenceFormat")
                            if referenceFormat == "file":
                                component.rename(f'{component.getFile()}')
                            elif referenceFormat == "parent-file":
                                component.rename(f'{component.getParent()}-{component.getFile()}')
                            else: #i have no clue
                                component.rename(f'{component.getParent()}-{component.getFile()}')
                        else: #undefined
                            component.rename(f'{component.getParent()}-{component.getFile()}')
                    elif alreadyDefined:
                        log.debugprint(f'rule should modify {refs[component.getName()]}')
                        refs[component.getName()].modify(rule, value)
                    else:
                        log.print(f'Rule declared without `use` or previous component to overload.', LogLevel.WARNING)

                    if refs.get(component.getName()) is not None:
                        log.debugprint(refs[component.getName()].getMetadata())
    log.debugprint("userefs:")
    for key, ref in refs.items():
        log.debugprint(f'{key}: {ref.getMetadata()}')

    assemble(log, refs, protodoc)

if __name__ == "__main__":
    main()
