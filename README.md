# How Value Names in Tool Schemas Change the Searches of AI Agents

An AI agent fills the fields of a tool with values from a fixed list. This project asks what happens when an allowed value is also an everyday word.

For example, a traveller asks a booking agent for "a hotel" and may mean any place to stay. The search tool, however, accepts only `hotel` or `guesthouse`. If the agent writes `type = hotel`, the search can hide every guesthouse that fits the traveller's needs, although the call is valid under the tool's schema.

The study measures how often this happens with several language models, tests what causes it, tests repairs, and proposes a release test for changes to tool schemas.

## Status

- The preprint and its code and data are in preparation and will be added to this repository.
- The registered held-out test is public on OSF: https://osf.io/bv8q9 (registration A).

## Author

Dev D. Goyal, Independent Researcher.

## License

Text: CC BY 4.0. The license of the code will be stated when the code is added.
