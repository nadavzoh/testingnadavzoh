from src.Services.PatternMatcher import PatternMatcher
from src.Models.AbstractDialogModel import AbstractDialogModel
import re

class AfDialogModel(AbstractDialogModel):
    def __init__(self):
        self.matcher = PatternMatcher()

        self.net = ""
        self.net_regex = False
        self.template = ""
        self.template_regex = False

        self.activity_factor = ""
        self.float_regex_pattern = re.compile(r"^0(\.\d+)?|1(\.0+)?$")

        self.em_enabled = False
        self.sh_enabled = False


    def find_matches(self):
        if not self.net:
            return [], []
        return self.matcher.find_matches(self.template, self.net, self.template_regex, self.net_regex)

    def format_line(self):
        """Format the model data as a line to be inserted/edited in the config file."""
        # Build flags part

        # flags_str = " ".join(flags)

        # Format the line to be inserted
        if self.template:
            if self.net:
                pattern = f"{{{self.template}:{self.net}}}"
            else:
                pattern = f"{{{self.template}}}"
        else:
            pattern = f"{{{self.net}}}"

        parts = [pattern]

        if self.activity_factor:
            parts.append(self.activity_factor)

        flags = []
        # Construct flags part
        if self.template:
            if self.template_regex:
                flags.append("template-regexp")
            else:
                flags.append("template-regular")
        if self.net:
            if self.net_regex:
                flags.append("net-regexp")
            else:
                flags.append("net-regular")

        if self.em_enabled or self.sh_enabled:
            flags.append("sch")
        if self.em_enabled:
            flags.append("em")
        if self.sh_enabled:
            flags.append("sh")

        # Join all parts
        pattern_and_af_str = " ".join(parts)
        flags_str = "_".join(flags)

        line = pattern_and_af_str + " " + flags_str
        return line

    def get_fields_from_line(self, line):
        """Parse a config line into fields the model can understand."""
        if not line:
            return {}

        out = {}
        fields = line.split()
        if len(fields) < 2:
            raise ValueError("Invalid line format")

        # Parse the pattern (template and net)
        try:
            out['template'], out['net'] = fields[0].strip("{}").split(":")
        except ValueError:
            out['net'] = fields[0].strip("{}")

        # Parse the activity factor
        out['af'] = fields[1]

        # Parse the flags
        if len(fields) > 2:
            flags = fields[2].split("_")
            out['template_regex'] = "template-regexp" in flags
            out['net_regex'] = "net-regexp" in flags
            out['em'] = "em" in flags
            out['sh'] = "sh" in flags
        else:
            # default to both True in case of no flags
            out['em'] = True
            out['sh'] = True
        return out

    def validate_input(self):
        """Validate the current input data."""
        # Validate net
        if not self.net:
            raise ValueError("Pattern is required")
        # Validate activity factor
        if not self.activity_factor:
            raise ValueError("Activity Factor is required")
        # Validate activity factor is a float between 0 and 1
        if not self.float_regex_pattern.match(self.activity_factor):
            raise ValueError("Activity Factor must be a number between 0 and 1")

        return True