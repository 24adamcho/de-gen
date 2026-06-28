# Protodoc specification
The protodoc is a file that describes what themes and/or components should be used to generate a design.md document. It should be a series of module and component references that coalesces into the finished output.

The protodoc uses YAML.

## Base fields:
A question mark means that a field is optional.

Name | Type | Example | Description
------------------
`version` | String | `version:"1.0"` | Protodoc specification version
`lang`? | String | `lang:"en-us"` | Language setting for design.md output.
`themes` | String array | `themes: ["example/theme"]` | List of folder locations for theme imports.
`layers` | Multi-field tree | see section on layers | Structure describing what components are taken from themes.

## Layer fields:
Layer fields should mirror the file structure of the components inside the theme they are borrowing from. Travelling down, each component can be either used as-is or traversed further for fine-grain control.
Layers only apply when the component is referenced. Layers are applied in the order they are described, where the last definition used overrides the previous.

In this example, `example/theme` is used as a 'base theme', where `another/theme` then overrides certain elements.
```
themes
|-example
|   |-theme
|       |-...
|-another
    |-theme
        |-buttons
        |   |-primary.md
        |   |-...
        |-paragraphs
        |   |-...
        |-...
```

```yaml
version: "1.0",
themes: ["example/theme", "another/theme"]
layers:
    example:
        theme:
            use: True
    another:
        theme:
            colors:
                primary:
                    reroute: "{colors.black}"
            components:
                buttons:
                    primary:
                        name: "button-primary"
                        backgroundColor:
                            use: True
                        textColor:
                            use: True
                    secondary:
                        use: True
                        name: "button-secondary"
                        backgroundColor:
                            use: False
                        textColor:
                            force: "{colors.primary}"
            typography:
                use: True
                unique: True
```

### Component rules
Name | Type | Description
-------------------------
`use` | Bool | Use this component over the previous layer or base. Later component references in the same scope can either redundantly affirm use or disable use. Applying `use: False` means the layer is disabled and the previous layer's rule applies.
`unique` | Bool | Any later component that attempts to redefine this component or any subcomponents throws an error. Default behaviour is `unique: False`.
`reroute` | String:String | The specification for design.md includes a system for referencing other sections for styling. However, since multiple themes may not have compatible color references, a field is required for resolution.
`name` | String | Sets the component name for identity resolution. Due to the fuzzy nature of the design.md standard, the lowest component referrence possible is through file names. This means the default behaviour is to identify components by file name, but file structure uniqueness is optional and may not be compatible between different themes. The `name` field means the component is forced to have a specific id, which should be coalesced throughout the rest of the document.

