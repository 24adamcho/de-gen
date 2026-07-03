import argparse
import re
from pathlib import Path, PurePath
from log import Logger
from log import LogLevel
from log import DebugLevel
from protodoc import Protodoc
from themerefs import ThemeRef
from assembler import assemble

log = Logger()

##thanks gpt
def parse_args():
    parser = argparse.ArgumentParser(
        prog="",
        description=""
    )

    # Positional argument
    parser.add_argument(
        "file",
        help="Input file"
    )

    # Log level
    parser.add_argument(
        "--loglevel",
        type=lambda s: LogLevel[s.upper()],
        choices=list(LogLevel),
        default=LogLevel.INFO,
        metavar="{QUIET,FATAL,WARNING,INFO}",
        help="Logging level"
    )

    # Debug level
    parser.add_argument(
        "--debuglevel",
        type=lambda s: DebugLevel[s.upper()],
        choices=list(DebugLevel),
        default=DebugLevel.NONE,
        metavar="{NONE,SOME,MORE,ALL}",
        help="Debug level"
    )

    return parser.parse_args()

def initProtodoc(f: str):
    filepath = Path(f)
    if filepath.is_dir():
        fcheck = filepath / "protodoc.yaml"
        if fcheck.is_file() == False:
            fcheck = filepath / "protodoc.yml"
        if fcheck.is_file() == False:
            log.error("Couldn't find protodoc.yaml.")
        filepath = fcheck
    print(filepath)

    with filepath.open("r") as file:
        content = file.read()
        log.print(f'Read protodoc: {content}')
        return Protodoc(str(filepath), content, log)

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

def write(protodoc: Protodoc, md: str):
    dir = "."
    if protodoc.getOutputDir() is not None:
        dir = str(protodoc.getOutputDir())
    else:
        dir = str(protodoc.getDir())

    outpath = Path(dir)
    if outpath.is_dir():
        outpath = outpath / "Design.md" #default file name
    
    with outpath.open("w") as f:
        f.write(md)
        log.print(f'Wrote output to {outpath}.')

def main():
    args = parse_args()
    log.setLogLevel(args.loglevel)
    log.setDebugLevel(args.debuglevel)
    log.print("Start", LogLevel.INFO)
    protodoc = initProtodoc(args.file)

    themerefs = []
    for theme in protodoc.getThemes():
        log.debugprint(f'Reading for {theme}')
        ref = ThemeRef(theme, theme, log)
        themerefs.append(ref)

    for ref in themerefs:
        parts = ref.getThemeParts()
        for k, v in parts.items():
            log.debugprint(f'k:{k}', DebugLevel.MORE)

    
    layers = protodoc.getLayers()
    log.debugprint(f'Layers: {layers}')
    rules = []
    for theme in themerefs:
        rules.extend(flatten(layers, str(Path(theme.getPath()).parent), [])) #wacky hack to match the flattened keys to the file paths in themerefs
        #TODO: This is dumb and leads to a lot of pain down there if it changes even slightly. Too unsable. Must change component name resolution and rule application sequence for full fix.

    for k in rules:
        log.debugprint(f'rule k:{k}')

    ruleregex = []
    for e in rules:
        k = next(iter(e))

        #remove the final part of the key string, since it's a key object in the yaml dict
        split = k.rpartition('/') #splits string from last slash into a three-element list (before, '/', after)
        path = split[0] #string head before slash, append to regex
        rule = split[-1] #string tail after slash
        log.debugprint(split)

        #regex match against theme refs
        regex = re.compile(f'^{re.escape(str(Path(path).relative_to(".")))}*')
        log.debugprint(path)

        ruleregex.append((regex, rule, e[k]))


    #we go ass backwards, going through each component and computing rules that apply to it.
    refs= {}
    for theme in themerefs:
        for ref in theme.getThemeParts().keys():
            for regex, rule, value in ruleregex:
                log.debugprint(f'attempt match {ref} to {regex}')
                if regex.match(str(Path(ref).relative_to("."))) is not None:
                    log.debugprint(f'matched {ref} to {rule}:{value}')
                    component = theme.getThemeParts()[ref]
                    alreadyDefined = component.getName() in refs.keys()

                    #`use` replaces previous reference
                    if rule == "use":
                        if value == True:
                            if alreadyDefined:
                                if refs[component.getName()] != component:
                                    if refs[component.getName()].isUnique():
                                        log.error(f'Cannot apply rule for {component.getName()}: Previously defined as `unique`.')
                                    log.debugprint(f'{component.getName()} overloaded.')
                                    refs[component.getName()] = component
                            else:
                                log.debugprint(f'Ref added: {component.getName()}', DebugLevel.SOME)
                                refs[component.getName()] = component
                        elif value == False:
                            if alreadyDefined:
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
                                log.debugprint(f'Default format for {component} set to {component.getParent()}-{component.getFile()}')
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

    log.print("Assembling design...")
    md = assemble(log, refs, protodoc)
    write(protodoc, md)

if __name__ == "__main__":
    main()
