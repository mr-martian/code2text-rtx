from code2text.translate import Pattern
from tree_sitter_apertium import RTX

base_rules = [
    {'pattern': '[(semicolon) (comment)] @root', 'output': ''},
]

rules = [Pattern.from_json(RTX, rl) for rl in base_rules]
