import re


class LexiInterpreter:
    def __init__(self):
        self.context = {"mood": None, "tone": None, "style": None}
        self.output = []

    def parse(self, code: str):
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("set"):
                _, param, value = line.split(maxsplit=2)
                self.context[param] = value
            elif line.startswith("say"):
                text = re.match(r'say\s+"(.+)"', line)
                if text:
                    self.output.append(text.group(1))
            elif line.startswith("repeat"):
                count = int(line.split()[1])
                block = []
                i += 1
                while i < len(lines) and not lines[i].startswith("}"):
                    block.append(lines[i])
                    i += 1
                for _ in range(count):
                    self.parse("\n".join(block))
            elif line.startswith("if"):
                cond = re.match(r"if (\w+) is (\w+)", line)
                if cond:
                    key, val = cond.groups()
                    block = []
                    i += 1
                    while i < len(lines) and not lines[i].startswith("}"):
                        block.append(lines[i])
                        i += 1
                    if self.context.get(key) == val:
                        self.parse("\n".join(block))
            i += 1

    def render(self):
        return "\n".join(self.output)


if __name__ == "__main__":
    code = """
    set mood happy
    set tone casual
    say "Hello there!"
    if mood is happy {
        say "It's great to see you!"
    }
    repeat 2 {
        say "Have a wonderful day!"
    }
    """
    interpreter = LexiInterpreter()
    interpreter.parse(code)
    result = interpreter.render()
    print(result)
