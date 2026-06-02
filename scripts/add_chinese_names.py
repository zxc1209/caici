#!/usr/bin/env python3
"""
Add Chinese names to all NBA players in players.js.
Uses a comprehensive dictionary-first approach with syllable-based fallback.
"""
import re, json, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_PATH = os.path.join(BASE_DIR, 'web', 'js', 'players.js')
MP_PATH = os.path.join(BASE_DIR, 'miniprogram', 'data', 'players.js')

# ── 1. Load players ──────────────────────────────────────────────
def load_players(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'^(export default|module\.exports)\s*=\s*', '', content.strip())
    content = content.rstrip(';')
    content = re.sub(r',\s*(\]|\})', r'\1', content)
    return json.loads(content), content

# ── 2. Build dictionaries ────────────────────────────────────────
