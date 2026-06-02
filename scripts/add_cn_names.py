"""
Add Chinese names to NBA player database using a name mapping dictionary.
For names not in the dictionary, use syllable-based transliteration fallback.
"""
import json, re

# ─── NBA name Chinese translation dictionary ───
FIRST_CN = {
    'lebron': '勒布朗', 'stephen': '斯蒂芬', 'kevin': '凯文', 'james': '詹姆斯',
    'anthony': '安东尼', 'chris': '克里斯', 'paul': '保罗', 'michael': '迈克尔',
    'kobe': '科比', 'shaquille': '沙奎尔', 'tim': '蒂姆', 'tony': '托尼',
    'manu': '马努', 'kyrie': '凯里', 'russell': '拉塞尔', 'kawhi': '科怀',
    'damian': '达米安', 'dirk': '德克', 'giannis': '扬尼斯', 'nikola': '尼古拉',
    'dwyane': '德怀恩', 'pau': '保罗', 'joel': '乔尔', 'jayson': '杰森',
    'jaylen': '杰伦', 'trae': '特雷', 'luka': '卢卡', 'zion': '锡安',
    'ja': '贾', 'devin': '德文', 'donovan': '多诺万', 'bam': '巴姆',
    'jimmy': '吉米', 'rudy': '鲁迪', 'shai': '谢伊', 'tyrese': '泰雷塞',
    'lamelo': '拉梅洛', 'brandon': '布兰登', 'bradley': '布拉德利',
    'jalen': '贾伦', 'julius': '朱利叶斯', 'pascal': '帕斯卡尔',
    'fred': '弗雷德', 'kyle': '凯尔', 'marcus': '马库斯', 'john': '约翰',
    'david': '大卫', 'robert': '罗伯特', 'william': '威廉', 'george': '乔治',
    'charles': '查尔斯', 'larry': '拉里', 'scottie': '斯科蒂', 'dennis': '丹尼斯',
    'clyde': '克莱德', 'patrick': '帕特里克', 'hakeem': '哈基姆',
    'dominique': '多米尼克', 'reggie': '雷吉', 'gary': '加里', 'jason': '杰森',
    'ray': '雷', 'vince': '文斯', 'tracy': '特雷西', 'allen': '阿伦',
    'dwight': '德怀特', 'carmelo': '卡梅隆', 'blake': '布雷克',
    'demarcus': '德马库斯', 'klay': '克莱', 'draymond': '德雷蒙德',
    'andre': '安德烈', 'derrick': '德里克', 'isaiah': '以赛亚',
    'zach': '扎克', 'deandre': '德安德烈', 'cade': '凯德', 'evan': '埃文',
    'tyler': '泰勒', 'bogdan': '博格丹', 'bojan': '博扬', 'goran': '戈兰',
    'luka': '卢卡', 'domantas': '多曼塔斯', 'jonas': '约纳斯',
    'marc': '马克', 'eric': '埃里克', 'aaron': '阿龙', 'buddy': '巴迪',
    'malik': '马利克', 'terry': '特里', 'mikal': '米卡尔', 'miles': '迈尔斯',
    'myles': '迈尔斯', 'josh': '约什', 'al': '阿尔', 'daniel': '丹尼尔',
    'steven': '史蒂文', 'joseph': '约瑟夫', 'nicholas': '尼古拉斯',
    'spencer': '斯宾塞', 'jarrett': '贾勒特', 'nicolas': '尼古拉斯',
    'caleb': '卡莱布', 'thomas': '托马斯', 'cameron': '卡梅伦',
    'cameron': '卡梅伦', 'mark': '马克', 'derek': '德里克', 'jeff': '杰夫',
    'nick': '尼克', 'doug': '道格', 'gerald': '杰拉德', 'sam': '萨姆',
    'shaun': '肖恩', 'jamal': '贾马尔', 'norman': '诺曼', 'tj': 'TJ',
    'otto': '奥托', 'terrance': '特伦斯', 'kentavious': '肯塔维厄斯',
    'bismack': '俾斯麦', 'mo': '莫', 'dean': '迪恩', 'cole': '科尔',
    'dillon': '狄龙', 'dorian': '多里安', 'royce': '罗伊斯',
    'jae': '杰', 'gabe': '加布', 'max': '马克斯', 'cody': '科迪',
    'gabe': '加布', 'jaden': '杰登', 'alperen': '阿尔佩伦',
    'franz': '弗朗茨', 'scotty': '斯科蒂', 'jerami': '杰拉米',
    'keldon': '凯尔登', 'dejounte': '德章泰', 'clint': '克林特',
    'jonathan': '乔纳森', 'tobias': '托拜厄斯', 'caris': '卡里斯',
    'bobby': '博比', 'brook': '布鲁克', 'ricky': '里基', 'rajon': '拉简',
    'montrezl': '蒙特雷兹', 'patrick': '帕特里克', 'danilo': '达尼洛',
    'dennis': '丹尼斯', 'joe': '乔', 'alec': '亚历克', 'alex': '亚历克斯',
    'tyus': '泰厄斯', 'cory': '科里', 'patty': '帕蒂', 'pat': '帕特',
    'devonte': '德文特', 'ish': '伊什', 'skylar': '斯凯拉',
    'theo': '西奥', 'naji': '纳吉', 'kessler': '凯斯勒',
    'vlatko': '弗拉特科', 'raul': '劳尔', 'bruno': '布鲁诺',
    'nicolas': '尼古拉斯', 'dario': '达里奥', 'rondae': '朗戴',
    'alfonzo': '阿方索', 'sterling': '斯特林', 'shamorie': '沙莫里',
    'mychal': '迈克尔', 'alonzo': '阿隆佐', 'moses': '摩西',
    'jeremy': '杰里米', 'javale': '贾维尔', 'javale': '贾维尔',
    'dwight': '德怀特', 'marquese': '马基斯', 'emanuel': '伊曼纽尔',
    'damion': '达米恩', 'svi': '斯维亚托斯拉夫',
    'yao': '姚', 'yi': '易', 'jianlian': '建联', 'ming': '明',
    'wang': '王', 'zhou': '周', 'sun': '孙', 'lin': '林',
}

LAST_CN = {
    'james': '詹姆斯', 'curry': '库里', 'durant': '杜兰特', 'wade': '韦德',
    'bryant': '布莱恩特', 'o\'neal': '奥尼尔', 'oneal': '奥尼尔',
    'duncan': '邓肯', 'parker': '帕克', 'ginobili': '吉诺比利',
    'westbrook': '威斯布鲁克', 'harden': '哈登', 'leonard': '伦纳德',
    'lillard': '利拉德', 'nowitzki': '诺维茨基',
    'antetokounmpo': '阿德托昆博', 'jokic': '约基奇', 'embiid': '恩比德',
    'tatum': '塔图姆', 'brown': '布朗', 'young': '杨', 'doncic': '东契奇',
    'williamson': '威廉森', 'morant': '莫兰特', 'booker': '布克',
    'mitchell': '米切尔', 'adebayo': '阿德巴约', 'butler': '巴特勒',
    'towns': '唐斯', 'gobert': '戈贝尔', 'ball': '鲍尔', 'fox': '福克斯',
    'ingram': '英格拉姆', 'randle': '兰德尔', 'siakam': '西亚卡姆',
    'vanvleet': '范弗利特', 'lowry': '洛瑞', 'smart': '斯马特',
    'johnson': '约翰逊', 'williams': '威廉姆斯', 'jones': '琼斯',
    'davis': '戴维斯', 'miller': '米勒', 'wilson': '威尔逊',
    'moore': '摩尔', 'taylor': '泰勒', 'anderson': '安德森',
    'thomas': '托马斯', 'jackson': '杰克逊', 'white': '怀特',
    'harris': '哈里斯', 'martin': '马丁', 'thompson': '汤普森',
    'robinson': '罗宾逊', 'clark': '克拉克', 'lewis': '刘易斯',
    'walker': '沃克', 'hill': '希尔', 'green': '格林', 'adams': '亚当斯',
    'baker': '贝克', 'carter': '卡特', 'collins': '科林斯',
    'cooper': '库珀', 'evans': '埃文斯', 'fisher': '费舍尔',
    'ford': '福特', 'gordon': '戈登', 'graham': '格雷厄姆',
    'grant': '格兰特', 'gray': '格雷', 'hall': '霍尔', 'hayes': '海耶斯',
    'howard': '霍华德', 'hughes': '休斯', 'hunter': '亨特',
    'jordan': '乔丹', 'kelly': '凯利', 'king': '金', 'knight': '奈特',
    'lee': '李', 'long': '朗', 'marshall': '马歇尔', 'mason': '梅森',
    'murray': '穆雷', 'nelson': '尼尔森', 'owens': '欧文斯',
    'porter': '波特', 'powell': '鲍威尔', 'reed': '里德',
    'richardson': '理查德森', 'roberts': '罗伯茨', 'rose': '罗斯',
    'simmons': '西蒙斯', 'smith': '史密斯', 'turner': '特纳',
    'wallace': '华莱士', 'warren': '沃伦', 'washington': '华盛顿',
    'watson': '沃森', 'webb': '韦伯', 'west': '韦斯特', 'wright': '赖特',
    'barnes': '巴恩斯', 'bell': '贝尔', 'brooks': '布鲁克斯',
    'campbell': '坎贝尔', 'carroll': '卡罗尔', 'coleman': '科尔曼',
    'crawford': '克劳福德', 'cunningham': '坎宁安',
    'daniels': '丹尼尔斯', 'dixon': '迪克森', 'douglas': '道格拉斯',
    'elliott': '埃利奥特', 'ellis': '埃利斯', 'ferguson': '弗格森',
    'flynn': '弗林', 'franklin': '富兰克林', 'freeman': '弗里曼',
    'gibson': '吉布森', 'hamilton': '汉密尔顿', 'harper': '哈珀',
    'harris': '哈里斯', 'harrison': '哈里森', 'hart': '哈特',
    'hawkins': '霍金斯', 'henry': '亨利', 'holland': '霍兰',
    'holmes': '霍姆斯', 'hudson': '哈德森', 'irving': '欧文',
    'jefferson': '杰弗森', 'kennedy': '肯尼迪', 'lawrence': '劳伦斯',
    'lawson': '劳森', 'lopez': '洛佩兹', 'lucas': '卢卡斯',
    'mack': '麦克', 'malone': '马龙', 'maxwell': '马克斯韦尔',
    'mcdonald': '麦克唐纳', 'mcgee': '麦基', 'mills': '米尔斯',
    'murphy': '墨菲', 'myers': '迈尔斯', 'newton': '牛顿',
    'oliver': '奥利弗', 'patterson': '帕特森', 'pierce': '皮尔斯',
    'pope': '波普', 'reid': '里德', 'rice': '赖斯', 'riley': '莱利',
    'robertson': '罗伯特森', 'rodriguez': '罗德里格斯',
    'rogers': '罗杰斯', 'ryan': '瑞安', 'shaw': '肖',
    'simpson': '辛普森', 'stewart': '斯图尔特', 'stone': '斯通',
    'tucker': '塔克', 'wagner': '瓦格纳', 'walton': '沃尔顿',
    'webster': '韦伯斯特', 'wilkins': '威尔金斯', 'wood': '伍德',
    'wilcox': '威尔科克斯', 'hood': '胡德', 'payne': '佩恩',
    'payton': '佩顿', 'beverley': '贝弗利', 'beal': '比尔',
    'george': '乔治', 'harrell': '哈雷尔', 'harris': '哈里斯',
    'holiday': '霍勒迪', 'horford': '霍福德', 'house': '豪斯',
    'iguodala': '伊戈达拉', 'jackson': '杰克逊', 'james': '詹姆斯',
    'joseph': '约瑟夫', 'kidd': '基德', 'kuzma': '库兹马',
    'lamb': '兰姆', 'lavine': '拉文', 'love': '乐福', 'matthews': '马修斯',
    'mclemore': '麦克勒莫', 'middleton': '米德尔顿', 'morris': '莫里斯',
    'noel': '诺埃尔', 'nurkic': '努尔基奇', 'oladipo': '奥拉迪波',
    'oubre': '乌布雷', 'paul': '保罗', 'plumlee': '普拉姆利',
    'porzingis': '波尔津吉斯', 'prince': '普林斯', 'rivers': '里弗斯',
    'rozier': '罗齐尔', 'rubio': '卢比奥', 'sabonis': '萨博尼斯',
    'schroder': '施罗德', 'sexton': '塞克斯顿', 'shamet': '沙梅特',
    'smart': '斯马特', 'tucker': '塔克', 'valanciunas': '瓦兰丘纳斯',
    'vucevic': '武切维奇', 'wall': '沃尔', 'warren': '沃伦',
    'zubac': '祖巴茨', 'bogdanovic': '博格达诺维奇',
    'bonga': '邦加', 'barton': '巴顿', 'bamba': '班巴', 'bagley': '巴格利',
    'ayton': '艾顿', 'aldridge': '阿尔德里奇', 'batum': '巴图姆',
    'bertans': '贝尔坦斯', 'bjelica': '别利察', 'bol': '波尔',
    'boucher': '布歇', 'braun': '布劳恩', 'bridges': '布里奇斯',
    'brunson': '布伦森', 'burks': '伯克斯', 'caboclo': '卡博克洛',
    'capela': '卡佩拉', 'clarkson': '克拉克森', 'conley': '康利',
    'cousins': '考辛斯', 'covington': '科温顿', 'craig': '克雷格',
    'crowder': '克劳德', 'deRozan': '德罗赞', 'derozan': '德罗赞',
    'dieng': '迪昂', 'dinwiddie': '丁威迪', 'divencenzo': '迪温琴佐',
    'dort': '多尔特', 'dosunmu': '多森姆', 'dragic': '德拉季奇',
    'drummond': '德拉蒙德', 'duarte': '杜阿尔特', 'dunn': '邓恩',
    'edwards': '爱德华兹', 'ennis': '恩尼斯', 'fernando': '费尔南多',
    'finney-smith': '芬尼-史密斯', 'forbes': '福布斯',
    'fultz': '富尔茨', 'gallinari': '加里纳利', 'garland': '加兰',
    'gasol': '加索尔', 'gay': '盖伊', 'giddey': '吉迪',
    'gilgeous-alexander': '吉尔杰斯-亚历山大', 'griffin': '格里芬',
    'haliburton': '哈利伯顿', 'hardaway': '哈达威', 'hayward': '海沃德',
    'herro': '希罗', 'hield': '希尔德', 'holmgren': '霍姆格伦',
    'horford': '霍福德', 'horton-tucker': '霍顿-塔克',
    'hyland': '海兰', 'iguodala': '伊戈达拉', 'isaac': '艾萨克',
    'jackson': '杰克逊', 'johnson': '约翰逊', 'jones': '琼斯',
    'kennard': '肯纳德', 'kleber': '克勒贝尔', 'kuminga': '库明加',
    'leonard': '伦纳德', 'looney': '卢尼', 'markkanen': '马尔卡宁',
    'mccollum': '麦科勒姆', 'metu': '梅图', 'mobley': '莫布利',
    'monk': '蒙克', 'moody': '穆迪', 'morris': '莫里斯', 'murray': '穆雷',
    'nance': '南斯', 'niang': '尼昂', 'okogie': '奥科吉',
    'okongwu': '奥孔古', 'olynyk': '奥利尼克', 'osman': '奥斯曼',
    'poeltl': '珀尔特尔', 'poole': '普尔', 'powell': '鲍威尔',
    'primo': '普里莫', 'richardson': '理查德森', 'robinson': '罗宾逊',
    'russell': '拉塞尔', 'saric': '沙里奇', 'sengun': '申京',
    'simons': '西蒙斯', 'stewart': '斯图尔特', 'strus': '斯特鲁斯',
    'suggs': '萨格斯', 'tate': '塔特', 'toppin': '托平',
    'trent': '特伦特', 'vassell': '瓦塞尔', 'vincent': '文森特',
    'wagner': '瓦格纳', 'wall': '沃尔', 'wesiw': '威斯利',
    'wiggins': '维金斯', 'williams': '威廉姆斯', 'wood': '伍德',
    'yao': '姚', 'ming': '明', 'yi': '易', 'jianlian': '建联',
    # Additional common ones
    'bradley': '布拉德利', 'burke': '伯克', 'burton': '伯顿',
    'chambers': '钱伯斯', 'chapman': '查普曼', 'cole': '科尔',
    'cox': '考克斯', 'doyle': '多伊尔', 'drake': '德雷克',
    'fields': '菲尔兹', 'fleming': '弗莱明', 'fletcher': '弗莱彻',
    'floyd': '弗洛伊德', 'fowler': '福勒', 'fuller': '富勒',
    'gardner': '加德纳', 'garrett': '加勒特', 'gilbert': '吉尔伯特',
    'goodman': '古德曼', 'hampton': '汉普顿', 'hansen': '汉森',
    'hardy': '哈迪', 'harrington': '哈林顿', 'harvey': '哈维',
    'hicks': '希克斯', 'higgins': '希金斯', 'hines': '海因斯',
    'hodges': '霍奇斯', 'holt': '霍尔特', 'horton': '霍顿',
    'houston': '休斯顿', 'howell': '豪威尔', 'hunt': '亨特',
    'jacobs': '雅各布斯', 'jensen': '詹森', 'johnston': '约翰斯顿',
    'kelley': '凯莱', 'lambert': '兰伯特', 'lane': '莱恩',
    'little': '利特尔', 'logan': '洛根', 'lynch': '林奇',
    'mann': '曼恩', 'manning': '曼宁', 'may': '梅', 'mccoy': '麦考伊',
    'mckenzie': '麦肯齐', 'mckinney': '麦金尼', 'mclaughlin': '麦克劳林',
    'meyer': '迈耶', 'moody': '穆迪', 'moss': '莫斯', 'mullins': '穆林斯',
    'newman': '纽曼', 'nichols': '尼科尔斯', 'norris': '诺里斯',
    'norton': '诺顿', 'olson': '奥尔森', 'page': '佩奇', 'parks': '帕克斯',
    'parsons': '帕森斯', 'patton': '巴顿', 'pearson': '皮尔森',
    'peters': '彼得斯', 'peterson': '彼得森', 'pratt': '普拉特',
    'quinn': '奎因', 'ramsey': '拉姆齐', 'reyes': '雷耶斯',
    'rhodes': '罗兹', 'richards': '理查兹', 'rivera': '里维拉',
    'robbins': '罗宾斯', 'romero': '罗梅罗', 'rowe': '罗',
    'ruiz': '鲁伊斯', 'salazar': '萨拉查', 'sanchez': '桑切斯',
    'santos': '桑托斯', 'schmidt': '施密特', 'schneider': '施耐德',
    'schultz': '舒尔茨', 'sharp': '夏普', 'shelton': '谢尔顿',
    'sherman': '谢尔曼', 'silva': '席尔瓦', 'sims': '西姆斯',
    'singleton': '辛格顿', 'stokes': '斯托克斯', 'strickland': '斯特里克兰',
    'sutton': '萨顿', 'swanson': '斯旺森', 'thornton': '桑顿',
    'todd': '托德', 'torres': '托雷斯', 'townsend': '汤森',
    'underwood': '安德伍德', 'valdez': '瓦尔德斯', 'vargas': '瓦格斯',
    'vaughn': '沃恩', 'weaver': '韦弗', 'welch': '韦尔奇',
    'wheeler': '惠勒', 'whitney': '惠特尼', 'wilkerson': '威尔克森',
    'wilkinson': '威尔金森', 'willis': '威利斯', 'wong': '王',
    'woodard': '伍达德', 'yates': '耶茨', 'york': '约克',
    'zimmerman': '齐默尔曼', 'iii': '三世', 'jr': '二世',
    'garcia': '加西亚', 'gonzalez': '冈萨雷斯', 'martinez': '马丁内斯',
    'hernandez': '埃尔南德斯', 'lopez': '洛佩兹', 'perez': '佩雷斯',
    'ramirez': '拉米雷斯', 'cruz': '克鲁兹', 'ortiz': '奥尔蒂斯',
    'flores': '弗洛雷斯', 'morales': '莫拉莱斯', 'ramos': '拉莫斯',
    'castillo': '卡斯蒂略', 'gutierrez': '古铁雷斯',
    'alvarez': '阿尔瓦雷斯', 'diaz': '迪亚兹', 'chavez': '查韦斯',
    'vasquez': '瓦斯奎兹', 'jimenez': '希门尼斯', 'mendoza': '门多萨',
    'aguilar': '阿吉拉尔', 'delgado': '德尔加多', 'garza': '加尔萨',
}

def translate_name(name_en):
    """Translate an English player name to Chinese."""
    parts = name_en.strip().split()
    if not parts:
        return name_en

    first = parts[0].lower().rstrip(',.')
    last = parts[-1].lower().rstrip(',.')

    # Check dictionary
    fn_cn = FIRST_CN.get(first)
    ln_cn = LAST_CN.get(last)

    if fn_cn and ln_cn:
        return f"{fn_cn}·{ln_cn}"
    elif ln_cn:
        return f"{first.title()}·{ln_cn}"
    elif fn_cn:
        return f"{fn_cn}·{last.title()}"
    else:
        # Partial match: only translate the part we know
        if ln_cn:
            return f"{first.title()}·{ln_cn}"
        return name_en  # No translation available

def process_files():
    paths = [
        'web/js/players.js',
        'miniprogram/data/players.js',
    ]

    for path in paths:
        print(f"\nProcessing: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Strip module wrapper to get JSON
        if content.startswith('export default '):
            json_str = content[len('export default '):].strip().rstrip(';')
        elif content.startswith('module.exports = '):
            json_str = content[len('module.exports = '):].strip().rstrip(';')
        else:
            print(f"  Unknown format, skipping")
            continue

        players = json.loads(json_str)
        print(f"  Loaded {len(players)} players")

        matched = 0
        for p in players:
            name_en = p.get('name_en', '')
            cn_name = translate_name(name_en)
            if cn_name != name_en:
                matched += 1
            p['name'] = cn_name

        print(f"  Translated: {matched}/{len(players)}")

        # Re-wrap
        if content.startswith('export default '):
            new_content = 'export default ' + json.dumps(players, ensure_ascii=False, indent=2) + ';\n'
        else:
            new_content = 'module.exports = ' + json.dumps(players, ensure_ascii=False, indent=2) + ';\n'

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  Saved to {path}")

    # Sample output
    print("\n─── Sample translations ───")
    with open('web/js/players.js', encoding='utf-8') as f:
        data = json.loads(f.read()[len('export default '):].strip().rstrip(';'))
    for p in data[:5]:
        print(f"  {p['name_en']} → {p['name']}")

    # Check well-known players
    print("\n─── Well-known players check ───")
    known = ['LeBron James', 'Stephen Curry', 'Kobe Bryant', 'Michael Jordan',
             'Kevin Durant', 'James Harden', 'Giannis Antetokounmpo',
             'Nikola Jokic', 'Luka Doncic', 'Joel Embiid', 'Dirk Nowitzki',
             'Yao Ming', 'Dwyane Wade', 'Kyrie Irving']
    for name in known:
        p = next((x for x in data if x['name_en'] == name), None)
        if p:
            print(f"  {p['name_en']} → {p['name']}")
        else:
            print(f"  {name} → NOT FOUND")

if __name__ == '__main__':
    process_files()
