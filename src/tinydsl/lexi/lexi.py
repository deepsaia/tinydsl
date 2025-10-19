from tinydsl.parser.lark_lexi_parser import LarkLexiParser

class LexiInterpreter:
    def __init__(self):
        self.parser = LarkLexiParser()

    def parse(self, code: str):
        self.output = self.parser.parse(code)

    def render(self):
        return self.output


# Example usage
if __name__ == "__main__":
    code = """
    set mood happy
    say "Hello!"
    if mood is happy {
        say "I'm feeling great today!"
    }
    remember favorite_color = "green"
    say "My favorite color is:"
    recall favorite_color
    task greet {
        say "Greetings, traveler!"
    }
    call greet
    repeat 2 {
        say "This is fun!"
    }
    """
    interpreter = LexiInterpreter()
    interpreter.parse(code)
    result = interpreter.render()
    print(result)
