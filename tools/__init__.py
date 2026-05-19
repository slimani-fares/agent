from tools import calculator, web_search, read_file

TOOLS = {
    "calculator": calculator.calculator,
    "web_search": web_search.web_search,
    "read_file": read_file.read_file,
}

TOOL_SCHEMAS = [
    calculator.SCHEMA,
    web_search.SCHEMA,
    read_file.SCHEMA,
]
