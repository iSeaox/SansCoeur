import json
from typing import Any, Dict, List, Union

class GameDataEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        # Ensure indent is preserved for normal formatting
        self.custom_indent = kwargs.get('indent', 4)
        super().__init__(*args, **kwargs)

    def iterencode(self, obj, _one_shot=False):
        """Custom JSON encoder that formats 'reaction_time' arrays without indentation"""
        if isinstance(obj, dict):
            # Process dictionary items
            for chunk in self._iterencode_dict(obj, _one_shot, 0):
                yield chunk
        elif isinstance(obj, list):
            # Process list items
            for chunk in self._iterencode_list(obj, _one_shot, 0):
                yield chunk
        else:
            # Use default encoder for other types
            for chunk in super().iterencode(obj, _one_shot):
                yield chunk

    def _iterencode_dict(self, d, _one_shot, level, in_round_score=False, in_players=False):
        indent = ' ' * (self.custom_indent * level)
        next_indent = ' ' * (self.custom_indent * (level + 1))

        # Check if this dict should be displayed on a single line
        inline_dict = in_round_score or in_players or (level > 0 and any(parent_key in ['round_score', 'players'] for parent_key in getattr(self, '_parent_key_stack', [])))

        if inline_dict:
            yield '{'
            first = True
            for key, value in d.items():
                if not first:
                    yield ', '
                first = False
                yield json.dumps(key)
                yield ': '

                # Special handling for reaction_time arrays even in inline mode
                if key == 'reaction_time' and isinstance(value, list):
                    yield '['
                    if value:
                        for i, item in enumerate(value):
                            if i > 0:
                                yield ','
                            yield json.dumps(item)
                    yield ']'
                elif isinstance(value, dict):
                    # Use a flat display for nested dicts in round_score or players
                    for chunk in self._iterencode_dict(value, _one_shot, level + 1, True, in_players):
                        yield chunk
                elif isinstance(value, list):
                    for chunk in self._iterencode_list(value, _one_shot, level + 1, in_players):
                        yield chunk
                else:
                    yield json.dumps(value, cls=type(self))
            yield '}'
        else:
            yield '{\n'
            first = True
            for key, value in d.items():
                if not first:
                    yield ',\n'
                first = False
                yield next_indent + json.dumps(key)
                yield ': '

                # Special handling for reaction_time arrays
                if key == 'reaction_time' and isinstance(value, list):
                    yield '['
                    if value:
                        for i, item in enumerate(value):
                            if i > 0:
                                yield ','
                            yield json.dumps(item)
                    yield ']'
                # Check if this is the round_score key
                elif key == 'round_score' and isinstance(value, list):
                    # Store the parent key to inform nested dicts
                    old_parent_keys = getattr(self, '_parent_key_stack', [])
                    self._parent_key_stack = old_parent_keys + ['round_score']
                    for chunk in self._iterencode_list(value, _one_shot, level + 1):
                        yield chunk
                    self._parent_key_stack = old_parent_keys
                # Check if this is the players key
                elif key == 'players' and isinstance(value, list):
                    # Store the parent key to inform nested dicts
                    old_parent_keys = getattr(self, '_parent_key_stack', [])
                    self._parent_key_stack = old_parent_keys + ['players']
                    for chunk in self._iterencode_list(value, _one_shot, level + 1, True):
                        yield chunk
                    self._parent_key_stack = old_parent_keys
                elif isinstance(value, dict):
                    for chunk in self._iterencode_dict(value, _one_shot, level + 1):
                        yield chunk
                elif isinstance(value, list):
                    for chunk in self._iterencode_list(value, _one_shot, level + 1):
                        yield chunk
                else:
                    yield json.dumps(value, cls=type(self))
            yield '\n' + indent + '}'

    def _iterencode_list(self, lst, _one_shot, level, in_players=False):
        indent = ' ' * (self.custom_indent * level)
        next_indent = ' ' * (self.custom_indent * (level + 1))

        # Check for simple list of primitives (like score)
        all_primitives = all(isinstance(x, (int, float, str, bool, type(None))) for x in lst)
        # Check if this is a list in round_score or players
        in_round_score = any(parent_key == 'round_score' for parent_key in getattr(self, '_parent_key_stack', []))
        if not in_players:  # Only check for players if not already explicitly set
            in_players = any(parent_key == 'players' for parent_key in getattr(self, '_parent_key_stack', []))

        if all_primitives and len(lst) <= 5:  # Short primitive lists with easier readability
            yield '['
            first = True
            for value in lst:
                if not first:
                    yield ', '
                first = False
                yield json.dumps(value)
            yield ']'
        else:
            yield '[\n'
            first = True
            for value in lst:
                if not first:
                    yield ',\n'
                first = False
                yield next_indent

                if isinstance(value, dict) and (in_round_score or in_players):
                    # Use inline display for dicts in round_score or players
                    for chunk in self._iterencode_dict(value, _one_shot, level + 1, in_round_score, in_players):
                        yield chunk
                elif isinstance(value, dict):
                    for chunk in self._iterencode_dict(value, _one_shot, level + 1):
                        yield chunk
                elif isinstance(value, list):
                    for chunk in self._iterencode_list(value, _one_shot, level + 1, in_players):
                        yield chunk
                else:
                    yield json.dumps(value, cls=type(self))
            yield '\n' + indent + ']'