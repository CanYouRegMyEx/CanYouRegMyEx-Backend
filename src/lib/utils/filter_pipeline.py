import re

class FilterPipeline:
    """
    A simple helper class for applying multiple regex sequentially.\n
    pattern_sequence: List[re.Pattern]      - Patterns to be applied, sequentially\n
    op_string: str                          - Operations to perform with the respective pattern at the same index,
    ? is matching, - is removing the pattern from the string\n
    """

    def __init__(self, pattern_sequence, op_string=""):
        self.pattern_sequence = pattern_sequence
        self.op_string = op_string

    def filter(self, input_str: str):
        res = input_str

        for i, pattern in enumerate(self.pattern_sequence):

            if i >= len(self.op_string): break

            operation = self.op_string[i]

            if operation == '?':
                res = "".join(re.findall(pattern, res))
            elif operation == '-':
                res = re.sub(pattern, '', res)
        
        return res

    def __str__(self):
        return str(self.pattern_sequence)
