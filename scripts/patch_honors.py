"""
Patch NBA player honors using:
1. NBA champions by year → cross-reference with player teams for championships
2. Hardcoded MVP winners list
3. Hardcoded Hall of Famers list
4. Estimate all-star from career performance + known data
"""
import json

# ─── NBA Champions by year ───
CHAMPIONS = {
    1947: 'PHI', 1948: 'BAL', 1949: 'MNL', 1950: 'MNL', 1951: 'ROC',
    1952: 'MNL', 1953: 'MNL', 1954: 'MNL', 1955: 'SYR', 1956: 'PHW',
    1957: 'BOS', 1958: 'STL', 1959: 'BOS', 1960: 'BOS', 1961: 'BOS',
    1962: 'BOS', 1963: 'BOS', 1964: 'BOS', 1965: 'BOS', 1966: 'BOS',
    1967: 'PHI', 1968: 'BOS', 1969: 'BOS', 1970: 'NYK', 1971: 'MIL',
    1972: 'LAL', 1973: 'NYK', 1974: 'BOS', 1975: 'GSW', 1976: 'BOS',
    1977: 'POR', 1978: 'WSB', 1979: 'SEA', 1980: 'LAL', 1981: 'BOS',
    1982: 'LAL', 1983: 'PHI', 1984: 'BOS', 1985: 'LAL', 1986: 'BOS',
    1987: 'LAL', 1988: 'LAL', 1989: 'DET', 1990: 'DET', 1991: 'CHI',
    1992: 'CHI', 1993: 'CHI', 1994: 'HOU', 1995: 'HOU', 1996: 'CHI',
    1997: 'CHI', 1998: 'CHI', 1999: 'SAS', 2000: 'LAL', 2001: 'LAL',
    2002: 'LAL', 2003: 'SAS', 2004: 'DET', 2005: 'SAS', 2006: 'MIA',
    2007: 'SAS', 2008: 'BOS', 2009: 'LAL', 2010: 'LAL', 2011: 'DAL',
    2012: 'MIA', 2013: 'MIA', 2014: 'SAS', 2015: 'GSW', 2016: 'CLE',
    2017: 'GSW', 2018: 'GSW', 2019: 'TOR', 2020: 'LAL', 2021: 'MIL',
    2022: 'GSW', 2023: 'DEN', 2024: 'BOS', 2025: 'OKC',
}

# ─── MVP Winners ───
MVP_WINNERS = {
    'bill-russell': 5, 'wilt-chamberlain': 4, 'kareem-abdul-jabbar': 7,
    'moses-malone': 3, 'larry-bird': 3, 'magic-johnson': 3,
    'michael-jordan': 5, 'hakeem-olajuwon': 1, 'charles-barkley': 1,
    'david-robinson': 1, 'karl-malone': 2, 'shaquille-oneal': 1,
    'allen-iverson': 1, 'tim-duncan': 2, 'kevin-garnett': 1,
    'steve-nash': 2, 'dirk-nowitzki': 1, 'kobe-bryant': 1,
    'lebron-james': 4, 'derrick-rose': 1, 'kevin-durant': 1,
    'stephen-curry': 2, 'russell-westbrook': 1, 'james-harden': 1,
    'giannis-antetokounmpo': 2, 'nikola-jokic': 3, 'joel-embiid': 1,
}

# ─── Hall of Fame players ───
HALL_OF_FAME = {
    'kareem-abdul-jabbar', 'michael-jordan', 'magic-johnson', 'larry-bird',
    'wilt-chamberlain', 'bill-russell', 'shaquille-oneal', 'hakeem-olajuwon',
    'kobe-bryant', 'tim-duncan', 'kevin-garnett', 'dirk-nowitzki',
    'charles-barkley', 'david-robinson', 'karl-malone', 'john-stockton',
    'scottie-pippen', 'patrick-ewing', 'clyde-drexler', 'dominique-wilkins',
    'reggie-miller', 'ray-allen', 'allen-iverson', 'jason-kidd',
    'steve-nash', 'gary-payton', 'dennis-rodman', 'dikembe-mutombo',
    'alonzo-mourning', 'yao-ming', 'tracy-mcgrady', 'grant-hill',
    'chris-webber', 'paul-pierce', 'chris-bosh', 'tony-parker',
    'manu-ginobili', 'pau-gasol', 'dwyane-wade', 'dirk-nowitzki',
    'vince-carter', 'ben-wallace', 'robert-parish', 'kevin-mchale',
    'james-worthy', 'isiah-thomas', 'joe-dumars', 'george-gervin',
    'julius-erving', 'moses-malone', 'rick-barry', 'elgin-baylor',
    'jerry-west', 'oscar-robertson', 'bob-cousy', 'dolph-schayes',
    'bill-sharman', 'sam-jones', 'elvin-hayes', 'wes-unseld',
    'dave-cowens', 'nate-archibald', 'pete-maravich', 'bill-walton',
    'bernard-king', 'bob-mcadoo', 'alex-english', 'artis-gilmore',
    'ralph-sampson', 'spencer-haywood',
}

# Team name normalization for matching
TEAM_MAP = {
    'LAL': 'LAL', 'BOS': 'BOS', 'GSW': 'GSW', 'CHI': 'CHI', 'SAS': 'SAS',
    'MIA': 'MIA', 'DET': 'DET', 'HOU': 'HOU', 'CLE': 'CLE', 'DAL': 'DAL',
    'MIL': 'MIL', 'TOR': 'TOR', 'DEN': 'DEN', 'OKC': 'OKC', 'NYK': 'NYK',
    'PHI': 'PHI', 'POR': 'POR', 'SEA': 'SEA', 'OKC': 'SEA',  # Thunder are former Sonics
    'WSB': 'WAS', 'BAL': 'BAL', 'MNL': 'MNL', 'SYR': 'SYR', 'ROC': 'ROC',
    'STL': 'STL', 'PHW': 'PHW', 'NOH': 'NOP', 'NOK': 'NOP',
    'BKN': 'NJN', 'NJN': 'NJN',
}

def count_championships(player):
    """Count championships based on team-year overlap."""
    teams = player.get('teams', [])
    career_start = player.get('career_start', 0)
    career_end = player.get('career_end', 2026)

    count = 0
    end_year = career_end if career_end is not None else 2026
    for year, champ_team in CHAMPIONS.items():
        if year < career_start or year > end_year:
            continue
        for t in teams:
            team_name = (t['team'] if isinstance(t, dict) else t).upper()
            # Normalize team names
            norm = TEAM_MAP.get(team_name, team_name)
            champ_norm = TEAM_MAP.get(champ_team, champ_team)
            if norm == champ_norm:
                count += 1
                break
    return count


def main():
    for path in ['miniprogram/data/players.js', 'web/js/players.js']:
        print(f"\nProcessing: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        prefix = 'module.exports = ' if 'module.exports' in content else 'export default '
        json_str = content[len(prefix):].strip().rstrip(';')
        players = json.loads(json_str)

        mvp_count = 0
        champ_count = 0
        hof_count = 0

        for p in players:
            pid = p['id']
            honors = p.setdefault('honors', {})

            # MVP
            if pid in MVP_WINNERS and honors.get('mvp', 0) == 0:
                honors['mvp'] = MVP_WINNERS[pid]
                mvp_count += 1

            # Hall of Fame
            if pid in HALL_OF_FAME:
                honors['hall_of_fame'] = True
                hof_count += 1

            # Championships from team data
            computed_champs = count_championships(p)
            if computed_champs > honors.get('championships', 0):
                honors['championships'] = computed_champs
                champ_count += 1

        print(f"  MVP updated: {mvp_count}")
        print(f"  Championships updated: {champ_count}")
        print(f"  Hall of Fame updated: {hof_count}")

        new_content = prefix + json.dumps(players, ensure_ascii=False, indent=2) + ';\n'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # Show samples
    print("\n--- Sample honors ---")
    samples = ['LeBron James', 'Stephen Curry', 'Russell Westbrook',
               'Shai Gilgeous-Alexander', 'Chris Paul', 'Kevin Durant',
               'Alex Caruso', 'Tim Duncan', 'Kobe Bryant', 'Dirk Nowitzki']
    for name in samples:
        p = next((x for x in players if x['name_en'] == name), None)
        if p:
            h = p['honors']
            print(f"  {name}: MVP={h['mvp']} Champs={h['championships']} HoF={h['hall_of_fame']}")

if __name__ == '__main__':
    main()
