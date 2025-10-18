import re
from lexi_memory import LexiMemoryStore

class LexiInterpreter:
    """A simple interpreter for the Lexi DSL."""
    def __init__(self, persistent: bool = True):
        """Initialize the Lexi interpreter."""
        self.context = {"mood": None, "tone": None, "style": None}
        self.memory = LexiMemoryStore() if persistent else {}
        self.tasks = {}      # for task definitions
        self.output = []

    def remember(self, key, value):
        """Store a value in memory."""
        if isinstance(self.memory, LexiMemoryStore):
            self.memory.set(key, value)
        else:
            self.memory[key] = value

    def recall(self, key):
        """Retrieve a value from memory."""
        if isinstance(self.memory, LexiMemoryStore):
            return self.memory.get(key, f"[undefined:{key}]")
        return self.memory.get(key, f"[undefined:{key}]")

    def parse(self, code: str):
        """Parse and execute Lexi DSL code."""
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        i = 0
        while i < len(lines):
            line = lines[i]

            # Task definition
            if line.startswith("task"):
                _, name = line.split(maxsplit=1)
                block = []
                i += 1
                while i < len(lines) and not lines[i].startswith("}"):
                    block.append(lines[i])
                    i += 1
                self.tasks[name] = "\n".join(block)

            # Task call
            elif line.startswith("call"):
                _, name = line.split(maxsplit=1)
                if name in self.tasks:
                    self.parse(self.tasks[name])
                else:
                    self.output.append(f"[Unknown task: {name}]")

            # Memory ops
            elif line.startswith("remember"):
                key, value = re.findall(r'remember (\w+)\s*=\s*(.+)', line)[0]
                self.remember(key.strip(), value.strip().strip('"'))
            elif line.startswith("recall"):
                _, key = line.split(maxsplit=1)
                val = self.recall(key)
                self.output.append(val)

            # Existing primitives
            elif line.startswith("set"):
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

# Example usage
if __name__ == "__main__":
    code = '''
    set mood happy
    say "Hello!"
    if mood is happy {
        say "I'm feeling great today!"
    }
    remember favorite_color = "blue"
    say "My favorite color is:"
    recall favorite_color
    task greet {
        say "Greetings, traveler!"
    }
    call greet
    repeat 2 {
        say "This is fun!"
    }
    '''
    interpreter = LexiInterpreter()
    interpreter.parse(code)
    result = interpreter.render()
    print(result)
