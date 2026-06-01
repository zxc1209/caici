"""NBA player data validation script. Reads players.json and validates all fields."""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "id", "name", "name_en", "position", "height", "weight",
    "nationality", "college", "draft_year", "draft_pick",
    "career_start", "career_end", "jersey_numbers", "teams",
    "honors", "play_style", "career_stats", "notable_relations",
    "difficulty_tier"
]

HONOR_FIELDS = ["mvp", "championships", "all_star", "all_nba_first", "hall_of_fame"]
STATS_FIELDS = ["ppg", "rpg", "apg"]
TEAM_FIELDS = ["team", "start", "end"]
RELATION_FIELDS = ["player_id", "relation"]
VALID_POSITIONS = {"PG", "SG", "SF", "PF", "C"}
VALID_TIERS = {1, 2, 3}


def validate_player(p):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in p:
            errors.append(f"Missing required field: {field}")
    if errors:
        return errors
    if p["position"] not in VALID_POSITIONS:
        errors.append(f"Invalid position: {p['position']}")
    if not (150 <= p["height"] <= 250):
        errors.append(f"Height out of range: {p['height']}cm")
    if not (60 <= p["weight"] <= 200):
        errors.append(f"Weight out of range: {p['weight']}kg")
    if not (1947 <= p["draft_year"] <= 2026):
        errors.append(f"Draft year out of range: {p['draft_year']}")
    if p["career_end"] is not None and p["career_start"] > p["career_end"]:
        errors.append("Career start after career end")
    for hf in HONOR_FIELDS:
        if hf not in p.get("honors", {}):
            errors.append(f"honors missing field: {hf}")
    for sf in STATS_FIELDS:
        if sf not in p.get("career_stats", {}):
            errors.append(f"career_stats missing field: {sf}")
    for i, t in enumerate(p.get("teams", [])):
        for tf in TEAM_FIELDS:
            if tf not in t:
                errors.append(f"teams[{i}] missing field: {tf}")
    for i, r in enumerate(p.get("notable_relations", [])):
        for rf in RELATION_FIELDS:
            if rf not in r:
                errors.append(f"notable_relations[{i}] missing field: {rf}")
    if p["difficulty_tier"] not in VALID_TIERS:
        errors.append(f"Invalid difficulty_tier: {p['difficulty_tier']}")
    return errors


def validate_all(players):
    all_errors = {}
    ids = set()
    for p in players:
        pid = p.get("id", "<unknown>")
        if p.get("id") in ids:
            all_errors[pid] = [f"Duplicate ID: {p['id']}"]
        ids.add(p.get("id"))
        errs = validate_player(p)
        if errs:
            all_errors[pid] = errs
    # Cross-reference checks
    for p in players:
        pid = p.get("id", "")
        for rel in p.get("notable_relations", []):
            if rel["player_id"] not in ids:
                all_errors.setdefault(pid, []).append(
                    f"notable_relations references unknown player: {rel['player_id']}"
                )
    # Bidirectional teammate check
    for p in players:
        for rel in p.get("notable_relations", []):
            if rel["relation"] == "队友":
                target_id = rel["player_id"]
                target = next((x for x in players if x["id"] == target_id), None)
                if target:
                    has_reverse = any(
                        r["player_id"] == p["id"] and r["relation"] == "队友"
                        for r in target.get("notable_relations", [])
                    )
                    if not has_reverse:
                        all_errors.setdefault(p["id"], []).append(
                            f"Teammate relation not bidirectional: {p['id']} -> {target_id}"
                        )
    return all_errors


def main():
    input_path = Path("miniprogram/data/players.js")
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Strip JS module wrapper: "module.exports = ...;"
    content = content.strip()
    if content.startswith("module.exports"):
        content = content.split("=", 1)[1].strip()
    if content.endswith(";"):
        content = content[:-1].strip()
    players = json.loads(content)
    print(f"Loaded {len(players)} players")
    errors = validate_all(players)
    if errors:
        print(f"\n[ERROR] {len(errors)} player(s) have issues:\n")
        for pid, errs in errors.items():
            print(f"  [{pid}]:")
            for e in errs:
                print(f"    - {e}")
        print(f"\nTotal: {len(errors)} player(s) failed validation")
        sys.exit(1)
    tiers = {1: 0, 2: 0, 3: 0}
    for p in players:
        tiers[p["difficulty_tier"]] += 1
    print(f"\n[OK] All data validated - PASS")
    print(f"  Stars (tier 1): {tiers[1]}")
    print(f"  Known (tier 2): {tiers[2]}")
    print(f"  All   (tier 3): {tiers[3]}")
    print(f"\nData file ready: {input_path}")


if __name__ == "__main__":
    main()
