WebGenAI provides a docker-based web app for creating projects and logic.
For more information, [click here](https://apilogicserver.github.io/Docs/WebGenAI/).

You will require an OpenAI API Key.  See the Manager readme.  You must also obtain a WebGenAI license (free eval, no credit card).

This is the default location for WebGenAI - projects, sqlite databases, etc.
* Examine these to verify genai logic, but use export to debug or make changes.
* You can export created projects to customize in your IDE - see [Export](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#export)
* See [Import / Merge WebGenai](https://apilogicserver.github.io/Docs/IDE-Import-WebGenAI/)

See docker_compose for WebGenAI run instructions.

> Note: you can also use your IDE Coding Assistant (e.g, Copilot) to create projects from prompts.

As shown below, you provide a database description and optionally logic.  
* Creates sample data, and derived columns in schema

![sample](https://apilogicserver.github.io/Docs/images/sample-ai/genai/genai-prompt.png)
