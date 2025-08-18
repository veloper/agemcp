# Apache AGE MCP Server

These tools provide an interface for AI Agents to manage multiple graphs in Apache AGE. They expose tools for creating, updating, administering, and visualizing graphs.

| Tool Name               | Purpose/Description                                                                 | Arguments                                                                                   |
|-------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| `get_or_create_graph`   | Get or create a graph with the specified name.                                      | `graph_name: str`                                                                           |
| `list_graphs`           | List all graph names in the database.                                               |                                                                                             |
| `upsert_graph`          | Upsert both vertices and edges into the specified graph (deep merge).                | `graph_name: str`, `vertices: List[Dict[str, Any]]`, `edges: List[Dict[str, Any]]`          |
| `upsert_edge`           | Insert or update an edge's properties in a graph non-destructively.                 | `graph_name: str`, `label: str`, `edge_start_ident: str`, `edge_end_ident: str`, `properties: Dict[str, Any]` |
| `upsert_vertex`         | Insert or update a vertex's properties in a graph non-destructively.                | `graph_name: str`, `vertex_ident: str`, `label: str`, `properties: Dict[str, Any]`          |
| `drop_graphs`           | Drop one or more graphs by name.                                                    | `graph_names: List[str]`                                                                    |
| `drop_vertex`           | Remove a vertex by ident.                                                           | `graph_name: str`, `vertex_ident: str`                                                      |
| `drop_edge`             | Remove an edge by ident.                                                            | `graph_name: str`, `edge_ident: str`                                                        |
| `generate_visualization`| Generate a single-page HTML file visualizing a graph using vis.js and pyvis.        | `graph_name: str`                                                                           |


## Server Setup

1. Clone the repository:

    ```bash
    git clone <repository-url> /your/local/path/to/agemcp
    ```

2. Navigate to the project directory:

    ```bash
    cd /your/local/path/to/agemcp
    ```
3. Install the required dependencies:

    ```bash
    uv sync
    ```
4. Run the server:

    ```bash
    uv run agemcp run --port 8000 --transport streamable-http
    ```
   You should see something like this:

    ```
    [07/30/25 14:32:54] INFO     Starting MCP server 'agemcp' with transport 'streamable-http' on http://0.0.0.0:8000/mcp/
    INFO:     Started server process [13951]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    ```


## Client Setup

### VSCode
1. Open Command Palette (Cmd+Shift+P or Ctrl+Shift+P).
2. Select `MCP: Add Server...`
3. Choose "HTTP" option.
4. Enter the server URL (e.g., `http://localhost:8000/mcp/`).
5. Enter a "server id" (e.g., `agemcp`).
6. Select `Global` for the scope.
7. Done. (It should appear in the `extensions` sidebar.)

### Roo / Cline / Claude
```json
{
  "mcpServers": {
    "agemcp": {
      "url": "http://localhost:8000/mcp/",
      "type": "streamable-http",
      "headers": {
        "Content-Type": "application/json"
      }
    }
  }
}
```
