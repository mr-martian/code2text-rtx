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
  name: (ident) @name
  (attr_default src: (ident) @src trg: (_) @trg_text)
  [(ident) (string) (attr_set_insert)] @tag_list
) @root''',
        'output': [
            {
                'lists': {'tag_list': {'join': ', '}},
                'output': 'Define the tag category {name} as consisting of {tag_list}, and if this category is not present, then insert {src} while parsing and replace it with {trg_text} when outputting.',
            }
        ],
    },
    {
        'pattern': '''
(attr_rule
  name: (ident) @name
  [(ident) (string) (attr_set_insert)] @tag_list
) @root''',
        'output': [
            {
                'lists': {'tag_list': {'join': ', '}},
                'output': 'Define the list {name} as consisting of {tag_list}.',
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
        'pattern': '(output_rule pos: (ident) @pos (magic)) @root',
        'output': 'When outputting {pos}, just copy the tags from the input.',
    },
    {
        'pattern': '(output_rule pos: (ident) @pos [(ident) (lit_tag)] @tag_list) @root',
        'output': [{
            'lists': {'tag_list': {'join': ', '}},
            'output': 'When outputting {pos}, put the following: {tag_list}.',
        }],
    },
    {
        'pattern': '(output_rule (ident) @root (#eq? @root "_"))',
        'output': 'the part of speech tag',
    },
    {
        'pattern': '(output_rule (lit_tag (ident) @tag) @root)',
        'output': 'the literal tag {tag}',
    },
    {
        'pattern': '(output_rule pos: (ident) (ident) @root_text)',
        'output': 'the {root_text} tag',
    },
    {
        'pattern': '''
(output_rule
  pos: (ident) @pos
  (lu_cond . (choice (always_tok) value: (_) @val) .)
) @root''',
        'output': 'When outputting {pos}, put {val}.',
    },
    {
        'pattern': '''
(output_rule pos: (ident) @pos (lu_cond (choice) @op_list)) @root
        ''',
        'output': [{
            'lists': {'op_list': {'join': '\n', 'html_type': 'ol'}},
            'output': 'When outputting {pos}, use the first applicable rule from:\n{op_list}',
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
        'pattern': '(str_op (_) @op) @root',
        'output': '{op}',
    },
    {
        # c -> Cl/Caseless, f -> Fold(case)
        'pattern': '((str_op_eq) @root (#match? @root ".*[cCfF].*"))',
        'output': 'equals (ignoring capitalization)',
    },
    {'pattern': '(str_op_eq) @root', 'output': '='},
    {
        # c -> Cl/Caseless, d -> folD(case)
        'pattern': '((str_op_isprefix) @root (#match? @root ".*[cCdD].*"))',
        'output': 'starts with (ignoring capitalization)',
    },
    {'pattern': '(str_op_isprefix) @root', 'output': 'starts with'},
    {
        # c -> Cl/Caseless, d -> folD(case)
        'pattern': '((str_op_hasprefix) @root (#match? @root ".*[cCdD].*"))',
        'output': 'starts with (ignoring capitalization) an element of',
    },
    {
        'pattern': '(str_op_hasprefix) @root',
        'output': 'starts with an element of'
    },
    {
        # c -> Cl/Caseless, l -> foLd(case)
        'pattern': '((str_op_issuffix) @root (#match? @root ".*[cClL].*"))',
        'output': 'ends with (ignoring capitalization)',
    },
    {'pattern': '(str_op_issuffix) @root', 'output': 'ends with'},
    {
        # c -> Cl/Caseless, o -> fOld(case)
        'pattern': '((str_op_hassuffix) @root (#match? @root ".*[cCoO].*"))',
        'output': 'ends with (ignoring capitalization) an element of',
    },
    {'pattern': '(str_op_hassuffix) @root', 'output': 'ends with an element of'},
    {
        # c -> Cl/Caseless, f -> Fold(case)
        'pattern': '((str_op_in) @root (#match? @root ".*[cCfF].*"))',
        'output': 'is (ignoring capitalization) an element of',
    },
    {'pattern': '(str_op_in) @root', 'output': 'is an element of'},
    {
        # l -> cL/caseLess, f -> Fold(case)
        'pattern': '((str_op_contains) @root (#match? @root ".*[lLfF].*"))',
        'output': 'contains (ignoring capitalization)',
    },
    {'pattern': '(str_op_contains) @root', 'output': 'contains'},
    {
        'pattern': '(reduce_rule_group . (ident) @pos . (arrow) (reduce_rule) @rule_list) @root',
        'output': [{
            'lists': {'rule_list': {'join': '\n', 'html_type': 'ul'}},
            'output': '{pos} phrases can be constructed according to the following rules:\n{rule_list}'
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
        'pattern': '''
(pattern_element
  (magic)? @magic
  lemma: [(ident) (string) (attr_set_insert)]? @lemma
  . (ident) @pos
  ("." . [(ident) (attr_set_insert) (string)] @tag_list)?
  (pattern_clip)? @set_list
) @root''',
        'output': multi_option(
            (None, 'a word with'),
            ('lemma', ' {lemma} and'),
            (None, ' part-of-speech tag {pos}'),
            ('tag_list', ' followed by {tag_list}'),
            ('set_list', ', from which copy the tags {set_list}'),
            ('magic', ', from which copy any tag needed by the chunk which is not specified somewhere else'),
            lists={'set_list': {'join': ', '}, 'tag_list': {'join': ', '}},
        ),
    },
    {
        'pattern': '(pattern_element (attr_prefix) . (ident) @root_text)',
        'output': 'a lemma in the list {root_text}',
    },
    {
        'pattern': '(pattern_clip (ident) @attr (clip_side)? @clip) @root',
        'output': [
            {
                'cond': [{'has': 'clip'}],
                'output': '{attr} from the {clip} side',
            },
            {'output': '{attr}'},
        ],
    },
    {
        'pattern': '((clip_side) @root (#eq? @root "/sl"))',
        'output': 'source',
    },
    {
        'pattern': '((clip_side) @root (#eq? @root "/tl"))',
        'output': 'target',
    },
    {
        'pattern': '((clip_side) @root (#eq? @root "/ref"))',
        'output': 'reference',
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
        'pattern': '(retag_rule src_attr: (ident) @src trg_attr: (ident) @trg (attr_pair) @pair_list) @root',
        'output': [{
            'lists': {'pair_list': {'join': ', '}},
            'output': 'To change {src} to {trg}, change: {pair_list}.',
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
  (macro_name (ident) @macro)?
  (output_var_set)? @vars
) @root''',
        'output': multi_option(
            (None, 'the word in position {pos_text}'),
            ('inserted', ', if that position has been created by a parent chunk inserting a word into this chunk'),
            ('macro', ', as if it had part-of-speech tag {macro}'),
            ('magic', ', with all tag slots which correspond to something on the chunk being filled in by copying'),
            ('conjoin', ', which should be joined to the preceding word'),
            ('insert', ', which should be made a child of the preceding chunk'),
            ('vars', ', with the following tags being overridden: {vars}'),
        ),
    },
    {
        'pattern': '(set_var name: (ident) @name value: (_) @val) @root',
        'output': 'set the tag {name} to {val}',
    },
    {
        'pattern': '(output_var_set (set_var) @set_list) @root',
        'output': [{
            'lists': {'set_list': {'join': ', '}},
            'output': '{set_list}',
        }],
    },
    {
        'pattern': '(clip val: (ident) @tag) @root',
        'output': '{tag}',
    },
    {
        'pattern': '''
(clip
  (inserted)? @inserted
  pos: (num) @pos_text
  attr: (ident) @attr
  (clip_side)? @side
  convert: (ident)? @conv
) @root
        ''',
        'output': multi_option(
            (None, 'the'),
            ('side', ' {side}'),
            (None, ' {attr} tag of word {pos_text}'),
            ('inserted', ', if that position has been created by a parent chunk inserting a word into this chunk'),
            ('conv', ', using the conversion rules to change it to a {conv} tag'),
        ),
    },
    {
        'pattern': '(ident) @root_text',
        'output': '{root_text}',
    },
]

rules = [Pattern.from_json(RTX, rl) for rl in base_rules]
