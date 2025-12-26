import numpy as np

class NumberRangeNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "start": ("INT", {"default": 1, "min": -100000, "max": 100000, "step": 1}),
                "end": ("INT", {"default": 10, "min": -100000, "max": 100000, "step": 1}),
                "step": ("INT", {"default": 1, "min": 1, "max": 100000, "step": 1}),
            },
        }

    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int_range", "float_range")
    OUTPUT_IS_LIST = (True, True)
    FUNCTION = "generate_range"
    CATEGORY = "Nimbus-Pack/Number"

    def generate_range(self, start, end, step):
        # Ensure step is valid (min 1 in config, but good to be safe)
        if step == 0:
            step = 1
            
        # Generate inclusive range for integers
        # range(start, end + 1, step) handles inclusive end for positive steps
        # For negative steps, it would be range(start, end - 1, step)
        
        if step > 0:
            values = list(range(start, end + 1, step))
        else:
             # If step is negative (though config min is 1, user might change it manually in json)
             # Let's assume positive step for now based on config "min": 1
             values = list(range(start, end + 1, step))

        # If the generated range is empty, return start
        if not values:
             values = [start]

        int_list = values
        float_list = [float(x) for x in values]

        return (int_list, float_list)
