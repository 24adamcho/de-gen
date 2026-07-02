# De-Gen (Design.md Generator)
DeGen is a program that uses componentized markdown files to construct a design.md file. 

## Why
There are a few benefits to this:
- Sections and components are reusable between projects and versions
- Outputs are deterministic, rather than ai-genning a new high-token-count design.md doc every time
- Design.md docs are large and heavy to write by hand, but writing designs for smaller bits is easier
- Componentized markdown files organized into themes means they can be 'kitbashed', or assembled from several themes.

## How
There are four concepts to go over.
### Component
The definition for 'component' differs from the design.md specification. In this system, a component is defined as a markdown file that can have 'rules' applied to it.
Here are the rules that can be applied to components:

| Rule | Type | Description
|------|------|------------
| `use` | Bool | Use this component over the previous layer or base. `use: False` means the component is disabled and the previous layer's rule applies.
| `unique` | Bool | Any later component that attempts to redefine this component or any subcomponents throws an error. Default behaviour is `unique: False`.
| `reroute` | String:String (`"From":"To"`) | The specification for design.md includes a system for referencing other sections for styling. However, since multiple themes may not have compatible color references, a field is required for resolution. The string will act as a replacement for any occurance of the first string.
| `name` | String | Sets the component name for identity resolution. Due to the fuzzy nature of the design.md standard, the lowest component referrence possible is through file names. This means the default behaviour is to identify components by file name, but file structure uniqueness is optional and may not be compatible between different themes. The `name` field means the component is forced to have a specific id, which should be coalesced throughout the rest of the document.
| `section` | String | Declares a component, or directory of subcomponents, to be part of a design.md section.

### Layer
A layer defines the member of a tree of components that determines the order they will be applied to the final output. For example:
```md
layers:
    themes:
        example:
            use: True
        another:
            buttons:
                use: True
```
Means that 'example' will be loaded first, and 'another/buttons' will be overlaid on top of it. Any components in 'another/buttons' that have the same name reference as 'example/buttons' will overload them, meaning that 'example/buttons' will not be applied.
Layers also use the same rules as components, and these rules apply to any child components.
Also to note, the field names of the members directly correspond to the file directories, acting as a reference tree. For example:
```
.directory
|-protodoc.yaml
|-themes
| |-example
| | |-buttons
| | | |-...
| | |-...
| |-another
| | |-buttons
| | | |-...
| | |-...
| |-...
|-...
```
would approximately be the file structure of the example above.

### Section
A section is the structural definition of the parts of a design.md doc. For example, there are sections for 'components' and 'typography', that map directly to the body content of the markdown. Sections are also ordered, with some being prioritized in the default spec.
Here are the fields that can be applied to sections:

| Name | Type | Description
| -----|------|--------------------
| `use`? | Bool | Broadly enables or disables sections. Defaults true.
| `title`? | String | Prepended tite string. Defaults to not outputting. . Section title strings have their `<h2>` (`##`) items prepended. If the section title is undefined or an empty string (`""`), the title is not written.
| `order`? | Number | Determines the sorting order of the final output. The default is to assemble without thinking about it, with design.md sections taking precedence. When `defaultSections` is set to true, default design.md sections are given the numerical value in the order they are defined (see spec).
| `referenceFormat`? | String("file", "parent-file", "full") | Enum for the component name reference format. Used to determine component reference collisions for overloads. Undefined defaults to "parent-file". When `defaultSections` is set to true, the reference format is set per-section to closest approximation of spec.
| .
| `prelude`? | String | Directions to a markdown file that will be used as the first body block. The prelude will not include itself in later concatenation. Defining the prelude to be a part of the section is not necessary, but can help illustrate that it is a member.
| `useMetadata`? | String("True", "False", "Layered", "Child") | Enum that determines how to hoist any frontmatter data for the section to the output. "True" means it will overlay itself on the top level frontmatter. "Layered" means it will overlay itself on an object named by the section. "Child" means it will use the file name to construct a parent object that the frontmatter is hoisted to, which is then layered on the section object. "False" means that the metadata will not be used. Default is "False". 
| `useBody`? | bool | Enables or disables using the body in the section when outputting. Defaults to True.
| `usePreludeMetadata`? | String("True", "False", "Layered", "Child") | Same as `useMetadata`.
| `memberPrefix`? | String | String to prepend to any body content that is declared to be a part of this section. Useful for bullet points.
| `memberPostfix`? | String | Appended version of `memberPrefix`. No clue if it's useful.
| `memberSplit`? | String | String used to join member body content together. For example, to put two newlines between bodies, the string `'\n\n'` is used. Default is '\n\n'.

There are also default sections, which can be overridden. Predefined sections available because typing the `sectionTitle` and othersomesuch configs every time would probably get annoying.  Default sections generally follow design.md specs for top level yaml in the design.md frontmatter and body content. The sections described here (except `footer`) are outputted according to specification order.

| Name | Design.md section | Protodoc section value | Description
| -----|-------------------|------------------------|------------
| Overview | n/a | `overview` | Brand and style; frontmatter in this section is ignored. If a directory, all child components are concatenated.
| Colors | `colors` | `colors` | Color section maps the child component's frontmatters directly to the output section. Subreferences (such as `"{colors.primary}"`) are not dynamically resolved, and must be rerouted.
| Component | `components` | `components` | Components define parts and styles. The frontmatters are carried up to the component section. Component names are default resolved as `{directory}-{filename}`, similar to css. Component keys can be overloaded with the `name` rule. Component names are used for body section names.
| Typography | `typography` | `typography` | Same as component section, but resolves `{filename}` as subsection key.
| Footer | n/a*** | `footer` | Section included at the end of the design.md. All child component bodies are concatenated. Frontmatter in this section are ignored.
*`{filename}` does not include the file extensions. `"primary.md"` resolves to just `"primary"`.
** Sections named here have defaults for their design.md section titles; these can still be overloaded with `sectionTitle`
*** Since there is no predefined footer title, it will use the value of `sectionTitle`, even if it is a blank string.

Predefined sections have their frontmatters hoisted, similar to nondefined sections.

| Name | Protodoc section value | Default title
|------|------------------------|--------------
| Layout | `layout`*** | "Layout & Spacing"
| Elevation* | `elevation`** | "Elevation & Depth"
| Shapes | `shapes`*** | "Shapes"
- **Elevation also does not have a defined design.md key, but for sectionTitle this is the string used.
- ***Instead of using the design.md spec for design tokens, uses a more descriptive token for the section.

Sections are defined in the protodoc:
```yaml
sections:
    overview:
        use: True
        useMetadata: False
        order: 0 #highest priority
...
layers:
    project:
        overview:
            use: True
            section: "overview" #declares this component to be placed in the 'overview' section of the output
```

### Protodoc
The protodoc is a YAML file that defines the sections, components, layers, and other things that will be included outputted, or other options.

| Name | Type | Example | Description
|------|------|---------|------------
| `docver` | String | `docver:"1.0"` | Protodoc specification version (not currently used but required).
| `lang`? | String | `lang:"en-us"` | Language setting for design.md output. (not currently used)
| `themes` | String array | `themes: ["example/theme"]` | List of folder locations for theme imports. Folders are relative to the protodoc.yaml location.
| `outputDir`? | String | `outputDir: "./designs"` | Output directory. Defaults to `"."`.
| `layers` | Multi-field tree | see section on layers | Structure describing what components are taken from themes.
| `defaultSections`? | bool | Enables or disables default section definitions. Default: `false`. Defining a new section with the same key (see Section) take precedence over default definitions.
| `sections`? | Multi-field tree | see Section
| `headers`? | Multi-field tree | see design.md examples and documentation | YAML segment that is carried directly to the output design.md YAML.
| `title`? | String | Optional design.md body `<h1>` document title. The # in `# Title` is not prepended.

