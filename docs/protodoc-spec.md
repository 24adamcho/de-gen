# Protodoc specification
The protodoc is a file that describes what themes and/or components should be used to generate a design.md document. It should be a series of module and component references that coalesces into the finished output.

The protodoc uses YAML.

## Base fields:
A question mark means that a field is optional.

Name | Type | Example | Description
------------------
`docver` | String | `docver:"1.0"` | Protodoc specification version
`lang`? | String | `lang:"en-us"` | Language setting for design.md output.
`themes` | String array | `themes: ["example/theme"]` | List of folder locations for theme imports.
`layers` | Multi-field tree | see section on layers | Structure describing what components are taken from themes.
`headers`? | Multi-field tree | see design.md examples and documentation | YAML segment that is carried directly to the output design.md YAML.

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
docver: "1.0",
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
`section` | String | Declares a component, or directory of subcomponents, to be part of a design.md section.
`sectionTitle` | String | Optional string that prepends a title to the body section when outputting.

### Sections
Sections follow design.md specs for top level yaml in the design.md frontmatter and body content.

Name | Design.md section | Protodoc section value | Description
---------------------------------
Overview | n/a | `overview` | Brand and style; frontmatter in this section is ignored. If a directory, all child components are concatenated.
Colors | `colors` | `colors` | Color section maps the child component's frontmatters directly to the output section. Subreferences (such as `"{colors.primary}"`) are not dynamically resolved, and must be rerouted.
Component | `component` | `component` | Components define parts and styles. The frontmatters are carried up to the component section. Component names are default resolved as `{directory}-{filename}`, similar to css. Component keys can be overloaded with the `name` rule. Component names are used for body section names.
Typography | `typography` | `typography` | Same as component section, but resolves `{filename}` as subsection key.
Footer | n/a*** | `footer` | Section included at the end of the design.md. All child component bodies are concatenated.
*`{filename}` does not include the file extensions. `"primary.md"` resolves to just `"primary"`.
** Sections named here have defaults for their design.md section titles; these can still be overloaded with `sectionTitle`
*** Since there is no predefined footer title, it will use the value of `sectionTitle`, even if it is a blank string.

Layout, elevation, and shapes are literally just components but you treat them special for some reason. For that reason, any nondefined component frontmatter and hoists it to the frontmatter in the output. The body is concatenated.
Predefined sections are available, because typing the `sectionTitle` every time would probably get annoying. Predefined sections have their frontmatters hoisted, similar to nondefined sections.

Name | Design.md section | Protodoc section value | Default title
---------------------------------
Layout | `spacing` | `layout` | "Layout & Spacing"
Elevation | n/a* | `elevation` | "Elevation & Depth"
Shapes | `rounded` | `shapes` | "Shapes"
*Elevation doesn't use the frontmatter according to spec, but it'll hoist it anyway.

For example:
```yaml
docver: "1.0",
themes: ["example/theme", "another/theme"]
layers:
    example:
        theme:
            components:
                use: True
                section: "component"
            layout:
                use: True
                section: "layout"
                sectionTitle: "Layout & Spacing"
```
Will resolve to:
```md
---
components:
    ...
layout:
    ...(contents of layout frontmatter)
---
## Components
...(component body text)
## Layout & Spacing
...(example/theme/layout body text)
```
