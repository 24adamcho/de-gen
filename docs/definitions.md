- # Design.md
A specification for creating ai-readable style guides for application design. (see https://github.com/google-labs-code/design.md) The format uses markdown files comprised of a YAML header, followed by human-readable descriptions.
- # Component
An object that describes the feature or look of a part of a design. Components can be nested or extended.
- # Style
A segment of css or human-readable text that describes the look of a component.

# Specific to this project
- # Theme
A set of markdown documents describing a unified set of components and styles.
- # Protodoc
A file that describes what themes and/or components should be used to generate a design.md document.
- # Clobbering
Some themes may redefine common elements, such as buttons or paragraph bodies. Clobbering is a technique that allows for multiple definitions to be present, but only one used at runtime. For example, two functions named 'sum' may be differentiated by 'sum-int-int' and 'sum-float-float'. Another form of clobbering would be overriding, where the last stated definition is the one that is used.
- # Layers
Layers are a series of components that are taken from one theme and applied over another. Layer components can be conflicting, where conflict resolution is applied at the protodoc level.
