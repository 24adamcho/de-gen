from component import Component
from log import Logger
import frontmatter
import yaml

def assemble(log: Logger, path: str, refs: dict[str, Component]):
    if path[-1] is not '/': #postappend path trailing directory mark
        path += '/'
            
    metadata = {}
    body = ""

    for key, component in refs.items():
        metadata[key] = component.getMetadata()
        body += component.getBody()
        body += '\n'

    metadatayaml = yaml.dump(metadata)

    log.print(f'---\n{metadatayaml}\n---\n{body}')
