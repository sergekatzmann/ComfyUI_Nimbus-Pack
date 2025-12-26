class MathOperationNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("INT", {"default": 0, "min": -1000000000, "max": 1000000000, "step": 1}),
                "b": ("INT", {"default": 0, "min": -1000000000, "max": 1000000000, "step": 1}),
                "operation": (["min", "max", "add", "subtract", "multiply", "divide"],),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("result",)
    FUNCTION = "process_math"
    CATEGORY = "Nimbus-Pack/Math"

    def process_math(self, a, b, operation):
        if operation == "min":
            result = min(a, b)
        elif operation == "max":
            result = max(a, b)
        elif operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b != 0:
                result = a // b
            else:
                result = 0
        else:
            result = 0 # Should not happen based on input types
            
        return (result,)
