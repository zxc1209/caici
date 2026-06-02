#!/usr/bin/env python3
"""
merge_position.py

Merges position, college, and nationality data from the DeanAnalyst NBA dataset
into the existing players.js file. Only fills in missing/null fields — existing
data is never overwritten.

Data sources:
  - Existing: web/js/players.js (ES module: export default [...])
  - Position: DeanAnalyst/nba-player-analysis PlayerIndex_nba_stats.csv

Outputs:
  - web/js/players.js           (ES module)
  - miniprogram/data/players.js (CommonJS)
"""

import csv
import io
import json
import os
import re
import sys
import collections
import hashlib
import urllib.request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CSV_URL = (
    "https://raw.githubusercontent.com/DeanAnalyst/nba-player-analysis/"
    "main/data/PlayerIndex_nba_stats.csv"
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_OUT = os.path.join(PROJECT_ROOT, "web", "js", "players.js")
MINIPROG_OUT = os.path.join(PROJECT_ROOT, "miniprogram", "data", "players.js")

# ---------------------------------------------------------------------------
# Position mapping: CSV abbreviation → our 5-position code
# ---------------------------------------------------------------------------

POSITION_MAP = {
    "G":   "PG",   # Guard → PG (split PG/SG deterministically later)
    "F":   "SF",   # Forward → SF
    "C":   "C",    # Center → C
    "G-F": "SG",   # Guard-Forward → SG
    "F-C": "PF",   # Forward-Center → PF
    "F-G": "SF",   # Forward-Guard → SF
    "C-F": "PF",   # Center-Forward → PF (closest match)
}

# ---------------------------------------------------------------------------
# Nationality mapping: English → Chinese
# ---------------------------------------------------------------------------

NATIONALITY_MAP = {
    "USA": "美国",
    "United States": "美国",
    "Canada": "加拿大",
    "France": "法国",
    "Germany": "德国",
    "Spain": "西班牙",
    "Italy": "意大利",
    "Australia": "澳大利亚",
    "Serbia": "塞尔维亚",
    "Croatia": "克罗地亚",
    "Greece": "希腊",
    "Lithuania": "立陶宛",
    "Turkey": "土耳其",
    "Brazil": "巴西",
    "Argentina": "阿根廷",
    "Slovenia": "斯洛文尼亚",
    "Nigeria": "尼日利亚",
    "Cameroon": "喀麦隆",
    "Congo": "刚果",
    "Senegal": "塞内加尔",
    "China": "中国",
    "Japan": "日本",
    "South Korea": "韩国",
    "Russia": "俄罗斯",
    "Latvia": "拉脱维亚",
    "Ukraine": "乌克兰",
    "Bosnia": "波黑",
    "Bosnia and Herzegovina": "波黑",
    "Montenegro": "黑山",
    "Switzerland": "瑞士",
    "Belgium": "比利时",
    "Netherlands": "荷兰",
    "Czech Republic": "捷克",
    "Poland": "波兰",
    "Finland": "芬兰",
    "Sweden": "瑞典",
    "Israel": "以色列",
    "South Sudan": "南苏丹",
    "Sudan": "苏丹",
    "Jamaica": "牙买加",
    "Dominican Republic": "多米尼加",
    "Puerto Rico": "波多黎各",
    "Bahamas": "巴哈马",
    "Venezuela": "委内瑞拉",
    "New Zealand": "新西兰",
    "England": "英国",
    "Great Britain": "英国",
    "United Kingdom": "英国",
    "Georgia": "格鲁吉亚",
    "Egypt": "埃及",
    "Tunisia": "突尼斯",
    "Angola": "安哥拉",
    "Mali": "马里",
    "Iran": "伊朗",
    "India": "印度",
    "Philippines": "菲律宾",
    "Mexico": "墨西哥",
    "Panama": "巴拿马",
    "Cuba": "古巴",
    "Trinidad and Tobago": "特立尼达和多巴哥",
    "Guyana": "圭亚那",
    "Uruguay": "乌拉圭",
    "Estonia": "爱沙尼亚",
    "Bulgaria": "保加利亚",
    "Romania": "罗马尼亚",
    "Hungary": "匈牙利",
    "Austria": "奥地利",
    "Iceland": "冰岛",
    "Denmark": "丹麦",
    "Norway": "挪威",
    "Ireland": "爱尔兰",
    "Portugal": "葡萄牙",
    "Macedonia": "北马其顿",
    "Belarus": "白俄罗斯",
    "Slovakia": "斯洛伐克",
    "Congo DR": "刚果民主共和国",
    "DR Congo": "刚果民主共和国",
    "DRC": "刚果民主共和国",
    "Democratic Republic of the Congo": "刚果民主共和国",
    "US Virgin Islands": "美属维尔京群岛",
    "St. Vincent & Grenadines": "圣文森特和格林纳丁斯",
    "Scotland": "苏格兰",
    "Sudan (UK)": "苏丹",
    "Cabo Verde": "佛得角",
    "Saint Lucia": "圣卢西亚",
    "Ghana": "加纳",
    "Guinea": "几内亚",
    "Cape Verde": "佛得角",
    "Gabon": "加蓬",
    "Tanzania": "坦桑尼亚",
    "Kenya": "肯尼亚",
    "Uganda": "乌干达",
    "Liberia": "利比里亚",
    "South Africa": "南非",
    "Zimbabwe": "津巴布韦",
    "Lebanon": "黎巴嫩",
    "Haiti": "海地",
    "Taiwan": "中国台湾",
    "Serbia and Montenegro": "塞尔维亚",
    "Yugoslavia": "南斯拉夫",
    "Czechoslovakia": "捷克斯洛伐克",
    "USSR": "苏联",
    "West Germany": "德国",
    "Virgin Islands": "美属维尔京群岛",
    "U.S. Virgin Islands": "美属维尔京群岛",
    "Antigua and Barbuda": "安提瓜和巴布达",
    "Barbados": "巴巴多斯",
    "Colombia": "哥伦比亚",
    "Peru": "秘鲁",
    "Chile": "智利",
    "Suriname": "苏里南",
    "Nicaragua": "尼加拉瓜",
    "Belize": "伯利兹",
    "Ecuador": "厄瓜多尔",
    "Bolivia": "玻利维亚",
    "Paraguay": "巴拉圭",
    "Saint Vincent and the Grenadines": "圣文森特和格林纳丁斯",
    "Cayman Islands": "开曼群岛",
    "British Virgin Islands": "英属维尔京群岛",
    "Qatar": "卡塔尔",
}

# ---------------------------------------------------------------------------
# Team abbreviation → Chinese team name (top 30+ NBA teams)
# ---------------------------------------------------------------------------

TEAM_NAME_MAP = {
    "ATL": "老鹰",
    "BOS": "凯尔特人",
    "BKN": "篮网",
    "NJN": "篮网",
    "CHA": "黄蜂",
    "CHH": "黄蜂",
    "CHO": "黄蜂",
    "CHI": "公牛",
    "CLE": "骑士",
    "DAL": "独行侠",
    "DEN": "掘金",
    "DET": "活塞",
    "GSW": "勇士",
    "HOU": "火箭",
    "IND": "步行者",
    "LAC": "快船",
    "LAL": "湖人",
    "MEM": "灰熊",
    "VAN": "灰熊",
    "MIA": "热火",
    "MIL": "雄鹿",
    "MIN": "森林狼",
    "NOH": "鹈鹕",
    "NOK": "鹈鹕",
    "NOP": "鹈鹕",
    "NYK": "尼克斯",
    "OKC": "雷霆",
    "SEA": "雷霆",
    "ORL": "魔术",
    "PHI": "76人",
    "PHX": "太阳",
    "POR": "开拓者",
    "SAC": "国王",
    "SAS": "马刺",
    "TOR": "猛龙",
    "UTA": "爵士",
    "WAS": "奇才",
    "WSB": "奇才",
    "SDC": "快船",
    "BUF": "快船",
    "KCK": "国王",
    "KCO": "国王",
    "CIN": "国王",
    "ROC": "国王",
    "STL": "老鹰",
    "MLH": "老鹰",
    "TRI": "老鹰",
    "FTW": "活塞",
    "SYR": "76人",
    "PHW": "勇士",
    "SFW": "勇士",
    "BAL": "奇才",
    "CHP": "奇才",
    "CHZ": "奇才",
    "AND": "奇才",
    "INO": "步行者",
    "KEN": "篮网",
    "LAS": "湖人",
    "MNL": "湖人",
    "MMP": "活塞",
    "MPS": "活塞",
    "NOJ": "爵士",
    "NJA": "篮网",
    "NYN": "篮网",
    "PRO": "凯尔特人",
    "SDR": "火箭",
    "SHE": "活塞",
    "TCB": "活塞",
    "TEX": "马刺",
    "WAT": "活塞",
    "WSC": "奇才",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_suffix(name: str) -> str:
    """Remove common name suffixes like Jr., Sr., III, II, IV."""
    # Remove trailing suffixes
    name = re.sub(r'\s+(jr\.?|sr\.?|iii|ii|iv|v)$', '', name, flags=re.IGNORECASE)
    return name.strip()


def normalize_name(name: str) -> str:
    """Normalize a player name for case-insensitive matching."""
    if not name:
        return ""
    # Lowercase, collapse whitespace, strip punctuation except hyphens and dots
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    return name


def deterministic_pg_sg(name: str) -> str:
    """For 'G' → randomly assign PG or SG deterministically based on name hash."""
    h = hashlib.md5(name.encode()).hexdigest()
    return "PG" if int(h[:8], 16) % 2 == 0 else "SG"


def is_chinese(text: str) -> bool:
    """Check if a string contains Chinese characters."""
    if not text:
        return False
    for ch in text:
        if '一' <= ch <= '鿿':
            return True
    return False


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def load_players(path: str) -> list:
    """Load players array from a JS module file (ESM or CommonJS)."""
    print(f"    Reading: {path}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip module wrapper
    json_str = content.strip()
    if json_str.startswith("export default "):
        json_str = json_str[len("export default "):]
    elif json_str.startswith("module.exports"):
        json_str = json_str.split("=", 1)[1].strip()
    json_str = json_str.rstrip(";").strip()

    players = json.loads(json_str)
    if not isinstance(players, list):
        raise TypeError(f"Expected a JSON array, got {type(players).__name__}")
    return players


def write_players(players: list, path: str, module_type: str = "esm") -> None:
    """Write players array to a JS module file."""
    json_str = json.dumps(players, ensure_ascii=False, indent=2, default=str)

    if module_type == "esm":
        content = f"export default {json_str};\n"
    else:
        content = f"module.exports = {json_str};\n"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"    Wrote {len(players)} players → {path}")


# ---------------------------------------------------------------------------
# CSV fetching and lookup building
# ---------------------------------------------------------------------------

def fetch_csv(url: str) -> list:
    """Download CSV and return list of dict rows."""
    print(f"    Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read()

    # Try UTF-8 with BOM stripping first
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"    Downloaded {len(rows)} rows, columns: {reader.fieldnames}")
    return rows


def map_position(csv_pos: str) -> str | None:
    """Map a CSV position abbreviation to our 5-position code."""
    csv_pos = (csv_pos or "").strip().upper()
    if not csv_pos:
        return None
    # Normalize separator (some use / or space)
    csv_pos = re.sub(r"\s*[/]\s*", "-", csv_pos)
    return POSITION_MAP.get(csv_pos)


def build_csv_lookup(csv_rows: list) -> dict:
    """Build a normalized-name → (position, college, nationality) lookup.

    For players with multiple rows (different teams/seasons), use the most
    common non-empty position, and the last non-empty college/country.
    """
    player_data = collections.defaultdict(lambda: {
        "positions": [],
        "colleges": [],
        "countries": [],
    })

    for r in csv_rows:
        first = (r.get("PLAYER_FIRST_NAME") or "").strip()
        last = (r.get("PLAYER_LAST_NAME") or "").strip()
        if not first and not last:
            continue

        full_name = f"{first} {last}"
        norm = normalize_name(full_name)

        pd = player_data[norm]

        # Position
        csv_pos = r.get("POSITION", "")
        our_pos = map_position(csv_pos)
        if our_pos:
            pd["positions"].append(our_pos)

        # College
        college = (r.get("COLLEGE") or "").strip()
        if college and college.lower() not in ("none", "undrafted", "n/a", ""):
            pd["colleges"].append(college)

        # Country
        country = (r.get("COUNTRY") or "").strip()
        if country and country.lower() not in ("none", "undrafted", "n/a", ""):
            pd["countries"].append(country)

    # --- Build final lookup ---
    lookup = {}
    lookup_no_suffix = {}
    for norm_name, pd in player_data.items():
        # Position: most common
        pos = None
        if pd["positions"]:
            pos_counter = collections.Counter(pd["positions"])
            pos = pos_counter.most_common(1)[0][0]

        # For G → split PG/SG deterministically
        if pos == "PG" and pd["positions"]:
            # Check if the original CSV position was just 'G'
            pos = deterministic_pg_sg(norm_name)

        # College: last (most recent)
        college = pd["colleges"][-1] if pd["colleges"] else None

        # Country → Chinese nationality
        country = pd["countries"][-1] if pd["countries"] else None
        nationality = None
        if country:
            nationality = NATIONALITY_MAP.get(country, country)

        entry = {
            "position": pos,
            "college": college,
            "nationality": nationality,
        }

        lookup[norm_name] = entry

        # Also index by suffix-stripped name (for matching Jr/Sr/III variants)
        stripped = strip_suffix(norm_name)
        if stripped != norm_name and stripped not in lookup:
            lookup_no_suffix[stripped] = entry

    return lookup, lookup_no_suffix


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def match_player(player: dict, lookup: dict, lookup_no_suffix: dict = None) -> tuple:
    """Try to match a player from our dataset to the CSV lookup.

    Returns (position, college, nationality) or (None, None, None).
    """
    if lookup_no_suffix is None:
        lookup_no_suffix = {}

    # Get the name to match on
    name = player.get("name") or player.get("name_en") or ""
    norm = normalize_name(name)
    if not norm:
        return None, None, None

    # Strategy 1: exact normalized match
    if norm in lookup:
        d = lookup[norm]
        return d["position"], d["college"], d["nationality"]

    # Strategy 1b: try no-suffix lookup (for CSV names that had suffixes stripped)
    if norm in lookup_no_suffix:
        d = lookup_no_suffix[norm]
        return d["position"], d["college"], d["nationality"]

    # Strategy 1c: strip suffix from player and try exact match
    norm_no_suffix = strip_suffix(norm)
    if norm_no_suffix != norm:
        if norm_no_suffix in lookup:
            d = lookup[norm_no_suffix]
            return d["position"], d["college"], d["nationality"]
        if norm_no_suffix in lookup_no_suffix:
            d = lookup_no_suffix[norm_no_suffix]
            return d["position"], d["college"], d["nationality"]

    # Strategy 2: last name + first initial (original name)
    parts = norm.split()
    if len(parts) >= 2:
        first_initial = parts[0][0] if parts[0] else ""
        last_name = parts[-1]

        for csv_name, d in lookup.items():
            csv_parts = csv_name.split()
            if len(csv_parts) < 2:
                continue
            csv_first = csv_parts[0]
            csv_last = csv_parts[-1]

            # Match: last names match AND first initial matches
            if csv_last == last_name and csv_first and csv_first[0] == first_initial:
                return d["position"], d["college"], d["nationality"]

            # Also try: last name is a substring (handles hyphenated, suffixes)
            if (csv_last in last_name or last_name in csv_last):
                if csv_first and csv_first[0] == first_initial:
                    return d["position"], d["college"], d["nationality"]

    # Strategy 3: strip suffix from player name, then try last+initial
    if norm_no_suffix != norm:
        parts = norm_no_suffix.split()
        if len(parts) >= 2:
            first_initial = parts[0][0] if parts[0] else ""
            last_name = parts[-1]

            for csv_name, d in lookup.items():
                csv_parts = csv_name.split()
                if len(csv_parts) < 2:
                    continue
                csv_first = csv_parts[0]
                csv_last = csv_parts[-1]

                if csv_last == last_name and csv_first and csv_first[0] == first_initial:
                    return d["position"], d["college"], d["nationality"]

                if (csv_last in last_name or last_name in csv_last):
                    if csv_first and csv_first[0] == first_initial:
                        return d["position"], d["college"], d["nationality"]

    return None, None, None


# ---------------------------------------------------------------------------
# Team name conversion
# ---------------------------------------------------------------------------

def convert_teams(players: list) -> int:
    """Add Chinese team names as a 'teams_cn' field (informational only).
    Returns number of players updated.
    """
    updated = 0
    for p in players:
        teams = p.get("teams", [])
        if not teams:
            continue
        cn_teams = [TEAM_NAME_MAP.get(t.upper(), t) for t in teams]
        if cn_teams != teams:
            # Only add the cn field if there's a difference
            p["teams_cn"] = cn_teams
            updated += 1
    return updated


# ---------------------------------------------------------------------------
# Fix garbled / English nationalities
# ---------------------------------------------------------------------------

def fix_nationalities(players: list) -> int:
    """Replace English nationality strings with Chinese, fix garbled text.
    Returns number of players updated.
    """
    fixed = 0
    for p in players:
        nat = p.get("nationality")
        if nat is None:
            continue
        # If it's already valid Chinese, skip
        if is_chinese(nat):
            continue
        # Try to map from known English values
        mapped = NATIONALITY_MAP.get(nat)
        if mapped:
            p["nationality"] = mapped
            fixed += 1
    return fixed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("NBA Player Position Merger")
    print("=" * 60)

    # ---- 1. Load existing players ----
    print("\n[1] Loading existing players...")
    players = load_players(WEB_OUT)
    total = len(players)
    print(f"    Loaded {total} players")

    # ---- 2. Fetch CSV ----
    print("\n[2] Fetching CSV data from DeanAnalyst...")
    csv_rows = fetch_csv(CSV_URL)

    # ---- 3. Build lookup ----
    print(f"\n[3] Building lookup ({len(csv_rows)} CSV rows)...")
    lookup, lookup_no_suffix = build_csv_lookup(csv_rows)
    print(f"    {len(lookup)} unique players in lookup")
    print(f"    {len(lookup_no_suffix)} suffix-stripped variants")

    # Show some sample lookup entries
    print("    Sample entries:")
    for name in list(lookup.keys())[:5]:
        d = lookup[name]
        print(f"      {name!r} → pos={d['position']}, "
              f"college={d['college']}, nat={d['nationality']}")

    # ---- 4. Merge position/college/nationality ----
    print("\n[4] Merging data...")
    matched = 0
    pos_filled = 0
    college_filled = 0
    nat_filled = 0

    for p in players:
        csv_pos, csv_college, csv_nat = match_player(p, lookup, lookup_no_suffix)

        # Check if this player was found in the CSV (any non-None return value)
        name_match_found = csv_pos is not None or csv_college is not None or csv_nat is not None

        if name_match_found:
            matched += 1

        # Only set position if currently null AND CSV has a position
        if csv_pos is not None:
            if p.get("position") is None:
                p["position"] = csv_pos
                pos_filled += 1

        # Fill college if missing/empty
        if csv_college and not p.get("college"):
            p["college"] = csv_college
            college_filled += 1

        # Fill nationality if missing/empty
        if csv_nat and not p.get("nationality"):
            p["nationality"] = csv_nat
            nat_filled += 1

    # ---- 5. Fix remaining English/garbled nationalities ----
    print("\n[5] Fixing English/garbled nationalities...")
    nat_fixed = fix_nationalities(players)

    # ---- 6. Convert team abbreviations to Chinese ----
    print("\n[6] Converting team abbreviations to Chinese...")
    teams_updated = convert_teams(players)

    # ---- 7. Statistics ----
    still_null_pos = sum(1 for p in players if p.get("position") is None)
    now_have_pos = total - still_null_pos

    pos_counts = collections.Counter(p.get("position") for p in players)

    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(f"{'=' * 60}")
    print(f"Total players:             {total}")
    print(f"Matched in CSV lookup:     {matched}")
    print(f"Position filled (was null): {pos_filled}")
    print(f"Now have position:         {now_have_pos}")
    print(f"Still missing position:    {still_null_pos}")
    print(f"College filled:            {college_filled}")
    print(f"Nationality filled:        {nat_filled}")
    print(f"Nationality fixed (EN→CN): {nat_fixed}")
    print(f"Teams CN added:            {teams_updated}")
    print("---")
    print("Position distribution:")
    for pos, cnt in pos_counts.most_common():
        pct = cnt / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {pos or 'null':>5s}: {cnt:4d} ({pct:5.1f}%) {bar}")

    # ---- 8. Write outputs ----
    print(f"\n[8] Writing outputs...")
    write_players(players, WEB_OUT, "esm")
    write_players(players, MINIPROG_OUT, "cjs")

    # ---- 9. Verify ----
    print(f"\n[9] Verifying outputs...")
    verify1 = load_players(WEB_OUT)
    verify2 = load_players(MINIPROG_OUT)
    assert len(verify1) == len(players), "Web output player count mismatch!"
    assert len(verify2) == len(players), "Miniprogram output player count mismatch!"
    v_still_null = sum(1 for p in verify1 if p.get("position") is None)
    v_have_pos = len(verify1) - v_still_null
    print(f"    Verified: {v_have_pos}/{len(verify1)} players have position")

    print(f"\n{'=' * 60}")
    print("Merge complete!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
