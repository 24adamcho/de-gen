# Component format specification
Components should be written as miniature design.md documents. They should be generalizable and broadly applicable to multiple situations.
Similarly, the folder structure should reflect the design system used.
Components are organized as a css styling frontmatter, followed by the human-readable description. Descriptions are later included in the design.md components section.
### Example
```
...
|-theme
    |-components
    |   |-buttons
    |   |   |-primary.md
    |   |   |-secondary.md
    |   |   |...
    |   |-paragraphs
    |   |   |-...
    |   |-...
    |-...
```

primary.md
```md
backgroundColor:"{colors.tertiary}"
textColor:"{colors.primary}"
rounded:"{rounded.sm}"
padding:12px
---
A primary button designed for bold, definitive actions.
```
