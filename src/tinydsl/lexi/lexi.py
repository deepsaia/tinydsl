from pathlib import Path
from tinydsl.core.base_dsl import BaseDSL
from tinydsl.parser.lark_lexi_parser import LarkLexiParser


class LexiInterpreter(BaseDSL):
    """
    Lexi DSL interpreter.

    Use version='v2' for enhanced features:
    - String operations (concat, split, substring, length, upper, lower)
    - Lists/Arrays (create, append, get, length, foreach)
    - Pattern matching (match/case)
    - Error handling (try/catch)
    """

    def __init__(self, version: str = "v1"):
        """
        Initialize Lexi interpreter.

        Args:
            version: 'v1' (default) or 'v2' (enhanced features)
        """
        self.version = version
        self.parser = LarkLexiParser(version=version)

    @property
    def name(self) -> str:
        """DSL identifier."""
        return "lexi"

    @property
    def grammar_path(self) -> Path:
        """Path to Lark grammar file."""
        data_dir = Path(__file__).parent.parent / "data"
        return data_dir / "lexi_grammar.lark"

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
