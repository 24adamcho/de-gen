# Protodoc specification
The protodoc is a file that describes what themes and/or components should be used to generate a design.md document. It should be a series of module and component references that coalesces into the finished output.

The protodoc uses YAML.

## Base fields:
A question mark means that a field is optional.

Name | Type | Example | Description
------------------
`docver` | String | `docver:"1.0"` | Protodoc specification version
`lang`? | String | `lang:"en-us"` | Language setting for design.md output.
`themes` | String array | `themes: ["example/theme"]` | List of folder locations for theme imports. Folders are relative to the protodoc.yaml location.
`outputDir`? | String | `outputDir: "./designs"` | Output directory. Defaults to `"."`.
`layers` | Multi-field tree | see section on layers | Structure describing what components are taken from themes.
`defaultTitles`? | bool | Enables or disables default titles. Default: `false`. `sectionTitles` take precedence over default titles.
`sections`? | Multi-field tree | see Sections
`headers`? | Multi-field tree | see design.md examples and documentation | YAML segment that is carried directly to the output design.md YAML.
`title`? | String | Optional design.md body `<h1>` document title. The # in `# Title` is not prepended.

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
                reroute: "black:{colors.primary}"
            components:
                buttons:
                    primary:
                        name: "button-primary"
                        backgroundColor: "white"
                        textColor: "#fa182f"
                    secondary:
                        use: True
                        name: "button-secondary"
                        backgroundColor: "green"
                        textColor: "{colors.primary}"
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

### Sections
Sections are document body elements that can be defined.

```yaml
docver: "1.0"
themes: ["example/theme", "another/theme"]
sections:
    intentions:
        title: "Design intentions"
        prelude: "example/theme/instructions"
layers:
    example:
        theme:
            use: True
            instructions:
                section: "intentions"
    another:
        theme:
            instructions:
                section "intentions"
```
The output will use a markdown file 'example/theme/instructions.md' as the first body block in an off-spec section, and then concatenate any later section additions. 
The section name is given by the key. Using the same section name as the design.md section overloads the default, if set.

Name | Type | Description
---------------------------------
`use`? | Bool | Broadly enables or disables sections. Defaults true.
`title`? | String | Prepended tite string. Defaults to not outputting. . Section title strings have their `<h2>` (`##`) items prepended. If the section title is undefined or an empty string (`""`), the title is not written.
`order`? | Number | Determines the sorting order of the final output. The default is to assemble without thinking about it, with design.md sections taking precedence. When `defaultTitles` is set to true, default design.md sections are given the numerical value in the order they are defined (see spec).
`referenceFormat`? | String("file", "parent-file", "full") | Enum for the component name reference format. Used to determine component reference collisions for overloads. Undefined defaults to "parent-file". When `defaultTitles` is set to true, the reference format is set per-section to closest approximation.
.
`prelude`? | String | Directions to a markdown file that will be used as the first body block. The prelude will not include itself in later concatenation. Defining the prelude to be a part of the section is not necessary, but can help illustrate that it is a member.
`useMetadata`? | String("True", "False", "Layered", "Child") | Enum that determines how to hoist any frontmatter data for the section to the output. "True" means it will overlay itself on the top level frontmatter. "Layered" means it will overlay itself on an object named by the section. "Child" means it will use the file name to construct a parent object that the frontmatter is hoisted to, which is then layered on the section object. "False" means that the metadata will not be used. Default is "False". 
`useBody`? | bool | Enables or disables using the body in the section when outputting. Defaults to True.
`usePreludeMetadata`? | String("True", "False", "Layered", "Child") | Same as `useMetadata`.
`memberPrefix`? | String | String to prepend to any body content that is declared to be a part of this section. Useful for bullet points.
`memberPostfix`? | String | Appended version of `memberPrefix`. No clue if it's useful.
`memberSplit`? | String | String used to join member body content together. For example, to put two newlines between bodies, the string `'\n\n'` is used. Default is '\n\n'.

There are also default sections, which can be overridden. Default sections generally follow design.md specs for top level yaml in the design.md frontmatter and body content. The sections described here (except `footer`) are outputted according to specification order.

Name | Design.md section | Protodoc section value | Description
---------------------------------
Overview | n/a | `overview` | Brand and style; frontmatter in this section is ignored. If a directory, all child components are concatenated.
Colors | `colors` | `colors` | Color section maps the child component's frontmatters directly to the output section. Subreferences (such as `"{colors.primary}"`) are not dynamically resolved, and must be rerouted.
Component | `components` | `components` | Components define parts and styles. The frontmatters are carried up to the component section. Component names are default resolved as `{directory}-{filename}`, similar to css. Component keys can be overloaded with the `name` rule. Component names are used for body section names.
Typography | `typography` | `typography` | Same as component section, but resolves `{filename}` as subsection key.
Footer | n/a*** | `footer` | Section included at the end of the design.md. All child component bodies are concatenated. Frontmatter in this section are ignored.
*`{filename}` does not include the file extensions. `"primary.md"` resolves to just `"primary"`.
** Sections named here have defaults for their design.md section titles; these can still be overloaded with `sectionTitle`
*** Since there is no predefined footer title, it will use the value of `sectionTitle`, even if it is a blank string.

Layout, elevation, and shapes are literally just components but you treat them special for some reason. For that reason, any nondefined component frontmatter and hoists it to the frontmatter in the output. The body is concatenated before the footer.
Predefined sections are available, because typing the `sectionTitle` every time would probably get annoying. Predefined sections have their frontmatters hoisted, similar to nondefined sections.

Name | Protodoc section value | Default title
---------------------------------
Layout | `layout`*** | "Layout & Spacing"
Elevation* | `elevation`** | "Elevation & Depth"
Shapes | `shapes`*** | "Shapes"
*Elevation doesn't use the frontmatter according to spec, but it'll hoist it anyway.
**Elevation also does not have a defined design.md key, but for sectionTitle this is the string used.
***Instead of using the design.md spec for design tokens, uses a more descriptive token for the section.

For example:
```yaml
docver: "1.0",
themes: ["example/theme", "another/theme"]
layers:
    example:
        theme:
            components:
                use: True
                section: "components"
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
