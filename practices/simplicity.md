## Logic

- code is just a knowledge graph of the topics needed to achieve an objective. divide and organize it accordingly
  - macro and micro cosmos
    - things are made of even smaller things, recursively

- KISS (Keep It Simple Stupid)
  - Do one thing and do it well
    - there should not be more than one thing going on in a single place
    - follow the Unix philosophy
  - how to design a solution
    - divide and conquer
      - define the initial input
      - define the final output
      - define the side-effects, like saving data into the database
      - define the steps to go from initial input to final output
      - for each step, repeat this process
  - if the task at hand is becoming difficult, it's probably going in the wrong direction. it's a sign that we are:
    - not splitting and abstracting the task into smaller pieces
    - we are going in a way we are not supposed too (usually things we don't know that we don't know) and we are forcing our way against the natural order of things

- YAGNI
  - only implement what we absolutely know and use today

- Explicit is better than implicit

- no ambiguity
  - fail early
    - only handle use-cases we are sure about
    - throw exceptions on unexpected use-cases, instead of letting them continue
      - your code should fail early when it encounters things we don't know or aren't sure about. Your code should not try to handle these unexpected uses-cases and should not let them continue
      - we can deal with things we don't know, once we get a better view at them in the error logs
    - do not use default values. it must be explicit that the values may not exist, and stop the propagation of nullable values as early as possible, since nullable values are ambiguous values
  - avoid global changes or overrides
    - stick to the the tech stack and libraries defaults
    - your changes should only impact the scope of your task, and not outside of it
      - if you have to change how a tool works for your use-case, keep the changes isolated in your use-case. do not let those changes leak outside of your use-case

- avoid abstractions
  - there is a bigger risk of building the wrong abstractions and cutting important accesses or details from the original instances

- good work is work you don't notice
  - ...because it flows so well that it does not impact anyone negatively
  - be mindful of how your changes will affect your colleagues and the project
  - your changes should only impact the scope of your task, and not outside of it

- Big O notation / O(n)

- your colleagues must be able to follow and execute the same steps and conclusions as you did

- we also recommend reading the [Zen of Python](https://peps.python.org/pep-0020/)

## Lifecycle of a piece of data

Consider all steps of the lifecycle of a piece of data

- Creation

  - who can create this piece of data?
  - will it conflict with existing data?

- Reading

  - who can read this piece of data?

- Update

  - who can update this piece of data?
  - how will the update affect other pieces of data?

- Undoing

  - how do we keep track of all the changes done to the piece of data?
  - how can changes to the piece of data be undone?
  - who can undo changes?
  - how will undoing changes affect other pieces of data?

- Disposal
  - who can dispose or deactivate a piece of data?
  - how will the disposal affect other pieces of data?
