#!/usr/bin/env python3
"""Restricted readers for eval answer YAML files.

This is intentionally not a general YAML parser. It supports only the root
scalar, root list, root list-of-maps, and one-level nested mapping shapes used
by the repository's eval answer oracles.
"""

from __future__ import annotations

import re


_ROOT_KEY_RE = re.compile(r"^(?P<key>[A-Za-z0-9_-]+)\s*:\s*(?P<value>.*)$")


def _strip_comment(value: str) -> str:
    if " #" in value:
        value = value.split(" #", 1)[0]
    return value.rstrip()


def _yaml_scalar(value: str) -> str:
    value = _strip_comment(value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _find_root_key(lines: list[str], key: str) -> tuple[int, str] | None:
    for index, line in enumerate(lines):
        match = _ROOT_KEY_RE.match(line)
        if match and match.group("key") == key:
            return index, match.group("value").strip()
    return None


def _section_lines(lines: list[str], start_index: int) -> list[str]:
    section: list[str] = []
    for line in lines[start_index + 1 :]:
        if not line.strip() or line.lstrip().startswith("#"):
            section.append(line)
            continue
        if _ROOT_KEY_RE.match(line):
            break
        section.append(line)
    return section


def _inline_list(value: str) -> list[str] | None:
    value = _strip_comment(value).strip()
    if value == "[]":
        return []
    if len(value) >= 2 and value[0] == "[" and value[-1] == "]":
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_yaml_scalar(part) for part in inner.split(",")]
    return None


def scalar_value(text: str, key: str) -> str | None:
    """Return a root scalar value, or None when the key is absent."""
    lines = text.splitlines()
    found = _find_root_key(lines, key)
    if found is None:
        return None
    _, value = found
    return _yaml_scalar(value)


def list_values(text: str, key: str) -> list[str]:
    """Return values from a root YAML list."""
    lines = text.splitlines()
    found = _find_root_key(lines, key)
    if found is None:
        return []
    start_index, inline_value = found
    inline = _inline_list(inline_value)
    if inline is not None:
        return inline
    values: list[str] = []
    for line in _section_lines(lines, start_index):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^\s{2}-\s*(.+?)\s*$", line)
        if match:
            values.append(_yaml_scalar(match.group(1)))
    return values


def list_of_maps(text: str, key: str) -> list[dict[str, str]]:
    """Return simple maps from a root YAML list."""
    lines = text.splitlines()
    found = _find_root_key(lines, key)
    if found is None:
        return []
    start_index, inline_value = found
    inline = _inline_list(inline_value)
    if inline == []:
        return []
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in _section_lines(lines, start_index):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item_match = re.match(r"^\s{2}-\s*(.*)$", line)
        if item_match:
            if current is not None:
                items.append(current)
            current = {}
            rest = item_match.group(1).strip()
            if rest:
                key_value = _parse_key_value(rest)
                if key_value is not None:
                    field, value = key_value
                    current[field] = value
            continue
        field_match = re.match(r"^\s{4}([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if field_match and current is not None:
            current[field_match.group(1)] = _yaml_scalar(field_match.group(2))
    if current is not None:
        items.append(current)
    return items


def nested_keys(text: str, key: str) -> set[str]:
    """Return immediate child keys below a root mapping."""
    lines = text.splitlines()
    found = _find_root_key(lines, key)
    if found is None:
        return set()
    start_index, inline_value = found
    if inline_value.strip() == "{}":
        return set()
    keys: set[str] = set()
    for line in _section_lines(lines, start_index):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^\s{2}([A-Za-z0-9_-]+)\s*:", line)
        if match:
            keys.add(match.group(1))
    return keys


def _parse_key_value(text: str) -> tuple[str, str] | None:
    if ":" not in text:
        return None
    key, value = text.split(":", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
        return None
    return key, _yaml_scalar(value)
