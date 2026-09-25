from fail.tools.tool import Tool


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def list_tools(self):
        return list(self._tools.values())

    def get_tool_descriptions(self):
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]