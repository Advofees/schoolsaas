## Before we start planning a feature

It's important to remind ourselves of our [simplicity practices](/practices/simplicity.md), specially:
- do one thing and do it well (Unix philosophy)
  - there should only be one thing going on in a single place
  - a complex feature should be splitted into individual features that are isolated from each other, but communicate in a few chokeholds.

## Flow of planning a feature:

we go from wider to more narrower scope

- we start by writing down objectives from the point of view from our target user
  - `As a {target user}, I want to {objective}`
- we design the UI mockup
- we decide where will the data be read from, and decide the backend code that needs to be implemented to source the missing data
- we take into account the current context. the feature must be backward compatible with our existing data and constraints. that means designing a transition from the current context to the next context, and deal with the use-cases that can not be migrated.
- we see our limitations and what can be done or not, and start from the top
- in the end, we should have visual mockups or wireframes, as well as the steps, described in text, that the user will go through to achieve their objective, as well as what is going on technically behind the scenes to process those steps
