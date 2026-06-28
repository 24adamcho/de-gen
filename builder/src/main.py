import argparse
import re
from log import Logger
from log import LogLevel
from log import DebugLevel
from protodoc import Protodoc
from themerefs import ThemeRef

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

    #rule `use`
    refs= {}
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
    for theme in themerefs:
        for ref in theme.getThemeParts().keys():
            for regex, rule, value in ruleregex:
                if regex.match(ref) is not None:
                    log.debugprint(f'matched {ref} to {rule}:{value}')
                    component = theme.getThemeParts()[ref]

                    #`use` replaces previous reference
                    if rule == "use":
                        if value == True:
                            log.debugprint(f'Ref added: {component.getName()}', DebugLevel.SOME)
                            refs[component.getName()] = component
                        elif value == False:
                            if refs[component.getName()] == component:
                                refs.pop(component.getName())
                    else:
                        if hasattr(refs, component.getName()) is not None:
                            log.debugprint(f'rule should modify {refs[component.getName()]}')
                            refs[component.getName()].modify(rule, value)
                        else:
                            log.print(f'Rule declared without `use` or previous component to overload.', LogLevel.WARNING)

    log.debugprint("userefs:")
    for key, ref in refs.items():
        log.debugprint(f'{key}: {ref.getMetadata()}')

if __name__ == "__main__":
    main()
