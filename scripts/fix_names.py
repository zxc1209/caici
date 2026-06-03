"""
Fix Chinese names using a comprehensive NBA last name dictionary.
Covers standard NBA Chinese translations for common surnames.
"""
import json, re

# ─── First Name dictionary ───
FIRST_CN_FULL = {
    'aaron': '阿龙', 'adam': '亚当', 'adrian': '阿德里安', 'al': '阿尔',
    'alan': '阿兰', 'alec': '亚历克', 'alex': '亚历克斯', 'alfonzo': '阿方索',
    'alonzo': '阿隆佐', 'amar': '阿马雷', 'amare': '阿马雷', 'andre': '安德烈',
    'andrew': '安德鲁', 'andy': '安迪', 'anthony': '安东尼', 'antoine': '安托万',
    'austin': '奥斯汀', 'avery': '埃弗里', 'bam': '巴姆', 'baron': '拜伦',
    'ben': '本', 'bill': '比尔', 'billy': '比利', 'bismack': '俾斯麦',
    'blake': '布雷克', 'bob': '鲍勃', 'bobby': '博比', 'bogdan': '博格丹',
    'bojan': '博扬', 'brad': '布拉德', 'bradley': '布拉德利', 'brandon': '布兰登',
    'brian': '布莱恩', 'brook': '布鲁克', 'bruce': '布鲁斯', 'bruno': '布鲁诺',
    'buddy': '巴迪', 'byron': '拜伦', 'cade': '凯德', 'caleb': '卡莱布', 'calvin': '卡尔文',
    'cameron': '卡梅伦', 'carl': '卡尔', 'carlos': '卡洛斯', 'carmelo': '卡梅隆',
    'cedric': '塞德里克', 'chandler': '钱德勒', 'charles': '查尔斯', 'chris': '克里斯',
    'christian': '克里斯蒂安', 'chuck': '查克', 'cliff': '克利夫', 'clint': '克林特',
    'clyde': '克莱德', 'coby': '科比', 'cody': '科迪', 'cole': '科尔',
    'corey': '科里', 'cory': '科里', 'craig': '克雷格', 'curtis': '柯蒂斯',
    'dale': '戴尔', 'damian': '达米安', 'damion': '达米恩', 'dan': '丹',
    'danny': '丹尼', 'daniel': '丹尼尔', 'danilo': '达尼洛', 'danny': '丹尼',
    'dante': '丹特', 'dario': '达里奥', 'darius': '达里厄斯', 'david': '大卫',
    'deandre': '德安德烈', 'demar': '德马尔', 'demarcus': '德马库斯',
    'demetrius': '德米特里厄斯', 'dennis': '丹尼斯', 'denzel': '登泽尔',
    'derek': '德里克', 'derrick': '德里克', 'desmond': '德斯蒙德', 'devin': '德文',
    'devonte': '德文特', 'dewayne': '德维恩', 'dillon': '狄龙', 'dirk': '德克',
    'domantas': '多曼塔斯', 'dominique': '多米尼克', 'don': '唐', 'donovan': '多诺万',
    'dorian': '多里安', 'doug': '道格', 'draymond': '德雷蒙德', 'dwight': '德怀特',
    'dwyane': '德怀恩', 'earl': '厄尔', 'eddie': '埃迪', 'edgar': '埃德加',
    'eldridge': '埃尔德里奇', 'elton': '埃尔顿', 'emanuel': '伊曼纽尔',
    'enes': '埃内斯', 'eric': '埃里克', 'ervin': '埃尔文', 'evan': '埃文',
    'frank': '弗兰克', 'franz': '弗朗茨', 'fred': '弗雷德', 'gabe': '加布',
    'gary': '加里', 'gene': '吉恩', 'george': '乔治', 'gerald': '杰拉德',
    'giannis': '扬尼斯', 'gilbert': '吉尔伯特', 'glen': '格伦', 'glenn': '格伦',
    'goran': '戈兰', 'gordon': '戈登', 'grant': '格兰特', 'greg': '格雷格',
    'hakeem': '哈基姆', 'harold': '哈罗德', 'harrison': '哈里森', 'harry': '哈里',
    'hassan': '哈桑', 'herb': '赫布', 'horace': '霍勒斯', 'howard': '霍华德',
    'ike': '艾克', 'isaac': '艾萨克', 'isaiah': '以赛亚', 'ish': '伊什',
    'ivan': '伊万', 'jabari': '贾巴里', 'jack': '杰克', 'jaden': '杰登',
    'jae': '杰', 'jahlil': '贾利尔', 'jakob': '雅各布', 'jamal': '贾马尔',
    'james': '詹姆斯', 'jamie': '杰米', 'jared': '贾里德', 'jarrett': '贾勒特',
    'jason': '杰森', 'javale': '贾维尔', 'jay': '杰伊', 'jaylen': '杰伦',
    'jayson': '杰森', 'jeff': '杰夫', 'jeffrey': '杰弗里', 'jerami': '杰拉米',
    'jeremy': '杰里米', 'jerome': '杰罗姆', 'jerry': '杰里', 'jerryd': '杰里德',
    'jim': '吉姆', 'jimmy': '吉米', 'joakim': '乔金', 'joe': '乔', 'joel': '乔尔',
    'john': '约翰', 'johnny': '约翰尼', 'jonas': '约纳斯', 'jonathan': '乔纳森',
    'jordan': '乔丹', 'josh': '约什', 'joshua': '约书亚', 'jrue': '朱',
    'julius': '朱利叶斯', 'justin': '贾斯汀', 'juwan': '朱万',
    'karl': '卡尔', 'kawhi': '科怀', 'keith': '基思', 'keldon': '凯尔登',
    'kemba': '肯巴', 'kendrick': '肯德里克', 'kenneth': '肯尼思', 'kent': '肯特',
    'kentavious': '肯塔维厄斯', 'kenyon': '肯扬', 'kevin': '凯文', 'klay': '克莱',
    'kobe': '科比', 'kristaps': '克里斯塔普斯', 'kurt': '库尔特', 'kyle': '凯尔',
    'kyrie': '凯里', 'lamarcus': '拉马库斯', 'lamelo': '拉梅洛', 'lance': '兰斯',
    'larry': '拉里', 'lebron': '勒布朗', 'lee': '李', 'leroy': '勒罗伊',
    'lonnie': '朗尼', 'lou': '路', 'lu': '卢', 'luca': '卢卡', 'luka': '卢卡',
    'luol': '罗尔', 'magic': '魔术师', 'malik': '马利克', 'manny': '曼尼',
    'manuel': '曼努埃尔', 'marc': '马克', 'marcus': '马库斯', 'mario': '马里奥',
    'mark': '马克', 'markelle': '马克尔', 'markieff': '马基夫', 'mason': '梅森',
    'maurice': '莫里斯', 'max': '马克斯', 'maxi': '马克西', 'melo': '梅洛',
    'meyers': '迈耶斯', 'michael': '迈克尔', 'mike': '迈克', 'mikal': '米卡尔',
    'miles': '迈尔斯', 'milos': '米洛斯', 'mitch': '米奇', 'monta': '蒙塔',
    'monte': '蒙特', 'montrezl': '蒙特雷兹', 'moses': '摩西', 'mo': '莫',
    'mychal': '迈查尔', 'myles': '迈尔斯', 'naji': '纳吉', 'nathan': '内森',
    'nemanja': '内马尼亚', 'nicholas': '尼古拉斯', 'nick': '尼克', 'nico': '尼科',
    'nicolas': '尼古拉斯', 'nikola': '尼古拉', 'noah': '诺阿', 'norman': '诺曼',
    'og': 'OG', 'omer': '奥默', 'oscar': '奥斯卡', 'otto': '奥托',
    'patrick': '帕特里克', 'patty': '帕蒂', 'paul': '保罗', 'pau': '保罗',
    'pete': '皮特', 'peter': '彼得', 'phil': '菲尔', 'pj': 'PJ', 'quentin': '昆廷',
    'quincy': '昆西', 'raj': '拉吉', 'rajon': '拉简', 'ralph': '拉尔夫',
    'randy': '兰迪', 'rashard': '拉沙德', 'raul': '劳尔', 'ray': '雷',
    'raymond': '雷蒙德', 'reggie': '雷吉', 'reggie': '雷吉', 'ricky': '里基',
    'robert': '罗伯特', 'rodney': '罗德尼', 'ron': '罗恩', 'ronald': '罗纳德',
    'rondae': '朗戴', 'roy': '罗伊', 'royce': '罗伊斯', 'rudy': '鲁迪',
    'russell': '拉塞尔', 'ryan': '瑞安', 'sam': '萨姆', 'samuel': '塞缪尔',
    'scott': '斯科特', 'scottie': '斯科蒂', 'sean': '肖恩', 'seth': '塞思',
    'shabazz': '沙巴兹', 'shai': '谢伊', 'shaquille': '沙奎尔', 'shaun': '肖恩',
    'spencer': '斯宾塞', 'stanley': '斯坦利', 'stephen': '斯蒂芬', 'steve': '史蒂夫',
    'steven': '史蒂文', 'taj': '泰', 'terrance': '特伦斯', 'terry': '特里',
    'thaddeus': '赛迪斯', 'theo': '西奥', 'tim': '蒂姆', 'tobias': '托拜厄斯',
    'tom': '汤姆', 'tony': '托尼', 'trae': '特雷', 'tracy': '特雷西',
    'trevor': '特雷弗', 'tristan': '特里斯坦', 'troy': '特洛伊', 'ty': '泰',
    'tyler': '泰勒', 'tyreke': '泰雷克', 'tyrese': '泰雷塞', 'tyrone': '泰隆',
    'tyus': '泰厄斯', 'victor': '维克托', 'vince': '文斯', 'vlatko': '弗拉特科',
    'wade': '韦德', 'walker': '沃克', 'walt': '沃尔特', 'wayne': '韦恩',
    'wendell': '温德尔', 'wesley': '韦斯利', 'wil': '威尔', 'will': '威尔',
    'william': '威廉', 'willie': '威利', 'willy': '威利', 'yogi': '约吉',
    'zach': '扎克', 'zachary': '扎卡里', 'zaire': '宰雷', 'zion': '锡安',
    # Non-standard/unique first names
    'de\'aaron': '达龙', 'de\'andre': '德安德烈', 'de\'anthony': '德安东尼',
    'd\'angelo': '德安吉洛', 'jae\'sean': '杰肖恩', 'jahmi\'us': '贾缪斯',
    'day\'ron': '戴罗恩', 'mamadou': '马马杜', 'amar\'e': '阿马雷',
    'e\'twaun': '伊托万', 'shareef': '谢里夫', 'mahmoud': '马哈茂德',
    'tariq': '塔里克', 'gheorghe': '格奥尔基', 'horacio': '奥拉西奥',
    'hot': '霍特', 'ivano': '伊万诺', 'jerome': '杰罗姆',
}

# ─── Comprehensive NBA Last Name → Chinese dictionary ───
LAST_CN_FULL = {
    # Super common surnames
    'williams': '威廉姆斯', 'johnson': '约翰逊', 'jones': '琼斯', 'brown': '布朗',
    'smith': '史密斯', 'jackson': '杰克逊', 'robinson': '罗宾逊', 'davis': '戴维斯',
    'thomas': '托马斯', 'green': '格林', 'anderson': '安德森', 'martin': '马丁',
    'harris': '哈里斯', 'wright': '赖特', 'edwards': '爱德华兹', 'miller': '米勒',
    'taylor': '泰勒', 'white': '怀特', 'james': '詹姆斯', 'allen': '阿伦',
    'morris': '莫里斯', 'thompson': '汤普森', 'hunter': '亨特', 'young': '杨',
    'hill': '希尔', 'grant': '格兰特', 'king': '金', 'scott': '斯科特',
    'alexander': '亚历山大', 'evans': '埃文斯', 'richardson': '理查德森',
    'collins': '科林斯', 'hamilton': '汉密尔顿', 'gray': '格雷', 'curry': '库里',
    'howard': '霍华德', 'walker': '沃克', 'knight': '奈特', 'murray': '穆雷',
    'simmons': '西蒙斯', 'butler': '巴特勒', 'daniels': '丹尼尔斯', 'powell': '鲍威尔',
    'hall': '霍尔', 'graham': '格雷厄姆', 'wallace': '华莱士', 'watson': '沃森',

    # NBA specific famous names
    'jordan': '乔丹', 'bryant': '布莱恩特', 'o\'neal': '奥尼尔', 'oneal': '奥尼尔',
    'duncan': '邓肯', 'nowitzki': '诺维茨基', 'antetokounmpo': '阿德托昆博',
    'jokic': '约基奇', 'embiid': '恩比德', 'doncic': '东契奇', 'leonard': '伦纳德',
    'lillard': '利拉德', 'westbrook': '威斯布鲁克', 'harden': '哈登', 'wade': '韦德',
    'parker': '帕克', 'ginobili': '吉诺比利', 'irving': '欧文', 'durant': '杜兰特',
    'olajuwon': '奥拉朱旺', 'stockton': '斯托克顿', 'malone': '马龙', 'barkley': '巴克利',
    'ewing': '尤因', 'pippen': '皮蓬', 'rodman': '罗德曼', 'mutombo': '穆托姆博',
    'mourning': '莫宁', 'iverson': '艾弗森', 'kidd': '基德', 'nash': '纳什',
    'garnett': '加内特', 'mcdyess': '麦克戴斯', 'carter': '卡特', 'miller': '米勒',
    'payton': '佩顿', 'camby': '坎比', 'brand': '布兰德', 'francis': '弗朗西斯',
    'marbury': '马布里', 'arenas': '阿里纳斯', 'stoudemire': '斯塔德迈尔',
    'yao': '姚明', 'ming': '姚明',

    # Active stars
    'tatum': '塔图姆', 'booker': '布克', 'mitchell': '米切尔', 'adebayo': '阿德巴约',
    'towns': '唐斯', 'gobert': '戈贝尔', 'ball': '鲍尔', 'fox': '福克斯',
    'ingram': '英格拉姆', 'randle': '兰德尔', 'siakam': '西亚卡姆',
    'vanvleet': '范弗利特', 'lowry': '洛瑞', 'smart': '斯马特', 'morant': '莫兰特',
    'williamson': '威廉森', 'mobley': '莫布利', 'cunningham': '坎宁安',
    'barnes': '巴恩斯', 'suggs': '萨格斯', 'giddey': '吉迪', 'haliburton': '哈利伯顿',
    'maxey': '马克西', 'herro': '希罗', 'bain': '贝恩', 'garland': '加兰',
    'brunson': '布伦森', 'holmgren': '霍姆格伦', 'wembanyama': '文班亚马',
    'sengun': '申京', 'markkanen': '马尔卡宁', 'vucevic': '武切维奇',
    'sabonis': '萨博尼斯', 'valanciunas': '瓦兰丘纳斯', 'porzingis': '波尔津吉斯',
    'schroder': '施罗德', 'bogdanovic': '博格达诺维奇', 'nurkic': '努尔基奇',
    'capela': '卡佩拉', 'poeltl': '珀尔特尔', 'zubac': '祖巴茨',
    'wiggins': '维金斯', 'ayton': '艾顿', 'bridges': '布里奇斯',
    'hield': '希尔德', 'turner': '特纳', 'conley': '康利', 'clarkson': '克拉克森',
    'sexton': '塞克斯顿', 'love': '乐福', 'lavine': '拉文', 'derozan': '德罗赞',
    'beal': '比尔', 'middleton': '米德尔顿', 'holiday': '霍勒迪', 'lopez': '洛佩兹',
    'horford': '霍福德', 'rozier': '罗齐尔', 'hayward': '海沃德', 'oladipo': '奥拉迪波',
    'wall': '沃尔', 'cousins': '考辛斯', 'griffin': '格里芬', 'aldridge': '阿尔德里奇',
    'millsap': '米尔萨普', 'iguodala': '伊戈达拉', 'rondo': '隆多', 'paul': '保罗',

    # Common names
    'bailey': '贝利', 'baker': '贝克', 'baldwin': '鲍德温', 'banks': '班克斯',
    'barber': '巴伯', 'barnett': '巴奈特', 'barry': '巴里', 'bass': '巴斯',
    'battle': '巴特尔', 'bazemore': '贝兹莫尔', 'beasley': '比斯利', 'bell': '贝尔',
    'benjamin': '本杰明', 'bennett': '本内特', 'benson': '本森', 'beverley': '贝弗利',
    'bird': '伯德', 'bjelica': '别利察', 'blair': '布莱尔', 'bogut': '博古特',
    'bol': '波尔', 'booker': '布克', 'boone': '布恩', 'bosh': '波什',
    'bowen': '鲍文', 'bradley': '布拉德利', 'brewer': '布鲁尔', 'brooks': '布鲁克斯',
    'brown': '布朗', 'burke': '伯克', 'burks': '伯克斯', 'burton': '伯顿',
    'cade': '凯德', 'caldwell': '考德威尔', 'campbell': '坎贝尔', 'carroll': '卡罗尔',
    'carter': '卡特', 'chandler': '钱德勒', 'chapman': '查普曼', 'clark': '克拉克',
    'clarkson': '克拉克森', 'cole': '科尔', 'coleman': '科尔曼', 'cook': '库克',
    'cooper': '库珀', 'craig': '克雷格', 'crawford': '克劳福德', 'cunningham': '坎宁安',
    'curry': '库里', 'davis': '戴维斯', 'dawson': '道森', 'deck': '德克',
    'dellavedova': '德拉维多瓦', 'dieng': '迪昂', 'dinwiddie': '丁威迪',
    'diop': '迪奥普', 'dixon': '迪克森', 'douglas': '道格拉斯', 'dragic': '德拉季奇',
    'drummond': '德拉蒙德', 'dudley': '达德利', 'dunn': '邓恩', 'ellington': '埃灵顿',
    'ellis': '埃利斯', 'farmer': '法玛尔', 'felton': '费尔顿', 'ferguson': '弗格森',
    'finney-smith': '芬尼-史密斯', 'fisher': '费舍尔', 'flynn': '弗林',
    'forbes': '福布斯', 'ford': '福特', 'foster': '福斯特', 'fox': '福克斯',
    'franklin': '富兰克林', 'frazier': '弗雷泽', 'freeman': '弗里曼',
    'fultz': '富尔茨', 'gallinari': '加里纳利', 'galloway': '加洛韦',
    'garcia': '加西亚', 'gardner': '加德纳', 'garrett': '加勒特', 'gasol': '加索尔',
    'gay': '盖伊', 'george': '乔治', 'gibson': '吉布森', 'gilbert': '吉尔伯特',
    'gilgeous-alexander': '吉尔杰斯-亚历山大', 'gordon': '戈登', 'green': '格林',
    'griffin': '格里芬', 'hammond': '哈蒙德', 'hampton': '汉普顿', 'hansen': '汉森',
    'hardaway': '哈达威', 'harden': '哈登', 'hardy': '哈迪', 'harper': '哈珀',
    'harrell': '哈雷尔', 'harrington': '哈林顿', 'harrison': '哈里森', 'hart': '哈特',
    'harvey': '哈维', 'hauser': '豪瑟', 'hawkins': '霍金斯', 'hayes': '海耶斯',
    'hayward': '海沃德', 'henderson': '亨德森', 'henry': '亨利', 'hernangomez': '埃尔南戈麦斯',
    'hicks': '希克斯', 'higgins': '希金斯', 'hines': '海因斯', 'holmes': '霍姆斯',
    'hood': '胡德', 'house': '豪斯', 'houston': '休斯顿', 'howell': '豪威尔',
    'hudson': '哈德森', 'hughes': '休斯', 'ibaka': '伊巴卡', 'iguodala': '伊戈达拉',
    'isaac': '艾萨克', 'jackson': '杰克逊', 'jacobs': '雅各布斯', 'jefferson': '杰弗森',
    'jenkins': '詹金斯', 'jensen': '詹森', 'johnson': '约翰逊', 'johnston': '约翰斯顿',
    'jones': '琼斯', 'jordan': '乔丹', 'joseph': '约瑟夫', 'kaman': '卡曼',
    'kelley': '凯莱', 'kelly': '凯利', 'kennard': '肯纳德', 'kennedy': '肯尼迪',
    'kidd': '基德', 'kilic': '基利奇', 'kleber': '克勒贝尔', 'korver': '科沃尔',
    'kuzma': '库兹马', 'lamb': '兰姆', 'lambert': '兰伯特', 'lane': '莱恩',
    'lavine': '拉文', 'lawrence': '劳伦斯', 'lawson': '劳森', 'lee': '李',
    'leonard': '伦纳德', 'lewis': '刘易斯', 'little': '利特尔', 'livingston': '利文斯顿',
    'logan': '洛根', 'long': '朗', 'lopez': '洛佩兹', 'love': '乐福',
    'lowry': '洛瑞', 'lucas': '卢卡斯', 'lynch': '林奇', 'mack': '麦克',
    'maggette': '马盖蒂', 'manning': '曼宁', 'marion': '马里昂', 'marshall': '马歇尔',
    'martin': '马丁', 'mason': '梅森', 'matthews': '马修斯', 'maxwell': '马克斯韦尔',
    'may': '梅', 'mccollum': '麦科勒姆', 'mccoy': '麦考伊', 'mcdonald': '麦克唐纳',
    'mcgee': '麦基', 'mcgrady': '麦格雷迪', 'mckenzie': '麦肯齐', 'mckinney': '麦金尼',
    'mclaughlin': '麦克劳林', 'mclemore': '麦克勒莫', 'middleton': '米德尔顿',
    'miles': '迈尔斯', 'mills': '米尔斯', 'millsap': '米尔萨普', 'mitchell': '米切尔',
    'monk': '蒙克', 'moody': '穆迪', 'moore': '摩尔', 'morgan': '摩根',
    'morris': '莫里斯', 'moss': '莫斯', 'mullins': '穆林斯', 'murphy': '墨菲',
    'murray': '穆雷', 'myers': '迈尔斯', 'nash': '纳什', 'nelson': '尼尔森',
    'newman': '纽曼', 'newton': '牛顿', 'nichols': '尼科尔斯', 'niang': '尼昂',
    'nurkic': '努尔基奇', 'o\'neal': '奥尼尔', 'oakley': '奥克利', 'okogie': '奥科吉',
    'oladipo': '奥拉迪波', 'oliver': '奥利弗', 'olson': '奥尔森', 'osman': '奥斯曼',
    'oubre': '乌布雷', 'owens': '欧文斯', 'page': '佩奇', 'parker': '帕克',
    'parks': '帕克斯', 'parsons': '帕森斯', 'patterson': '帕特森', 'patton': '巴顿',
    'paul': '保罗', 'payne': '佩恩', 'payton': '佩顿', 'pearson': '皮尔森',
    'perkins': '帕金斯', 'perry': '佩里', 'peters': '彼得斯', 'peterson': '彼得森',
    'phillips': '菲利普斯', 'pierce': '皮尔斯', 'plumlee': '普拉姆利', 'poole': '普尔',
    'pope': '波普', 'porter': '波特', 'powell': '鲍威尔', 'pratt': '普拉特',
    'price': '普莱斯', 'prince': '普林斯', 'quinn': '奎因', 'ramsey': '拉姆齐',
    'randle': '兰德尔', 'reddish': '雷迪什', 'reed': '里德', 'reid': '里德',
    'reyes': '雷耶斯', 'reynolds': '雷诺兹', 'rhodes': '罗兹', 'rice': '赖斯',
    'richards': '理查兹', 'richardson': '理查德森', 'riddick': '里迪克', 'riley': '莱利',
    'rivers': '里弗斯', 'robbins': '罗宾斯', 'roberts': '罗伯茨', 'robertson': '罗伯特森',
    'robinson': '罗宾逊', 'rodriguez': '罗德里格斯', 'rogers': '罗杰斯', 'romero': '罗梅罗',
    'rondo': '隆多', 'rose': '罗斯', 'rowe': '罗', 'rozier': '罗齐尔',
    'rubio': '卢比奥', 'ruiz': '鲁伊斯', 'russell': '拉塞尔', 'ryan': '瑞安',
    'sabonis': '萨博尼斯', 'salazar': '萨拉查', 'sanchez': '桑切斯', 'sanders': '桑德斯',
    'santos': '桑托斯', 'saric': '沙里奇', 'schmidt': '施密特', 'schneider': '施耐德',
    'schofield': '斯科菲尔德', 'schultz': '舒尔茨', 'scott': '斯科特', 'sexton': '塞克斯顿',
    'shamet': '沙梅特', 'sharp': '夏普', 'shaw': '肖', 'shelton': '谢尔顿',
    'sheppard': '谢泼德', 'sherman': '谢尔曼', 'silva': '席尔瓦', 'sims': '西姆斯',
    'singleton': '辛格顿', 'smart': '斯马特', 'smith': '史密斯',
    'snyder': '斯奈德', 'spencer': '斯宾塞', 'stewart': '斯图尔特',
    'stokes': '斯托克斯', 'stone': '斯通', 'strickland': '斯特里克兰',
    'sutton': '萨顿', 'swanson': '斯旺森',
    'tate': '塔特', 'terry': '特里', 'thompson': '汤普森', 'thornton': '桑顿',
    'tinsley': '廷斯利', 'todd': '托德', 'torres': '托雷斯', 'towns': '唐斯',
    'townsend': '汤森', 'tucker': '塔克', 'turner': '特纳', 'tyler': '泰勒',
    'udrih': '尤德里', 'underwood': '安德伍德', 'valdez': '瓦尔德斯',
    'vanvleet': '范弗利特', 'vargas': '瓦格斯', 'vaughn': '沃恩', 'villanueva': '维拉纽瓦',
    'vincent': '文森特', 'vucevic': '武切维奇',
    'wade': '韦德', 'wagner': '瓦格纳', 'walton': '沃尔顿',
    'walters': '沃尔特斯', 'ward': '沃德', 'warren': '沃伦', 'washington': '华盛顿',
    'watkins': '沃特金斯', 'watson': '沃森', 'weaver': '韦弗', 'webb': '韦伯',
    'webster': '韦伯斯特', 'welch': '韦尔奇', 'wells': '威尔斯', 'west': '韦斯特',
    'white': '怀特', 'whitney': '惠特尼', 'wilcox': '威尔科克斯',
    'wilkerson': '威尔克森', 'wilkins': '威尔金斯', 'wilkinson': '威尔金森',
    'williams': '威廉姆斯', 'williamson': '威廉森', 'willis': '威利斯',
    'wilson': '威尔逊', 'wong': '王', 'wood': '伍德', 'woodard': '伍达德',
    'woods': '伍兹', 'wrigh': '赖特', 'wright': '赖特',
    'yates': '耶茨', 'york': '约克',
    'zimmerman': '齐默尔曼', 'zubac': '祖巴茨',

    # Additional NBA names
    'abdur-rahim': '阿卜杜尔-拉希姆', 'abdul-rauf': '阿卜杜尔-拉乌夫',
    'abdul-wahad': '阿卜杜尔-瓦哈德', 'ariza': '阿里扎', 'artest': '阿泰斯特',
    'bagley': '巴格利', 'ball': '鲍尔', 'bamba': '班巴', 'batum': '巴图姆',
    'bazley': '贝兹利', 'beal': '比尔', 'bertans': '贝尔坦斯', 'bey': '贝',
    'bogdanovic': '博格达诺维奇', 'bol': '波尔', 'bonga': '邦加', 'boucher': '布歇',
    'braun': '布劳恩', 'brogdon': '布罗格登', 'bullock': '布洛克',
    'caboclo': '卡博克洛', 'caldwell-pope': '考德威尔-波普', 'carmelo': '卡梅隆',
    'caruso': '卡鲁索', 'clarkson': '克拉克森', 'clinton': '克林顿',
    'coffey': '科菲', 'connaughton': '康诺顿', 'corley': '科利',
    'covington': '科温顿', 'craig': '克雷格', 'crowder': '克劳德',
    'daniels': '丹尼尔斯', 'dieng': '迪昂', 'diop': '迪奥普', 'divencenzo': '迪温琴佐',
    'dort': '多尔特', 'dosunmu': '多森姆', 'duarte': '杜阿尔特',
    'eason': '伊森', 'edwards': '爱德华兹', 'ennis': '恩尼斯',
    'fernando': '费尔南多', 'finney-smith': '芬尼-史密斯', 'fultz': '富尔茨',
    'gallinari': '加里纳利', 'garland': '加兰', 'garuba': '加鲁巴',
    'george': '乔治', 'giddey': '吉迪', 'gilgeous-alexander': '吉尔杰斯-亚历山大',
    'gobert': '戈贝尔', 'gordon': '戈登', 'grant': '格兰特', 'green': '格林',
    'grimes': '格莱姆斯', 'haliburton': '哈利伯顿', 'hardaway': '哈达威',
    'harrell': '哈雷尔', 'harris': '哈里斯', 'herro': '希罗',
    'hield': '希尔德', 'holmgren': '霍姆格伦', 'holmes': '霍姆斯',
    'horford': '霍福德', 'horton-tucker': '霍顿-塔克', 'house': '豪斯',
    'howard': '霍华德', 'huerter': '赫尔特', 'hunter': '亨特',
    'ingram': '英格拉姆', 'isaac': '艾萨克', 'ivey': '艾维',
    'jackson': '杰克逊', 'james': '詹姆斯', 'jokic': '约基奇',
    'jones': '琼斯', 'joseph': '约瑟夫', 'kennard': '肯纳德',
    'kidd': '基德', 'king': '金', 'kispert': '基斯珀特',
    'kleber': '克勒贝尔', 'knight': '奈特', 'knox': '诺克斯',
    'kuminga': '库明加', 'kuzma': '库兹马', 'lauri': '马尔卡宁',
    'lavine': '拉文', 'lee': '李', 'leonard': '伦纳德',
    'lewis': '刘易斯', 'looney': '卢尼', 'lopez': '洛佩兹',
    'love': '乐福', 'lowry': '洛瑞', 'luka': '东契奇',
    'marshall': '马歇尔', 'martin': '马丁', 'mathurin': '马瑟林',
    'matthews': '马修斯', 'mccollum': '麦科勒姆', 'mcdaniels': '麦克丹尼尔斯',
    'mcgee': '麦基', 'metu': '梅图', 'middleton': '米德尔顿',
    'miller': '米勒', 'mills': '米尔斯', 'mitchell': '米切尔',
    'mobley': '莫布利', 'monk': '蒙克', 'moody': '穆迪', 'moore': '摩尔',
    'morant': '莫兰特', 'morris': '莫里斯', 'murphy': '墨菲',
    'murray': '穆雷', 'nance': '南斯', 'niang': '尼昂',
    'noel': '诺埃尔', 'nurkic': '努尔基奇', 'nwora': '诺拉',
    'okeke': '奥克克', 'okongwu': '奥孔古', 'oladipo': '奥拉迪波',
    'olynyk': '奥利尼克', 'oneal': '奥尼尔', 'osman': '奥斯曼',
    'oubre': '乌布雷', 'parker': '帕克', 'parsons': '帕森斯',
    'patton': '巴顿', 'paul': '保罗', 'payne': '佩恩', 'payton': '佩顿',
    'poeltl': '珀尔特尔', 'poole': '普尔', 'porter': '波特',
    'powell': '鲍威尔', 'primo': '普里莫', 'prince': '普林斯',
    'randle': '兰德尔', 'reed': '里德', 'reaves': '里夫斯',
    'richardson': '理查德森', 'rivers': '里弗斯', 'robinson': '罗宾逊',
    'rose': '罗斯', 'rozier': '罗齐尔', 'russell': '拉塞尔',
    'sabonis': '萨博尼斯', 'saric': '沙里奇', 'schroder': '施罗德',
    'sexton': '塞克斯顿', 'shamet': '沙梅特', 'sharpe': '夏普',
    'simmons': '西蒙斯', 'simons': '西蒙斯', 'siakam': '西亚卡姆',
    'smart': '斯马特', 'smith': '史密斯', 'sochan': '索汉',
    'stevens': '史蒂文斯', 'stewart': '斯图尔特', 'strus': '斯特鲁斯',
    'suggs': '萨格斯', 'tatum': '塔图姆', 'thompson': '汤普森',
    'toppin': '托平', 'towns': '唐斯', 'trent': '特伦特',
    'tucker': '塔克', 'turner': '特纳',
    'valanciunas': '瓦兰丘纳斯', 'vanderbilt': '范德比尔特',
    'vassell': '瓦塞尔', 'vincent': '文森特', 'vucevic': '武切维奇',
    'wagner': '瓦格纳', 'walker': '沃克', 'wall': '沃尔',
    'wallace': '华莱士', 'washington': '华盛顿', 'westbrook': '威斯布鲁克',
    'white': '怀特', 'wiggins': '维金斯', 'williams': '威廉姆斯',
    'williamson': '威廉森', 'wood': '伍德', 'wright': '赖特',
    'young': '杨', 'zubac': '祖巴茨',
}

def fix_all_names():
    for path in ['miniprogram/data/players.js', 'web/js/players.js']:
        print(f"\nProcessing: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        prefix = 'module.exports = ' if 'module.exports' in content else 'export default '
        players = json.loads(content[len(prefix):].strip().rstrip(';'))

        fixed = 0
        for p in players:
            parts = p['name_en'].split()
            if len(parts) < 2:
                continue

            first = parts[0].lower().rstrip(".,'\"")
            last = parts[-1].lower().rstrip(".,'\"")

            # Look up first name
            fn_cn = FIRST_CN_FULL.get(first)
            if not fn_cn:
                # Try removing dots/apostrophes
                clean = re.sub(r"[.']", '', first)
                fn_cn = FIRST_CN_FULL.get(clean)

            # Look up last name
            ln_cn = LAST_CN_FULL.get(last)
            if not ln_cn:
                for sfx in [' jr', ' sr', ' iii', ' ii', ' iv']:
                    base = last.replace(sfx, '')
                    ln_cn = LAST_CN_FULL.get(base)
                    if ln_cn: break

            if not ln_cn and '-' in last:
                subs = last.split('-')
                sub_cn = [LAST_CN_FULL.get(s, s) for s in subs]
                if all(s != orig for s, orig in zip(sub_cn, subs)):
                    ln_cn = '-'.join(sub_cn)

            if fn_cn and ln_cn:
                old = p['name']
                p['name'] = f"{fn_cn}·{ln_cn}"
                if old != p['name']: fixed += 1
            elif ln_cn:
                # Use existing first name part (may be phonetic, but better than nothing)
                cn_parts = old = p.get('name', '').split('·')
                old_fn = cn_parts[0] if cn_parts else first.title()
                p['name'] = f"{old_fn}·{ln_cn}"
                if old != p['name']: fixed += 1
            elif fn_cn:
                old = p.get('name', '')
                cn_parts = old.split('·')
                old_ln = cn_parts[-1] if len(cn_parts) > 1 else last.title()
                p['name'] = f"{fn_cn}·{old_ln}"
                if old != p['name']: fixed += 1

        print(f"  Fixed {fixed} names")

        new_content = prefix + json.dumps(players, ensure_ascii=False, indent=2) + ';\n'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    # Show samples
    print("\n--- Sample fixes ---")
    samples = ['Michael Jordan', 'Jordan Clarkson', 'Klay Thompson',
               'John Stockton', 'Karl Malone', 'Hakeem Olajuwon',
               'Dikembe Mutombo', 'Scottie Pippen', 'Dennis Rodman']
    for name in samples:
        p = next((x for x in players if x['name_en'] == name), None)
        if p:
            print(f"  {name} → {p['name']}")

    # Count remaining bad names
    bad = sum(1 for x in players if re.search(r'[a-zA-Z]{3,}', x.get('name', '')))
    print(f"\n  Still have English letters: {bad}/{len(players)}")

if __name__ == '__main__':
    fix_all_names()
