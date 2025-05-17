Model Context Protocol is a way for:

1. **Bus User ad hoc flows** using existing published mcp services (vs. hard-coding in IT as an endpoint; flows can be cached for repeated use)

    * ***Natural Language access*** to corporate databases for improved user interfaces

    * LLMs ***choreograph*** multiple MCP calls (to 1 or more MCP servers) in a chain of calls - an agentic workflow. MCPs support shared contexts and goals, enabling the LLM to use the result from 1 call to determine whether the goals has been reached, or which service is appropriate to call next

3. Chat agents to ***discover*** and ***call*** external servers, be they databases, APIs, file systems, etc. MCPs support shared contexts and goals, enabling the LLM

    * ***Corporate database participation*** in such flows, by making key functions available as MCP calls.

This example is [explained here](https://apilogicserver.github.io/Docs/Integration-MCP/).