"""Placeholder substitution for agent/judge command templates.

Deliberately uses plain string replacement rather than str.format(): these
templates are user-authored shell commands (agents.yaml/judge.yaml), which
routinely contain literal `{` `}` (jq filters, awk scripts, inline Python
dict/set literals, shell brace expansion). str.format() would misinterpret
those as format fields and raise or substitute garbage.
"""
from __future__ import annotations


def substitute(template: str, **values: str) -> str:
    command = template
    for key, value in values.items():
        command = command.replace("{" + key + "}", value)
    return command
