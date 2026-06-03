"""
Phonetic transliteration fallback for NBA player names.
Maps English syllables to Chinese characters for names not covered by the dictionary.
"""
import json, re

# ─── Phoneme-to-Chinese mapping ───
# Covers common English consonant+vowel combinations
PHONEME_MAP = {
    # Single consonants
    'b': '布', 'c': '克', 'd': '德', 'f': '弗', 'g': '格',
    'h': '赫', 'j': '杰', 'k': '克', 'l': '尔', 'm': '姆',
    'n': '恩', 'p': '普', 'q': '奎', 'r': '尔', 's': '斯',
    't': '特', 'v': '维', 'w': '沃', 'x': '克斯', 'z': '兹',
    # Single vowels
    'a': '阿', 'e': '埃', 'i': '伊', 'o': '奥', 'u': '乌',
    # Vowel-consonant pairs (critical for word endings)
    'ab': '布', 'ac': '克', 'ad': '德', 'af': '夫', 'ag': '格',
    'ah': '赫', 'ak': '克', 'al': '尔', 'am': '姆', 'an': '恩',
    'ap': '普', 'ar': '尔', 'as': '斯', 'at': '特', 'av': '夫',
    'aw': '奥', 'ax': '克斯', 'ay': '伊', 'az': '兹',
    'eb': '布', 'ec': '克', 'ed': '德', 'ef': '夫', 'eg': '格',
    'eh': '赫', 'ek': '克', 'el': '尔', 'em': '姆', 'en': '恩',
    'ep': '普', 'er': '尔', 'es': '斯', 'et': '特', 'ev': '夫',
    'ew': '尤', 'ex': '克斯', 'ey': '伊', 'ez': '兹',
    'ib': '布', 'ic': '克', 'id': '德', 'if': '夫', 'ig': '格',
    'ih': '赫', 'ik': '克', 'il': '尔', 'im': '姆', 'in': '因',
    'ip': '普', 'ir': '尔', 'is': '斯', 'it': '特', 'iv': '夫',
    'iw': '尤', 'ix': '克斯', 'iy': '伊', 'iz': '兹',
    'ob': '布', 'oc': '克', 'od': '德', 'of': '夫', 'og': '格',
    'oh': '赫', 'ok': '克', 'ol': '尔', 'om': '姆', 'on': '昂',
    'op': '普', 'or': '尔', 'os': '斯', 'ot': '特', 'ov': '夫',
    'ow': '奥', 'ox': '克斯', 'oy': '伊', 'oz': '兹',
    'ub': '布', 'uc': '克', 'ud': '德', 'uf': '夫', 'ug': '格',
    'uh': '赫', 'uk': '克', 'ul': '尔', 'um': '姆', 'un': '恩',
    'up': '普', 'ur': '尔', 'us': '斯', 'ut': '特', 'uv': '夫',
    'uw': '尤', 'ux': '克斯', 'uy': '伊', 'uz': '兹',
    # Syllables - a
    'ba': '巴', 'be': '贝', 'bi': '比', 'bo': '博', 'br': '布',
    'bu': '布', 'by': '拜',
    # Syllables - c/k
    'ca': '卡', 'ce': '塞', 'ch': '奇', 'ci': '西', 'ck': '克',
    'cl': '克', 'co': '科', 'cr': '克', 'cu': '库', 'cy': '赛',
    # Syllables - d
    'da': '达', 'de': '德', 'di': '迪', 'do': '多', 'dr': '德',
    'du': '杜', 'dy': '迪',
    # Syllables - f
    'fa': '法', 'fe': '费', 'fi': '菲', 'fl': '弗', 'fo': '福',
    'fr': '弗', 'fu': '富',
    # Syllables - g
    'ga': '加', 'ge': '杰', 'gh': '格', 'gi': '吉', 'gl': '格',
    'go': '戈', 'gr': '格', 'gu': '古', 'gy': '吉',
    # Syllables - h
    'ha': '哈', 'he': '赫', 'hi': '希', 'ho': '霍', 'hu': '胡',
    'hy': '海',
    # Syllables - j
    'ja': '贾', 'je': '杰', 'ji': '吉', 'jo': '乔', 'ju': '朱',
    # Syllables - k
    'ka': '卡', 'ke': '凯', 'kh': '克', 'ki': '基', 'kl': '克',
    'kn': '恩', 'ko': '科', 'kr': '克', 'ku': '库', 'ky': '凯',
    # Syllables - l
    'la': '拉', 'le': '勒', 'li': '利', 'll': '尔', 'lo': '洛',
    'lu': '卢', 'ly': '利',
    # Syllables - m
    'ma': '马', 'mc': '麦克', 'me': '梅', 'mi': '米', 'mo': '莫',
    'mu': '穆', 'my': '迈',
    # Syllables - n
    'na': '纳', 'ne': '内', 'ni': '尼', 'no': '诺', 'nu': '努',
    'ny': '尼',
    # Syllables - p
    'pa': '帕', 'pe': '佩', 'ph': '菲', 'pi': '皮', 'pl': '普',
    'po': '波', 'pr': '普', 'pu': '普',
    # Syllables - r
    'ra': '拉', 're': '雷', 'rh': '尔', 'ri': '里', 'ro': '罗',
    'ru': '鲁', 'ry': '里',
    # Syllables - s
    'sa': '萨', 'sc': '斯', 'se': '塞', 'sh': '什', 'si': '西',
    'sk': '斯克', 'sl': '斯', 'sm': '斯', 'sn': '斯', 'so': '索',
    'sp': '斯', 'sq': '斯', 'st': '斯特', 'su': '苏', 'sw': '斯',
    'sy': '西',
    # Syllables - t
    'ta': '塔', 'te': '特', 'th': '斯', 'ti': '蒂', 'to': '托',
    'tr': '特', 'tu': '图', 'ty': '蒂',
    # Syllables - v
    'va': '瓦', 've': '维', 'vi': '维', 'vo': '沃', 'vu': '武',
    # Syllables - w
    'wa': '瓦', 'we': '韦', 'wh': '惠', 'wi': '威', 'wo': '沃',
    'wr': '尔', 'wu': '吴',
    # Syllables - y
    'ya': '亚', 'ye': '耶', 'yi': '伊', 'yo': '约', 'yu': '尤',
    # Syllables - z
    'za': '扎', 'ze': '泽', 'zi': '齐', 'zo': '佐', 'zu': '祖',
    # Common endings
    'son': '森', 'ton': '顿', 'man': '曼', 'land': '兰',
    'ford': '福德', 'wood': '伍德', 'berg': '伯格', 'ley': '利',
    'ville': '维尔', 'ster': '斯特', 'ers': '尔斯', 'ing': '英',
    'ell': '尔', 'ett': '特', 'ick': '克', 'ard': '德',
    'age': '奇', 'ain': '恩', 'air': '尔', 'ake': '克',
    'ale': '尔', 'all': '尔', 'and': '德', 'ane': '恩',
    'ang': '格', 'ank': '克', 'ant': '特', 'ard': '德',
    'ark': '克', 'art': '特', 'ash': '什', 'ast': '斯特',
    'att': '特', 'aun': '昂', 'aut': '特', 'awn': '恩',
    'axe': '克斯', 'ay': '伊', 'aye': '耶', 'ayn': '恩',
    'aze': '兹', 'ean': '安', 'ear': '尔', 'eas': '斯',
    'eck': '克', 'ede': '德', 'eed': '德', 'eek': '克',
    'eel': '尔', 'een': '恩', 'eer': '尔', 'eet': '特',
    'ein': '因', 'eld': '德', 'ele': '尔', 'ell': '尔',
    'elm': '姆', 'els': '斯', 'elt': '特', 'ely': '利',
    'eme': '姆', 'ena': '纳', 'end': '德', 'ene': '尼',
    'enk': '克', 'ens': '斯', 'ent': '特', 'enz': '兹',
    'eon': '昂', 'ere': '尔', 'eri': '里', 'erk': '克',
    'ern': '恩', 'ero': '罗', 'ers': '斯', 'ert': '特',
    'ery': '里', 'ess': '斯', 'est': '斯特', 'eta': '塔',
    'ete': '特', 'eth': '斯', 'ett': '特', 'ety': '蒂',
    'eux': '厄', 'eve': '夫', 'ew': '尤', 'ewe': '尤',
    'eyn': '恩', 'ice': '斯', 'ich': '奇', 'ick': '克',
    'ide': '德', 'ier': '尔', 'iew': '尤', 'ife': '夫',
    'iff': '夫', 'ift': '特', 'ige': '奇', 'igh': '伊',
    'ign': '因', 'ike': '克', 'ile': '尔', 'ill': '尔',
    'ilt': '特', 'ime': '姆', 'imm': '姆', 'imp': '普',
    'ims': '姆斯', 'ina': '纳', 'ind': '德', 'ine': '因',
    'ing': '英', 'ink': '克', 'ins': '斯', 'int': '特',
    'ion': '昂', 'ior': '尔', 'ipe': '普', 'ire': '尔',
    'irk': '克', 'irl': '尔', 'irm': '姆', 'irn': '恩',
    'irt': '特', 'ise': '斯', 'ish': '什', 'isk': '斯克',
    'iss': '斯', 'ist': '斯特', 'ite': '特', 'ith': '斯',
    'itt': '特', 'itz': '兹', 'ium': '厄姆', 'ius': '厄斯',
    'ive': '夫', 'ize': '兹', 'oan': '安', 'ock': '克',
    'odd': '德', 'ode': '德', 'off': '夫', 'oft': '特',
    'ohn': '恩', 'oic': '克', 'oig': '格', 'oil': '尔',
    'oin': '因', 'oir': '尔', 'oit': '特', 'oke': '克',
    'old': '德', 'ole': '尔', 'olf': '夫', 'olk': '克',
    'oll': '尔', 'olm': '姆', 'olt': '特', 'oly': '利',
    'omb': '姆', 'ome': '姆', 'omm': '姆', 'omp': '普',
    'oms': '姆斯', 'ond': '德', 'one': '恩', 'ong': '昂',
    'onk': '克', 'ons': '斯', 'ont': '特', 'ood': '德',
    'oof': '夫', 'ook': '克', 'ool': '尔', 'oon': '恩',
    'oor': '尔', 'oot': '特', 'ope': '普', 'opp': '普',
    'ops': '普斯', 'ord': '德', 'ore': '尔', 'orf': '夫',
    'org': '格', 'ork': '克', 'orm': '姆', 'orn': '恩',
    'orr': '尔', 'ors': '斯', 'ort': '特', 'ory': '里',
    'ose': '斯', 'osh': '什', 'osk': '斯克', 'oss': '斯',
    'ost': '斯特', 'oth': '斯', 'ott': '特', 'oud': '德',
    'ough': '夫', 'oul': '尔', 'ound': '德', 'oup': '普',
    'our': '尔', 'ous': '斯', 'out': '特', 'ove': '夫',
    'ow': '奥', 'owe': '奥', 'owl': '尔', 'own': '恩',
    'ows': '斯', 'oyd': '德', 'oyl': '尔', 'oys': '斯',
    'uce': '斯', 'uch': '奇', 'uck': '克', 'ude': '德',
    'uff': '夫', 'uge': '奇', 'ugh': '夫', 'uhr': '尔',
    'uig': '格', 'uil': '尔', 'uin': '因', 'uir': '尔',
    'uit': '特', 'uke': '克', 'ule': '尔', 'ull': '尔',
    'ult': '特', 'uly': '利', 'umb': '姆', 'umm': '姆',
    'ump': '普', 'ums': '姆斯', 'und': '德', 'ung': '昂',
    'unk': '克', 'unn': '恩', 'uns': '斯', 'unt': '特',
    'upe': '普', 'upp': '普', 'ups': '普斯', 'urb': '布',
    'urd': '德', 'ure': '尔', 'urf': '夫', 'urg': '格',
    'urk': '克', 'url': '尔', 'urn': '恩', 'urr': '尔',
    'urs': '斯', 'urt': '特', 'ury': '里', 'use': '斯',
    'ush': '什', 'usk': '斯克', 'uss': '斯', 'ust': '斯特',
    'ute': '特', 'uth': '斯', 'utt': '特', 'utz': '兹',
    'yce': '斯', 'ych': '奇', 'yck': '克', 'yer': '耶',
    'yle': '尔', 'yme': '姆', 'yne': '因', 'ype': '普',
    'yre': '尔', 'yth': '斯', 'yze': '兹',
    # Missing consonant clusters for fallback
    'yl': '伊尔', 'yr': '尔', 'yw': '尤',
    'ng': '恩格', 'nk': '恩克', 'nt': '恩特', 'nd': '恩德',
    'ns': '恩斯', 'nz': '恩兹',
    # Common name endings
    'son': '森', 'ton': '顿', 'don': '登', 'mon': '蒙',
    'lan': '兰', 'den': '登', 'len': '伦', 'ren': '伦',
    'sen': '森', 'ven': '文', 'men': '门', 'ken': '肯',
    'ron': '龙', 'lon': '隆', 'bon': '邦', 'con': '康',
    'ley': '利', 'ney': '尼', 'rey': '雷', 'lin': '林',
    'min': '明', 'win': '温', 'vin': '文', 'kin': '金',
    'gin': '金', 'tin': '廷', 'din': '丁', 'rin': '林',
    'sin': '辛', 'fin': '芬', 'pin': '平',
    'row': '罗', 'low': '洛', 'tow': '托', 'now': '诺',
    'bow': '鲍', 'cow': '考', 'dow': '道', 'how': '豪',
    'mor': '莫尔', 'dor': '多尔', 'for': '福尔', 'gor': '戈尔',
    'nor': '诺尔', 'tor': '托尔', 'cor': '科尔', 'por': '波尔',
    'ld': '尔德', 'lt': '尔特', 'lf': '尔夫', 'lk': '尔克',
    'lm': '尔姆', 'ln': '尔恩', 'lp': '尔普', 'rl': '尔',
    'rm': '姆', 'rn': '恩', 'rp': '普', 'rt': '特', 'rd': '德',
}

def phonetic_transliterate(word):
    """Convert an English word to Chinese using phonetic mapping."""
    word = word.lower().strip()
    if not word:
        return word

    # Handle special prefixes
    # Mc/Mac prefix
    if word.startswith('mc') and len(word) > 3:
        rest = phonetic_transliterate(word[2:])
        return '麦克' + (rest[1:] if rest.startswith('克') else rest)

    # O' prefix
    if word.startswith("o'") and len(word) > 2:
        return '奥' + phonetic_transliterate(word[2:])

    # Try to find longest matching syllable
    # Start with longest possible match (4 chars)
    for length in range(min(4, len(word)), 0, -1):
        chunk = word[:length]
        if chunk in PHONEME_MAP:
            result = PHONEME_MAP[chunk]
            rest = word[length:]
            if rest:
                next_result = phonetic_transliterate(rest)
                # Avoid duplicate consecutive characters
                if result[-1] == next_result[0] if next_result else False:
                    result += next_result[1:]
                else:
                    result += next_result
            return result

    # No match found for any chunk, try single character
    ALPHABET_FALLBACK = {'a':'阿','b':'布','c':'克','d':'德','e':'埃','f':'弗',
        'g':'格','h':'赫','i':'伊','j':'杰','k':'克','l':'勒','m':'姆',
        'n':'恩','o':'奥','p':'普','q':'奎','r':'尔','s':'斯','t':'特',
        'u':'乌','v':'维','w':'沃','x':'斯','y':'伊','z':'兹'}
    if len(word) == 1:
        return ALPHABET_FALLBACK.get(word, word)

    # Fallback: translate first char and recurse
    first = word[0]
    if first in PHONEME_MAP:
        return PHONEME_MAP[first] + phonetic_transliterate(word[1:])

    # Last resort: try single char from alphabet
    ALPHABET_FALLBACK = {'a':'阿','b':'布','c':'克','d':'德','e':'埃','f':'弗',
        'g':'格','h':'赫','i':'伊','j':'杰','k':'克','l':'勒','m':'姆',
        'n':'恩','o':'奥','p':'普','q':'奎','r':'尔','s':'斯','t':'特',
        'u':'乌','v':'维','w':'沃','x':'斯','y':'伊','z':'兹'}
    if first in ALPHABET_FALLBACK:
        return ALPHABET_FALLBACK[first] + phonetic_transliterate(word[1:])

    # Absolute last resort: return original
    return word


def translate_name(name_en):
    """Full name translation: dictionary first, then phonetic fallback."""
    parts = name_en.strip().split()
    if not parts:
        return name_en

    # Use existing dictionary logic from add_cn_names.py
    FIRST_CN = {}  # Will be imported from add_cn_names
    LAST_CN = {}

    first = parts[0].lower().rstrip(',.')
    last = parts[-1].lower().rstrip(',.')

    # Try dictionary first (from add_cn_names.py import)
    # For now, just use phonetic for everything missing
    fn_cn = phonetic_transliterate(first)
    ln_cn = phonetic_transliterate(last)

    return f"{fn_cn}·{ln_cn}"


def fix_half_translated(players):
    """Only fix name parts that still have English letters. Preserve existing CN translations."""
    fixed = 0
    for p in players:
        name = p.get('name', '')
        name_en = p.get('name_en', '')

        if not re.search(r'[a-zA-Z]', name):
            continue

        # Split current name by ·
        cn_parts = name.split('·')
        en_parts = [part.strip().lower() for part in name_en.split()]

        # Clean en_parts: remove dots and apostrophes
        en_parts_clean = [re.sub(r"[.']", '', p) for p in en_parts]

        new_parts = []
        for i, (cn, en) in enumerate(zip(cn_parts, en_parts_clean)):
            if re.search(r'[a-zA-Z]', cn):
                # This part still has English → re-translate
                new_parts.append(phonetic_transliterate(en))
            else:
                # Already translated → keep
                new_parts.append(cn)

        # Handle extra en parts (middle names etc)
        if len(en_parts_clean) > len(cn_parts):
            for en in en_parts_clean[len(cn_parts):]:
                new_parts.append(phonetic_transliterate(en))

        p['name'] = '·'.join(new_parts)
        fixed += 1

    return fixed


def main():
    paths = [
        'web/js/players.js',
        'miniprogram/data/players.js',
    ]

    for path in paths:
        print(f"\nProcessing: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('export default '):
            json_str = content[len('export default '):].strip().rstrip(';')
        elif content.startswith('module.exports = '):
            json_str = content[len('module.exports = '):].strip().rstrip(';')
        else:
            print(f"  Unknown format")
            continue

        players = json.loads(json_str)
        print(f"  Loaded {len(players)} players")

        fixed = fix_half_translated(players)
        print(f"  Fixed {fixed} half-translated names")

        # Count fully translated
        full_cn = sum(1 for p in players if not re.search(r'[a-zA-Z]{3,}', p.get('name', '')))
        print(f"  Fully translated: {full_cn}/{len(players)}")

        if content.startswith('export default '):
            new_content = 'export default ' + json.dumps(players, ensure_ascii=False, indent=2) + ';\n'
        else:
            new_content = 'module.exports = ' + json.dumps(players, ensure_ascii=False, indent=2) + ';\n'

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # Sample check
    print("\n─── Sample fixes ───")
    with open('web/js/players.js', encoding='utf-8') as f:
        data = json.loads(f.read()[len('export default '):].strip().rstrip(';'))
    samples = ['George McCloud', 'Grant Hill', 'Hakeem Olajuwon', 'Eric Snow',
               'Greg Ostertag', 'Adam Morrison', 'Andrew Bynum', 'Antoine Walker']
    for name in samples:
        p = next((x for x in data if x['name_en'] == name), None)
        if p:
            print(f"  {p['name_en']} → {p['name']}")


if __name__ == '__main__':
    main()
