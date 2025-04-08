from src.Services.PatternMatcher import PatternMatcher
import re
class AfDialogModel:
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
        # Build flags part
        flags = []
        if self.em_enabled:
            flags.append("_em")
        if self.sh_enabled:
            flags.append("_sh")

        flags_str = " ".join(flags)

        # Format the line to be inserted
        if self.template:
            if self.net:
                line = f"{{{self.template}:{self.net}}}"
            else:
                line = f"{{{self.template}}}"
        else:
            line = f"{{{self.net}}}"

        if self.activity_factor:
            line += f" {self.activity_factor}"

        # TODO: do this better.. its not well defined,
        # will probably be an ugly sequence of nested if-else statements
        if self.template_regex:
            line += " template-regexp"
        if self.net_regex:
            line += "_net-regexp"
        if flags_str:
            line += f"_sch{flags_str}"

        return line

    def get_fields_from_line(self, line):
        if line == "":
            return {}
        out = {}
        fields = line.split()
        if len(fields) < 3:
            raise ValueError("Invalid line format")
        try:
            out['template'], out['net'] = fields[0].strip("{}").split(":")
        except ValueError:
            out['net'] = fields[0].strip("{}")
        out['af'] = fields[1]
        flags = fields[2]
        if "net-regex" in flags:
            out['net_regex'] = True
        if "template-regex" in flags:
            out['template_regex'] = True
        # et - regexp_template - regexp_sch_sh
        if "_em" in flags:
            out['em'] = True
        if "_sh" in flags:
            out['sh'] = True
        # logic to parse checkboxes values from the flags
        return out

    def validate_input(self):
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