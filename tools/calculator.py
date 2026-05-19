SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Evaluates a Python mathematical expression and returns the result as a string. "
            "Use Python operators: + - * / for basic ops, ** for exponentiation (NOT ^), "
            "// for integer division, % for modulo. Use parentheses for grouping. "
            "Examples: '5 ** 2' for 5 squared, '(10 + 2) * 3', '2 ** 0.5' for square root."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A string representing the mathematical expression to evaluate.",
                },
            },
            "required": ["expression"],
        },
    },
}


def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression {expression!r}: {type(e).__name__}: {e}"
