#!/usr/bin/env python3
"""
fetch_nba_data.py

Downloads the public NBA player dataset and converts it to the players.js format
used by the NBA guessing game.

Data source (tried in order):
  1. KaggleHub  ->  justinas/nba-players-data  (all_seasons.csv)
  2. Direct URL ->  raw.githubusercontent.com  (legacy mirror)
  3. nba_api    ->  stats.nba.com live API      (fallback)

Outputs:
  1. web/js/players.js           (ES module:  export default [...])
  2. miniprogram/data/players.js (CommonJS:   module.exports = [...])
"""

import csv
import io
import json
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CSV_URL = (
    "https://raw.githubusercontent.com/justinas/nba-players-data/master/all_seasons.csv"
)

FALLBACK_URLS = [
    "https://raw.githubusercontent.com/justinas/nba-players-data/refs/heads/master/all_seasons.csv",
]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_OUT = os.path.join(PROJECT_ROOT, "web", "js", "players.js")
MINIPROG_OUT = os.path.join(PROJECT_ROOT, "miniprogram", "data", "players.js")

# Players active in or after this season are considered "still active" (career_end: null)
ACTIVE_CUTOFF_SEASON = 2022

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_id(name: str) -> str:
    """Lower-case, spaces to hyphens, strip non-alphanum/hyphen chars."""
    raw = name.lower().strip()
    raw = re.sub(r"[^a-z0-9\s-]", "", raw)
    raw = re.sub(r"\s+", "-", raw)
    # Collapse multiple hyphens
    raw = re.sub(r"-+", "-", raw)
    return raw.strip("-")


def nationality_from_country(country: str) -> str:
    """Map common country names to Chinese labels. Falls back to the raw string."""
    mapping = {
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
        "Georgia (country)": "格鲁吉亚",
        "Congo DR": "刚果民主共和国",
        "DR Congo": "刚果民主共和国",
        "Cape Verde": "佛得角",
        "Gabon": "加蓬",
        "Tanzania": "坦桑尼亚",
        "Kenya": "肯尼亚",
        "Uganda": "乌干达",
        "Liberia": "利比里亚",
        "South Africa": "南非",
        "Zimbabwe": "津巴布韦",
        "Lebanon": "黎巴嫩",
        "Qatar": "卡塔尔",
        "Taiwan": "中国台湾",
        "Haiti": "海地",
        "Antigua and Barbuda": "安提瓜和巴布达",
        "Barbados": "巴巴多斯",
        "Saint Vincent and the Grenadines": "圣文森特和格林纳丁斯",
        "U.S. Virgin Islands": "美属维尔京群岛",
        "British Virgin Islands": "英属维尔京群岛",
        "Cayman Islands": "开曼群岛",
        "Suriname": "苏里南",
        "Belize": "伯利兹",
        "Nicaragua": "尼加拉瓜",
        "Colombia": "哥伦比亚",
        "Peru": "秘鲁",
        "Ecuador": "厄瓜多尔",
        "Chile": "智利",
        "Bolivia": "玻利维亚",
        "Paraguay": "巴拉圭",
    }
    if country is None:
        return None
    return mapping.get(country.strip(), country.strip())


def classify_tier(avg_ppg: float, num_seasons: int) -> int:
    """Tier 1 (superstar), Tier 2 (notable), Tier 3 (everyone else)."""
    if avg_ppg > 18:
        return 1
    if avg_ppg > 15 and num_seasons >= 8:
        return 1
    if avg_ppg > 10:
        return 2
    if num_seasons >= 5:
        return 2
    return 3


def safe_float(val):
    """Parse a value to float, returning 0.0 on failure."""
    if val is None or val == "":
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_int(val, default=0):
    """Parse a value to int, returning *default* on failure."""
    if val is None or val == "":
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def parse_season_year(season_str: str):
    """Parse '1996-97' -> 1996. Returns None for unparseable values."""
    if not season_str or season_str.strip() == "":
        return None
    s = season_str.strip()
    m = re.match(r"^(\d{4})-\d{2}$", s)
    if m:
        return int(m.group(1))
    # Try bare year
    try:
        return int(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Data source: kagglehub
# ---------------------------------------------------------------------------

def load_csv_via_kagglehub():
    """Download and read the CSV via kagglehub. Returns the text content."""
    try:
        import kagglehub  # type: ignore
    except ImportError:
        print("[!] kagglehub not installed. Install with: pip install kagglehub")
        return None

    try:
        print("[*] Downloading dataset via kagglehub: justinas/nba-players-data")
        dataset_path = kagglehub.dataset_download("justinas/nba-players-data")
        csv_path = os.path.join(dataset_path, "all_seasons.csv")
        print(f"[*] Reading CSV from {csv_path}")
        with open(csv_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        print(f"[!] kagglehub download failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Data source: direct URL
# ---------------------------------------------------------------------------

def load_csv_via_url():
    """Try fetching the CSV from direct URLs. Returns text content or None."""
    import urllib.request

    urls = [CSV_URL] + FALLBACK_URLS
    for u in urls:
        try:
            print(f"[*] Fetching {u}")
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                try:
                    return raw.decode("utf-8")
                except UnicodeDecodeError:
                    return raw.decode("latin-1")
        except Exception as exc:
            print(f"[!] Failed: {exc}")
    return None


# ---------------------------------------------------------------------------
# Data source: nba_api
# ---------------------------------------------------------------------------

def load_data_via_nba_api():
    """Fallback: use the nba_api package to fetch live NBA data.
    Returns a list of per-season row dicts with the same keys as the CSV.
    """
    try:
        from nba_api.stats.static import players as static_players
        from nba_api.stats.endpoints import playercareerstats
        import time
    except ImportError:
        print("[!] nba_api not installed. Install with: pip install nba_api")
        return None

    print("[*] Fetching player list via nba_api...")
    nba_players = static_players.get_players()
    print(f"[*] Found {len(nba_players)} players in database")

    rows = []

    for i, p in enumerate(nba_players):
        pid = p["id"]
        name = p["full_name"]
        active = p.get("is_active", False)

        if (i + 1) % 200 == 0:
            print(f"    ... processed {i + 1}/{len(nba_players)} players")

        # Rate-limit: small delay to avoid throttling
        if i > 0 and i % 30 == 0:
            time.sleep(1)

        try:
            career = playercareerstats.PlayerCareerStats(player_id=pid, timeout=15)
            career_df = career.get_data_frames()[0]
        except Exception:
            # Many old/obscure players have no career stats
            continue

        if career_df is None or career_df.empty:
            continue

        for _, r in career_df.iterrows():
            row = {
                "player_name": name,
                "team_abbreviation": r.get("TEAM_ABBREVIATION", ""),
                "age": r.get("PLAYER_AGE", ""),
                "player_height": "",   # Not in career stats
                "player_weight": "",   # Not in career stats
                "college": "",         # Not in career stats
                "country": "",         # Not in career stats
                "draft_year": "",      # Not in career stats
                "draft_round": "",     # Not in career stats
                "draft_number": "",     # Not in career stats
                "gp": r.get("GP", 0),
                "pts": r.get("PTS", 0),
                "reb": r.get("REB", 0),
                "ast": r.get("AST", 0),
                "net_rating": "",      # Not in career stats
                "season": r.get("SEASON_ID", ""),  # e.g. "2023-24"
            }
            rows.append(row)

    print(f"[*] Fetched {len(rows)} player-season rows via nba_api")
    return rows


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_csv_text(csv_text: str):
    """Parse CSV text into a list of per-player aggregated dicts."""
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    print(f"[*] Parsed {len(rows)} rows from CSV")
    print(f"[*] Columns: {reader.fieldnames}")

    # Group by player_name (case-insensitive)
    player_rows: dict[str, list[dict]] = defaultdict(list)

    for row in rows:
        pname = (row.get("player_name") or "").strip()
        if not pname:
            continue
        player_rows[pname.lower()].append(row)

    print(f"[*] Unique players (by name): {len(player_rows)}")

    return aggregate_players(player_rows)


def process_nba_api_rows(rows):
    """Process rows from nba_api into per-player aggregated dicts."""
    print(f"[*] Processing {len(rows)} nba_api rows")

    player_rows: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        pname = (r.get("player_name") or "").strip()
        if not pname:
            continue
        player_rows[pname.lower()].append(r)

    print(f"[*] Unique players (by name): {len(player_rows)}")
    return aggregate_players(player_rows)


def aggregate_players(player_rows):
    """Given rows grouped by player name (lower), return list of player dicts."""
    players = []

    for lower_name, season_rows in player_rows.items():
        if not season_rows:
            continue

        canonical_name = season_rows[0].get("player_name", "").strip()

        # --- name_en ---
        name_en = canonical_name

        # --- id ---
        pid = make_id(canonical_name)

        # --- Collect per-season values ---
        seasons = []
        heights = []
        weights = []
        colleges = []
        countries = []
        draft_years = []
        draft_numbers = []
        teams_set = set()
        pts_list = []
        reb_list = []
        ast_list = []

        for r in season_rows:
            # Season
            season_raw = r.get("season", "")
            sy = parse_season_year(season_raw)
            if sy is not None and sy > 1900:
                seasons.append(sy)

            # Height
            ht = r.get("player_height")
            if ht is not None and ht != "":
                try:
                    h = float(ht)
                    if h < 10:          # assume metres
                        h = h * 100
                    heights.append(h)
                except (ValueError, TypeError):
                    pass

            # Weight
            wt = r.get("player_weight")
            if wt is not None and wt != "":
                try:
                    w = float(wt)
                    if w < 20:           # unlikely weight in kg → assume error
                        w = w * 100      # actually this might be wrong, just keep
                    weights.append(w)
                except (ValueError, TypeError):
                    pass

            # College
            col = (r.get("college") or "").strip()
            if col and col.lower() not in ("none", "undrafted", ""):
                # Avoid accumulating "None" string
                colleges.append(col)

            # Country
            cty = (r.get("country") or "").strip()
            if cty and cty.lower() not in ("none", "undrafted", ""):
                countries.append(cty)

            # Draft year
            dy = r.get("draft_year")
            if dy and str(dy).strip().lower() not in ("", "undrafted", "none"):
                try:
                    val = int(float(str(dy).strip()))
                    if 1940 < val < 2030:
                        draft_years.append(val)
                except (ValueError, TypeError):
                    pass

            # Draft number
            dn = r.get("draft_number")
            if dn and str(dn).strip().lower() not in ("", "undrafted", "none"):
                try:
                    draft_numbers.append(int(float(str(dn).strip())))
                except (ValueError, TypeError):
                    pass

            # Team
            team = (r.get("team_abbreviation") or "").strip()
            if team and team.lower() not in ("none", ""):
                teams_set.add(team.upper())

            # Stats
            pts_list.append(safe_float(r.get("pts")))
            reb_list.append(safe_float(r.get("reb")))
            ast_list.append(safe_float(r.get("ast")))

        # --- height: last available ---
        height = round(heights[-1]) if heights else None

        # --- weight: last available ---
        weight = round(weights[-1]) if weights else None

        # --- college ---
        # Take last non-empty college (most recent)
        college = colleges[-1] if colleges else None
        if college and college.strip() == "":
            college = None

        # --- nationality ---
        cntry = countries[-1] if countries else None
        nationality = nationality_from_country(cntry) if cntry else None

        # --- draft_year ---
        draft_year = draft_years[0] if draft_years else None

        # --- draft_pick ---
        draft_pick = draft_numbers[0] if draft_numbers else None

        # --- career_start / career_end ---
        valid_seasons = sorted(set(s for s in seasons if s > 0))
        career_start = valid_seasons[0] if valid_seasons else None
        max_season = valid_seasons[-1] if valid_seasons else None

        if max_season is not None and max_season >= ACTIVE_CUTOFF_SEASON:
            career_end = None
        else:
            career_end = max_season

        # --- teams ---
        teams = sorted(teams_set)

        # --- honors: all default (not available in this dataset) ---
        honors = {
            "mvp": 0,
            "championships": 0,
            "all_star": 0,
            "all_nba_first": 0,
            "hall_of_fame": False,
        }

        # --- play_style: null (not available) ---
        play_style = None

        # --- career_stats: average across all seasons ---
        avg_pts = round(sum(pts_list) / len(pts_list), 1) if pts_list else 0.0
        avg_reb = round(sum(reb_list) / len(reb_list), 1) if reb_list else 0.0
        avg_ast = round(sum(ast_list) / len(ast_list), 1) if ast_list else 0.0
        career_stats = {"ppg": avg_pts, "rpg": avg_reb, "apg": avg_ast}

        # --- notable_relations: empty (not available) ---
        notable_relations = []

        # --- jersey_numbers: empty (not available) ---
        jersey_numbers = []

        # --- difficulty_tier ---
        num_seasons = len(valid_seasons)
        difficulty_tier = classify_tier(avg_pts, num_seasons)

        player = {
            "id": pid,
            "name": name_en,
            "name_en": name_en,
            "position": None,
            "height": height,
            "weight": weight,
            "nationality": nationality,
            "college": college,
            "draft_year": draft_year,
            "draft_pick": draft_pick,
            "career_start": career_start,
            "career_end": career_end,
            "jersey_numbers": jersey_numbers,
            "teams": teams,
            "honors": honors,
            "play_style": play_style,
            "career_stats": career_stats,
            "notable_relations": notable_relations,
            "difficulty_tier": difficulty_tier,
        }

        players.append(player)

    # Deduplicate by id
    seen_ids = set()
    deduped = []
    for p in players:
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"])
            deduped.append(p)

    print(f"[*] After dedup: {len(deduped)} players")
    return deduped


def write_output(players):
    """Write players to both output files."""
    esm_json = json.dumps(players, ensure_ascii=False, indent=2, default=str)
    esm_content = f"export default {esm_json};\n"
    cjs_content = f"module.exports = {esm_json};\n"

    os.makedirs(os.path.dirname(WEB_OUT), exist_ok=True)
    with open(WEB_OUT, "w", encoding="utf-8") as f:
        f.write(esm_content)
    print(f"[*] Wrote {len(players)} players to {WEB_OUT}")

    os.makedirs(os.path.dirname(MINIPROG_OUT), exist_ok=True)
    with open(MINIPROG_OUT, "w", encoding="utf-8") as f:
        f.write(cjs_content)
    print(f"[*] Wrote {len(players)} players to {MINIPROG_OUT}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("NBA Player Data Fetcher")
    print("=" * 60)

    players = None

    # --- Strategy 1: kagglehub (most reliable) ---
    print("\n--- Trying kagglehub ---")
    csv_text = load_csv_via_kagglehub()
    if csv_text is not None:
        players = process_csv_text(csv_text)

    # --- Strategy 2: direct URL ---
    if players is None:
        print("\n--- Trying direct URL ---")
        csv_text = load_csv_via_url()
        if csv_text is not None:
            players = process_csv_text(csv_text)

    # --- Strategy 3: nba_api ---
    if players is None:
        print("\n--- Trying nba_api ---")
        nba_rows = load_data_via_nba_api()
        if nba_rows is not None:
            players = process_nba_api_rows(nba_rows)

    if players is None or len(players) == 0:
        print("[!] All data sources failed. No players generated.")
        sys.exit(1)

    # --- Statistics ---
    tier_counts = defaultdict(int)
    for p in players:
        tier_counts[p["difficulty_tier"]] += 1

    # Count how many have each field populated
    with_college = sum(1 for p in players if p["college"])
    with_draft = sum(1 for p in players if p["draft_year"])
    with_height = sum(1 for p in players if p["height"])
    with_nat = sum(1 for p in players if p["nationality"])
    with_teams = sum(1 for p in players if p["teams"])

    print(f"\n{'='*60}")
    print(f"STATISTICS")
    print(f"{'='*60}")
    print(f"Total players:       {len(players)}")
    print(f"Tier 1 (球星):       {tier_counts.get(1, 0)}")
    print(f"Tier 2 (知名):       {tier_counts.get(2, 0)}")
    print(f"Tier 3 (全部):       {tier_counts.get(3, 0)}")
    print(f"---")
    print(f"With college:        {with_college}")
    print(f"With draft info:     {with_draft}")
    print(f"With height/weight:  {with_height}")
    print(f"With nationality:    {with_nat}")
    print(f"With teams:          {with_teams}")
    print(f"{'='*60}")

    # --- Write outputs ---
    write_output(players)

    print("\nDone.")


if __name__ == "__main__":
    main()
