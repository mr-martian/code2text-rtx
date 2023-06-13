from code2text.translate import Pattern
from tree_sitter_apertium import RTX

base_rules = [
    {'pattern': '["{" "}" (comment)] @root', 'output': ''},
    {
        'pattern': '(source_file (_) @thing_list) @root',
        'output': [
            {
                'lists': {'thing_list': {'join': '\n'}},
                'output': '{thing_list}'
            }
        ]
    },
    {
        # TODO: x = @x ;
        'pattern': '''
(attr_rule
  name: (ident) @name_text
  (attr_default src: (ident) @src_text trg: (_) @trg_text)
  [(ident) (string) (attr_set_insert)]* @tag_list
) @root''',
        'output': [
            {
                'lists': {'tag_list': {'join': ', '}},
                'output': 'Define the tag category {name_text} as consisting of {tag_list}, and if this category is not present, then insert {src_text} while parsing and replace it with {trg_text} when outputting.',
            }
        ],
    },
    {
        # TODO: x = @x ;
        'pattern': '''
(attr_rule
  name: (ident) @name_text
  [(ident) (string) (attr_set_insert)]* @tag_list
) @root''',
        'output': [
            {
                'lists': {'tag_list': {'join': ', '}},
                'output': 'Define the list {name_text} as consisting of {tag_list}.',
            }
        ],
    },
    {
        'pattern': '(attr_set_insert (ident) @set_text) @root',
        'output': 'all the tags in {set_text}',
    },
    {
        'pattern': '(output_rule pos: (ident) @pos_text (magic)) @root',
        'output': 'When outputting {pos_text}, just copy the tags from the input.',
    },
    {
        # TODO: this doesn't capture in order?
        'pattern': '(output_rule pos: (ident) @pos_text [(ident) (lit_tag)] @tag_list) @root',
        'output': [{
            'lists': {'tag_list': {'join': ', '}},
            'output': 'When outputting {pos_text}, put the following: {tag_list}.',
        }],
    },
    {
        'pattern': '(output_rule "." @root)',
        'output': ', ',
    },
    {
        'pattern': '(output_rule (ident) @root (#match? @root "^_$"))',
        'output': 'the part of speech tag',
    },
    {
        'pattern': '(output_rule (lit_tag (ident) @tag_text) @root)',
        'output': 'the literal tag {tag_text}',
    },
    {
        'pattern': '(output_rule (ident) @root_text)',
        'output': 'the {root_text} tag',
    },
    {
        'pattern': '(attr_rule (ident) @root_text)',
        'output': '{root_text}',
    },
    {
        'pattern': '(reduce_rule_group . (ident) @pos_text . (arrow) (reduce_rule) @rule_list) @root',
        'output': [{
            'lists': {'rule_list': {'join': '\n'}},
            'output': '{pos_text} phrases can be constructed according to the following rules:\n{rule_list}'
        }],
    },
    {
        'pattern': '''
(reduce_rule
  rule_name: (string)? @name_text
  (weight)? @weight_text
  [(pattern_element) (unknown)] @pattern_list
  (condition)? @cond
  [(set_surf) (set_global_var) (set_global_str) (set_chunk_attr)]? @set_list
  (reduce_output) @output
) @root''',
        'output': [
            # TODO: use other fields
            {
                'lists': {'pattern_list': {'join': ', '}},
                'output': 'When parsing, match {pattern_list}, and when outputting, put {output}.',
            },
        ],
    },
    {
        'pattern': '(unknown) @root',
        'output': 'an unknown word',
    },
    {
        # TODO: lemmas, clip sides
        'pattern': '''
(pattern_element
  (magic)? @magic
  . (ident) @pos_text
  ("." . [(ident) (attr_set_insert) (string)] @tag_list)?
  ("$" . (ident) @set_list)?
) @root''',
        'output': [
            {
                'cond': [{'has': 'set_list'}],
                'lists': {'set_list': {'join': ', '}},
                'output': 'a word with part-of-speech {pos_text}, from which copy the tags {tag_list}',
            },
        ],
    },
    {
        'pattern': '(attr_pair src: (_) @src trg: (_) @trg) @root',
        'output': 'from {src} to {trg}',
    },
    {
        'pattern': '(attr_pair [(ident) (string)] @root_text)',
        'output': '{root_text}',
    },
    {
        'pattern': '(attr_pair (attr_set_insert (ident) @set_text)) @root',
        'output': 'every tag in {set_text}',
    },
    {
        'pattern': '(retag_rule src_attr: (ident) @src_text trg_attr: (ident) @trg_text (attr_pair) @pair_list) @root',
        'output': [{
            'lists': {'pair_list': {'join': ', '}},
            'output': 'To change {src_text} to {trg_text}, change: {pair_list}.',
        }],
    },
]

rules = [Pattern.from_json(RTX, rl) for rl in base_rules]
