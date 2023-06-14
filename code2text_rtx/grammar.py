from code2text.translate import Pattern
from tree_sitter_apertium import RTX

def multi_option(arg1, *args, lists=None):
    import copy
    key, val = arg1
    if args:
        ls = multi_option(*args, lists=lists)
    else:
        ls = [{'cond': [], 'output': '', 'lists': (lists or {})}]
    if key is None:
        for l in ls:
            l['output'] = val + l['output']
        return ls
    else:
        ret = []
        for l in ls:
            l2 = copy.deepcopy(l)
            l2['cond'].append({'has': key})
            l2['output'] = val + l2['output']
            ret.append(l2)
            ret.append(l)
        return ret

base_rules = [
    {'pattern': '["{" "}" (comment)] @root', 'output': ''},
    {
        'pattern': '(source_file (_) @thing_list) @root',
        'output': [
            {
                'lists': {'thing_list': {'join': '\n', 'html_type': 'p'}},
                'output': '{thing_list}'
            }
        ]
    },
    {
        'pattern': '''
(attr_rule
  name: (ident) @name_text
  (attr_default src: (ident) @src_text trg: (_) @trg_text)
  [(ident) (string) (attr_set_insert)] @tag_list
) @root''',
        'output': [
            {
                'lists': {'tag_list': {'join': ', '}},
                'output': 'Define the tag category {name_text} as consisting of {tag_list}, and if this category is not present, then insert {src_text} while parsing and replace it with {trg_text} when outputting.',
            }
        ],
    },
    {
        'pattern': '''
(attr_rule
  name: (ident) @name_text
  [(ident) (string) (attr_set_insert)] @tag_list
) @root''',
        'output': [
            {
                'lists': {'tag_list': {'join': ', '}},
                'output': 'Define the list {name_text} as consisting of {tag_list}.',
            }
        ],
    },
    {
        'pattern': '(attr_rule "@" . (ident) @root_text)',
        'output': '{root_text} (which cannot be overwritten when copying tags from a chunk)',
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
        'pattern': '(output_rule pos: (ident) @pos_text [(ident) (lit_tag)] @tag_list) @root',
        'output': [{
            'lists': {'tag_list': {'join': ', '}},
            'output': 'When outputting {pos_text}, put the following: {tag_list}.',
        }],
    },
    {
        'pattern': '(output_rule (ident) @root (#eq? @root "_"))',
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
        'pattern': '''
(output_rule
  pos: (ident) @pos_text
  (lu_cond . (choice (always_tok) value: (_) @val) .)
) @root''',
        'output': 'When outputting {pos_text}, put {val}.',
    },
    {
        'pattern': '''
(output_rule pos: (ident) @pos_text (lu_cond (choice) @op_list)) @root
        ''',
        'output': [{
            'lists': {'op_list': {'join': '\n', 'html_type': 'ol'}},
            'output': 'When outputting {pos_text}, use the first applicable rule from:\n{op_list}',
        }],
    },
    {
        'pattern': '(lu_cond (choice cond: (_) @cond value: (_) @val) @root)',
        'output': 'If {cond}, put {val}.',
    },
    {
        'pattern': '(lu_cond (choice (else_tok) value: (_) @val) @root)',
        'output': 'Otherwise, put {val}.',
    },
    {
        'pattern': '(condition . "(" (_) @thing_list ")" .) @root',
        'output': [{
            'lists': {'thing_list': {'join': ' '}},
            'output': '{thing_list}',
        }],
    },
    {
        'pattern': '(and) @root',
        'output': 'and',
    },
    {
        'pattern': '(or) @root',
        'output': 'or',
    },
    {
        'pattern': '(not) @root',
        'output': 'not',
    },
    {
        # TODO: more specific
        'pattern': '(str_op) @root_text',
        'output': '{root_text}',
    },
    {
        'pattern': '(attr_rule (ident) @root_text)',
        'output': '{root_text}',
    },
    {
        'pattern': '(reduce_rule_group . (ident) @pos_text . (arrow) (reduce_rule) @rule_list) @root',
        'output': [{
            'lists': {'rule_list': {'join': '\n', 'html_type': 'ul'}},
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
                'lists': {'pattern_list': {'join': ', ', 'html_type': 'ol'}},
                'output': 'When parsing, match {pattern_list}, and when outputting, put {output}.',
            },
        ],
    },
    {
        'pattern': '(reduce_output . "{" (_) @thing_list "}" .) @root',
        'output': [{
            'lists': {'thing_list': {'join': ', ', 'html_type': 'ol'}},
            'output': '{thing_list}',
        }],
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
            {
                'output': 'a word with part-of-speech {pos_text}',
            },
        ],
    },
    {
        'pattern': '(pattern_element (ident) @root_text)',
        'output': '{root_text}',
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
    {
        'pattern': '(blank) @root',
        'output': 'a space',
    },
    {
        'pattern': '''
(output_element
  (conjoin)? @conjoin
  (insert)? @insert
  (inserted)? @inserted
  (magic)? @magic
  (num) @pos_text
  (macro_name (ident) @macro_text)?
  (output_var_set)? @vars
) @root''',
        'output': multi_option(
            (None, 'the word in position {pos_text}'),
            ('inserted', ', if that position has been created by a parent chunk inserting a word into this chunk'),
            ('macro_text', ', as if it had part-of-speech tag {macro_text}'),
            ('magic', ', with all tag slots which correspond to something on the chunk being filled in by copying'),
            ('conjoin', ', which should be joined to the preceding word'),
            ('insert', ', which should be made a child of the preceding chunk'),
            ('vars', ', with the following tags being overridden: {vars}'),
        ),
    },
    {
        'pattern': '(set_var name: (ident) @name_text value: (_) @val) @root',
        'output': 'set the tag {name_text} to {val}',
    },
    {
        'pattern': '(output_var_set (set_var) @set_list) @root',
        'output': [{
            'lists': {'set_list': {'join': ', '}},
            'output': '{set_list}',
        }],
    },
    {
        'pattern': '(clip val: (ident) @tag_text) @root',
        'output': '{tag_text}',
    },
    {
        'pattern': '''
(clip
  (inserted)? @inserted
  pos: (num) @pos_text
  attr: (ident) @attr_text
  (clip_side)? @side
  convert: (ident)? @conv_text
) @root
        ''',
        'output': multi_option(
            (None, 'the'),
            ('side', ' {side}'),
            (None, ' {attr_text} tag of word {pos_text}'),
            ('inserted', ', if that position has been created by a parent chunk inserting a word into this chunk'),
            ('conv_text', ', using the conversion rules to change it to a {conv_text} tag'),
        ),
    },
]

rules = [Pattern.from_json(RTX, rl) for rl in base_rules]
