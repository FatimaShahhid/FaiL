from fail.tools.registry import ToolRegistry


class ToolManager:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

        self.allowed_folders = {
            "00 - Dashboard",
            "01 - Ideas",
            "02 - Research",
            "03 - Projects",
            "04 - Architecture",
            "05 - Decisions",
            "06 - Documentation",
            "07 - Canvases",
        }

    def validate(self, tool_name: str, arguments: dict):
        """Validate a tool call before execution."""

        tool = self.registry.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool not found: {tool_name}"
            )

        required_parameters = set(
            tool.parameters.keys()
        )

        provided_parameters = set(
            arguments.keys()
        )

        missing = (
            required_parameters
            - provided_parameters
        )

        if missing:
            raise ValueError(
                f"Missing tool arguments: "
                f"{', '.join(missing)}"
            )

        # -----------------------------------------------------
        # FOLDER PERMISSION CHECK
        # -----------------------------------------------------

        if "folder" in arguments:

            folder = arguments["folder"]

            if folder not in self.allowed_folders:
                raise PermissionError(
                    f"Folder not allowed: '{folder}'. "
                    f"Allowed folders: "
                    f"{', '.join(sorted(self.allowed_folders))}"
                )

        return True

    def run(self, tool_name: str, **kwargs):
        """Validate and execute a tool."""

        self.validate(
            tool_name,
            kwargs,
        )

        tool = self.registry.get(tool_name)

        return tool.execute(**kwargs)