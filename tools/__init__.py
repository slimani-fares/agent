from tools import calculator, recall, remember, web_search, read_file

TOOLS = {
    "calculator": calculator.calculator,
    "web_search": web_search.web_search,
    "read_file": read_file.read_file,
    "remember": remember.remember,
    "recall": recall.recall,
}

TOOL_SCHEMAS = [
    calculator.SCHEMA,
    remember.SCHEMA,
    web_search.SCHEMA,
    read_file.SCHEMA,
    recall.SCHEMA,  
]
