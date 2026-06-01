# NBA 球员猜词游戏 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个微信小程序 NBA 猜词游戏，支持双模式 + 三档难度，15 维相似度计算

**Architecture:** 纯前端微信小程序，球员数据打包为本地 JSON，所有相似度计算在客户端完成。三页面结构（首页/游戏/结果），核心逻辑集中在 utils/ 目录下的三个独立 JS 模块

**Tech Stack:** 微信小程序原生框架（WXML + WXSS + JS），Python 3（数据采集脚本），Node.js（工具函数单元测试）

---

## 文件结构总览

```
nba-guessing-game/
├── miniprogram/
│   ├── app.js                    # 小程序入口，全局数据加载
│   ├── app.json                  # 页面注册 + 窗口配置
│   ├── app.wxss                  # 全局样式
│   ├── pages/
│   │   ├── index/                # 首页 — 模式/难度选择
│   │   │   ├── index.js
│   │   │   ├── index.wxml
│   │   │   └── index.wxss
│   │   ├── game/                 # 游戏页 — 核心交互
│   │   │   ├── game.js
│   │   │   ├── game.wxml
│   │   │   └── game.wxss
│   │   └── result/               # 结果页 — 猜中展示
│   │       ├── result.js
│   │       ├── result.wxml
│   │       └── result.wxss
│   ├── utils/
│   │   ├── similarity.js         # 15 维相似度计算引擎
│   │   ├── autocomplete.js       # 球员名模糊匹配 + 验证
│   │   └── daily.js              # 每日挑战种子生成
│   └── data/
│       └── players.json          # 球员数据库
├── scripts/
│   └── build_data.py             # 数据采集与生成
├── tests/
│   ├── test_similarity.js        # 相似度引擎单元测试
│   └── test_autocomplete.js      # 自动补全单元测试
├── docs/superpowers/
│   ├── specs/2026-06-01-nba-guessing-game-design.md
│   └── plans/2026-06-01-nba-guessing-game-plan.md
├── .gitignore
└── README.md
```

---

### Task 1: 项目脚手架 + 全局配置

**Files:**
- Create: `miniprogram/app.json`
- Create: `miniprogram/app.js`
- Create: `miniprogram/app.wxss`
- Create: `.gitignore`

- [ ] **Step 1: 创建小程序入口配置 app.json**

```json
{
  "pages": [
    "pages/index/index",
    "pages/game/game",
    "pages/result/result"
  ],
  "window": {
    "navigationBarTitleText": "NBA 猜词",
    "navigationBarBackgroundColor": "#1a1a2e",
    "navigationBarTextStyle": "white",
    "backgroundColor": "#0f0f1a"
  },
  "sitemapLocation": "sitemap.json"
}
```

- [ ] **Step 2: 创建 app.js — 全局数据加载**

```javascript
App({
  globalData: {
    players: [],
    playersMap: {}   // { name_en: playerObject } 快速查找
  },

  onLaunch() {
    // 加载球员数据到全局
    const players = require('./data/players.json')
    this.globalData.players = players
    players.forEach(p => {
      this.globalData.playersMap[p.name_en] = p
    })
  }
})
```

- [ ] **Step 3: 创建 app.wxss — 全局样式**

```css
page {
  background-color: #0f0f1a;
  color: #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.container {
  padding: 20rpx 30rpx;
  min-height: 100vh;
}

.btn-primary {
  background-color: #e94560;
  color: white;
  border-radius: 12rpx;
  padding: 24rpx 0;
  text-align: center;
  font-size: 32rpx;
  font-weight: 600;
  margin: 20rpx 0;
}

.btn-secondary {
  background-color: #16213e;
  color: #e0e0e0;
  border-radius: 12rpx;
  padding: 24rpx 0;
  text-align: center;
  font-size: 32rpx;
  margin: 20rpx 0;
  border: 2rpx solid #2a2a4a;
}
```

- [ ] **Step 4: 创建 .gitignore**

```
miniprogram/data/players.json
__pycache__/
*.pyc
.DS_Store
node_modules/
```

- [ ] **Step 5: 创建目录结构**

Run: `mkdir -p miniprogram/pages/index miniprogram/pages/game miniprogram/pages/result miniprogram/utils miniprogram/data scripts tests`

- [ ] **Step 6: 提交**

```bash
git add miniprogram/app.json miniprogram/app.js miniprogram/app.wxss .gitignore
git commit -m "feat: add mini program scaffold and global config"
```

---

### Task 2: 手工测试数据集（20 名球员）

**Files:**
- Create: `miniprogram/data/players.json`

> **说明：** 先手工构建 20 名球员的完整数据，覆盖三种难度档位，用于开发调试。后期由 build_data.py 替换为全量数据。players.json 在 .gitignore 中排除，此文件仅用于开发。

- [ ] **Step 1: 创建包含 20 名球员的测试数据集**

```json
[
  {
    "id": "lebron-james",
    "name": "勒布朗·詹姆斯",
    "name_en": "LeBron James",
    "position": "SF",
    "height": 206,
    "weight": 113,
    "nationality": "美国",
    "college": null,
    "draft_year": 2003,
    "draft_pick": 1,
    "career_start": 2003,
    "career_end": null,
    "jersey_numbers": [23, 6],
    "teams": [
      { "team": "骑士", "start": 2003, "end": 2010 },
      { "team": "热火", "start": 2010, "end": 2014 },
      { "team": "骑士", "start": 2014, "end": 2018 },
      { "team": "湖人", "start": 2018, "end": null }
    ],
    "honors": {
      "mvp": 4,
      "championships": 4,
      "all_star": 20,
      "all_nba_first": 13,
      "hall_of_fame": false
    },
    "play_style": "全能组织前锋",
    "career_stats": { "ppg": 27.1, "rpg": 7.5, "apg": 7.4 },
    "notable_relations": [
      { "player_id": "dwyane-wade", "relation": "队友" },
      { "player_id": "kyrie-irving", "relation": "队友" },
      { "player_id": "stephen-curry", "relation": "宿敌" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "dwyane-wade",
    "name": "德怀恩·韦德",
    "name_en": "Dwyane Wade",
    "position": "SG",
    "height": 193,
    "weight": 100,
    "nationality": "美国",
    "college": "马奎特大学",
    "draft_year": 2003,
    "draft_pick": 5,
    "career_start": 2003,
    "career_end": 2019,
    "jersey_numbers": [3, 9],
    "teams": [
      { "team": "热火", "start": 2003, "end": 2016 },
      { "team": "公牛", "start": 2016, "end": 2017 },
      { "team": "骑士", "start": 2017, "end": 2018 },
      { "team": "热火", "start": 2018, "end": 2019 }
    ],
    "honors": {
      "mvp": 0,
      "championships": 3,
      "all_star": 13,
      "all_nba_first": 2,
      "hall_of_fame": true
    },
    "play_style": "得分后卫",
    "career_stats": { "ppg": 22.0, "rpg": 4.7, "apg": 5.4 },
    "notable_relations": [
      { "player_id": "lebron-james", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "yao-ming",
    "name": "姚明",
    "name_en": "Yao Ming",
    "position": "C",
    "height": 229,
    "weight": 141,
    "nationality": "中国",
    "college": null,
    "draft_year": 2002,
    "draft_pick": 1,
    "career_start": 2002,
    "career_end": 2011,
    "jersey_numbers": [11],
    "teams": [
      { "team": "火箭", "start": 2002, "end": 2011 }
    ],
    "honors": {
      "mvp": 0,
      "championships": 0,
      "all_star": 8,
      "all_nba_first": 0,
      "hall_of_fame": true
    },
    "play_style": "传统中锋",
    "career_stats": { "ppg": 19.0, "rpg": 9.2, "apg": 1.6 },
    "notable_relations": [],
    "difficulty_tier": 1
  },
  {
    "id": "stephen-curry",
    "name": "斯蒂芬·库里",
    "name_en": "Stephen Curry",
    "position": "PG",
    "height": 188,
    "weight": 84,
    "nationality": "美国",
    "college": "戴维森学院",
    "draft_year": 2009,
    "draft_pick": 7,
    "career_start": 2009,
    "career_end": null,
    "jersey_numbers": [30],
    "teams": [
      { "team": "勇士", "start": 2009, "end": null }
    ],
    "honors": {
      "mvp": 2,
      "championships": 4,
      "all_star": 10,
      "all_nba_first": 4,
      "hall_of_fame": false
    },
    "play_style": "三分射手",
    "career_stats": { "ppg": 24.8, "rpg": 4.7, "apg": 6.4 },
    "notable_relations": [
      { "player_id": "lebron-james", "relation": "宿敌" },
      { "player_id": "kevin-durant", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "kevin-durant",
    "name": "凯文·杜兰特",
    "name_en": "Kevin Durant",
    "position": "SF",
    "height": 211,
    "weight": 109,
    "nationality": "美国",
    "college": "德克萨斯大学",
    "draft_year": 2007,
    "draft_pick": 2,
    "career_start": 2007,
    "career_end": null,
    "jersey_numbers": [35, 7],
    "teams": [
      { "team": "雷霆", "start": 2007, "end": 2016 },
      { "team": "勇士", "start": 2016, "end": 2019 },
      { "team": "篮网", "start": 2019, "end": 2023 },
      { "team": "太阳", "start": 2023, "end": null }
    ],
    "honors": {
      "mvp": 1,
      "championships": 2,
      "all_star": 14,
      "all_nba_first": 6,
      "hall_of_fame": false
    },
    "play_style": "全能得分手",
    "career_stats": { "ppg": 27.3, "rpg": 7.0, "apg": 4.4 },
    "notable_relations": [
      { "player_id": "stephen-curry", "relation": "队友" },
      { "player_id": "lebron-james", "relation": "宿敌" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "kobe-bryant",
    "name": "科比·布莱恩特",
    "name_en": "Kobe Bryant",
    "position": "SG",
    "height": 198,
    "weight": 96,
    "nationality": "美国",
    "college": null,
    "draft_year": 1996,
    "draft_pick": 13,
    "career_start": 1996,
    "career_end": 2016,
    "jersey_numbers": [8, 24],
    "teams": [
      { "team": "湖人", "start": 1996, "end": 2016 }
    ],
    "honors": {
      "mvp": 1,
      "championships": 5,
      "all_star": 18,
      "all_nba_first": 11,
      "hall_of_fame": true
    },
    "play_style": "得分后卫",
    "career_stats": { "ppg": 25.0, "rpg": 5.2, "apg": 4.7 },
    "notable_relations": [
      { "player_id": "shaquille-oneal", "relation": "队友" },
      { "player_id": "pau-gasol", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "shaquille-oneal",
    "name": "沙奎尔·奥尼尔",
    "name_en": "Shaquille O'Neal",
    "position": "C",
    "height": 216,
    "weight": 147,
    "nationality": "美国",
    "college": "路易斯安那州立大学",
    "draft_year": 1992,
    "draft_pick": 1,
    "career_start": 1992,
    "career_end": 2011,
    "jersey_numbers": [32, 34, 33, 36],
    "teams": [
      { "team": "魔术", "start": 1992, "end": 1996 },
      { "team": "湖人", "start": 1996, "end": 2004 },
      { "team": "热火", "start": 2004, "end": 2008 },
      { "team": "太阳", "start": 2008, "end": 2009 },
      { "team": "骑士", "start": 2009, "end": 2010 },
      { "team": "凯尔特人", "start": 2010, "end": 2011 }
    ],
    "honors": {
      "mvp": 1,
      "championships": 4,
      "all_star": 15,
      "all_nba_first": 8,
      "hall_of_fame": true
    },
    "play_style": "统治型中锋",
    "career_stats": { "ppg": 23.7, "rpg": 10.9, "apg": 2.5 },
    "notable_relations": [
      { "player_id": "kobe-bryant", "relation": "队友" },
      { "player_id": "dwyane-wade", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "giannis-antetokounmpo",
    "name": "扬尼斯·阿德托昆博",
    "name_en": "Giannis Antetokounmpo",
    "position": "PF",
    "height": 211,
    "weight": 110,
    "nationality": "希腊",
    "college": null,
    "draft_year": 2013,
    "draft_pick": 15,
    "career_start": 2013,
    "career_end": null,
    "jersey_numbers": [34],
    "teams": [
      { "team": "雄鹿", "start": 2013, "end": null }
    ],
    "honors": {
      "mvp": 2,
      "championships": 1,
      "all_star": 8,
      "all_nba_first": 6,
      "hall_of_fame": false
    },
    "play_style": "全能前锋",
    "career_stats": { "ppg": 23.4, "rpg": 9.8, "apg": 4.9 },
    "notable_relations": [],
    "difficulty_tier": 1
  },
  {
    "id": "nikola-jokic",
    "name": "尼古拉·约基奇",
    "name_en": "Nikola Jokic",
    "position": "C",
    "height": 211,
    "weight": 129,
    "nationality": "塞尔维亚",
    "college": null,
    "draft_year": 2014,
    "draft_pick": 41,
    "career_start": 2015,
    "career_end": null,
    "jersey_numbers": [15],
    "teams": [
      { "team": "掘金", "start": 2015, "end": null }
    ],
    "honors": {
      "mvp": 3,
      "championships": 1,
      "all_star": 6,
      "all_nba_first": 4,
      "hall_of_fame": false
    },
    "play_style": "组织中锋",
    "career_stats": { "ppg": 21.0, "rpg": 10.8, "apg": 7.0 },
    "notable_relations": [],
    "difficulty_tier": 1
  },
  {
    "id": "tim-duncan",
    "name": "蒂姆·邓肯",
    "name_en": "Tim Duncan",
    "position": "PF",
    "height": 211,
    "weight": 113,
    "nationality": "美国",
    "college": "维克森林大学",
    "draft_year": 1997,
    "draft_pick": 1,
    "career_start": 1997,
    "career_end": 2016,
    "jersey_numbers": [21],
    "teams": [
      { "team": "马刺", "start": 1997, "end": 2016 }
    ],
    "honors": {
      "mvp": 2,
      "championships": 5,
      "all_star": 15,
      "all_nba_first": 10,
      "hall_of_fame": true
    },
    "play_style": "全能大前锋",
    "career_stats": { "ppg": 19.0, "rpg": 10.8, "apg": 3.0 },
    "notable_relations": [
      { "player_id": "tony-parker", "relation": "队友" },
      { "player_id": "manu-ginobili", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "tony-parker",
    "name": "托尼·帕克",
    "name_en": "Tony Parker",
    "position": "PG",
    "height": 188,
    "weight": 84,
    "nationality": "法国",
    "college": null,
    "draft_year": 2001,
    "draft_pick": 28,
    "career_start": 2001,
    "career_end": 2019,
    "jersey_numbers": [9],
    "teams": [
      { "team": "马刺", "start": 2001, "end": 2018 },
      { "team": "黄蜂", "start": 2018, "end": 2019 }
    ],
    "honors": {
      "mvp": 0,
      "championships": 4,
      "all_star": 6,
      "all_nba_first": 0,
      "hall_of_fame": true
    },
    "play_style": "组织后卫",
    "career_stats": { "ppg": 15.5, "rpg": 2.7, "apg": 5.6 },
    "notable_relations": [
      { "player_id": "tim-duncan", "relation": "队友" },
      { "player_id": "manu-ginobili", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "manu-ginobili",
    "name": "马努·吉诺比利",
    "name_en": "Manu Ginobili",
    "position": "SG",
    "height": 198,
    "weight": 93,
    "nationality": "阿根廷",
    "college": null,
    "draft_year": 1999,
    "draft_pick": 57,
    "career_start": 2002,
    "career_end": 2018,
    "jersey_numbers": [20],
    "teams": [
      { "team": "马刺", "start": 2002, "end": 2018 }
    ],
    "honors": {
      "mvp": 0,
      "championships": 4,
      "all_star": 2,
      "all_nba_first": 0,
      "hall_of_fame": true
    },
    "play_style": "第六人得分手",
    "career_stats": { "ppg": 13.3, "rpg": 3.5, "apg": 3.8 },
    "notable_relations": [
      { "player_id": "tim-duncan", "relation": "队友" },
      { "player_id": "tony-parker", "relation": "队友" }
    ],
    "difficulty_tier": 2
  },
  {
    "id": "kyrie-irving",
    "name": "凯里·欧文",
    "name_en": "Kyrie Irving",
    "position": "PG",
    "height": 188,
    "weight": 88,
    "nationality": "美国",
    "college": "杜克大学",
    "draft_year": 2011,
    "draft_pick": 1,
    "career_start": 2011,
    "career_end": null,
    "jersey_numbers": [2, 11],
    "teams": [
      { "team": "骑士", "start": 2011, "end": 2017 },
      { "team": "凯尔特人", "start": 2017, "end": 2019 },
      { "team": "篮网", "start": 2019, "end": 2023 },
      { "team": "独行侠", "start": 2023, "end": null }
    ],
    "honors": {
      "mvp": 0,
      "championships": 1,
      "all_star": 8,
      "all_nba_first": 0,
      "hall_of_fame": false
    },
    "play_style": "控球得分后卫",
    "career_stats": { "ppg": 23.6, "rpg": 4.0, "apg": 5.7 },
    "notable_relations": [
      { "player_id": "lebron-james", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "james-harden",
    "name": "詹姆斯·哈登",
    "name_en": "James Harden",
    "position": "SG",
    "height": 196,
    "weight": 100,
    "nationality": "美国",
    "college": "亚利桑那州立大学",
    "draft_year": 2009,
    "draft_pick": 3,
    "career_start": 2009,
    "career_end": null,
    "jersey_numbers": [13, 1],
    "teams": [
      { "team": "雷霆", "start": 2009, "end": 2012 },
      { "team": "火箭", "start": 2012, "end": 2021 },
      { "team": "篮网", "start": 2021, "end": 2022 },
      { "team": "76人", "start": 2022, "end": 2023 },
      { "team": "快船", "start": 2023, "end": null }
    ],
    "honors": {
      "mvp": 1,
      "championships": 0,
      "all_star": 10,
      "all_nba_first": 6,
      "hall_of_fame": false
    },
    "play_style": "持球大核心",
    "career_stats": { "ppg": 24.1, "rpg": 5.6, "apg": 7.1 },
    "notable_relations": [
      { "player_id": "kevin-durant", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "russell-westbrook",
    "name": "拉塞尔·威斯布鲁克",
    "name_en": "Russell Westbrook",
    "position": "PG",
    "height": 191,
    "weight": 91,
    "nationality": "美国",
    "college": "加州大学洛杉矶分校",
    "draft_year": 2008,
    "draft_pick": 4,
    "career_start": 2008,
    "career_end": null,
    "jersey_numbers": [0, 4],
    "teams": [
      { "team": "雷霆", "start": 2008, "end": 2019 },
      { "team": "火箭", "start": 2019, "end": 2020 },
      { "team": "奇才", "start": 2020, "end": 2021 },
      { "team": "湖人", "start": 2021, "end": 2023 },
      { "team": "快船", "start": 2023, "end": 2024 },
      { "team": "掘金", "start": 2024, "end": null }
    ],
    "honors": {
      "mvp": 1,
      "championships": 0,
      "all_star": 9,
      "all_nba_first": 2,
      "hall_of_fame": false
    },
    "play_style": "爆发型控卫",
    "career_stats": { "ppg": 21.7, "rpg": 7.1, "apg": 8.1 },
    "notable_relations": [
      { "player_id": "kevin-durant", "relation": "队友" },
      { "player_id": "james-harden", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "pau-gasol",
    "name": "保罗·加索尔",
    "name_en": "Pau Gasol",
    "position": "PF",
    "height": 213,
    "weight": 113,
    "nationality": "西班牙",
    "college": null,
    "draft_year": 2001,
    "draft_pick": 3,
    "career_start": 2001,
    "career_end": 2019,
    "jersey_numbers": [16, 17],
    "teams": [
      { "team": "灰熊", "start": 2001, "end": 2008 },
      { "team": "湖人", "start": 2008, "end": 2014 },
      { "team": "公牛", "start": 2014, "end": 2016 },
      { "team": "马刺", "start": 2016, "end": 2019 },
      { "team": "雄鹿", "start": 2019, "end": 2019 }
    ],
    "honors": {
      "mvp": 0,
      "championships": 2,
      "all_star": 6,
      "all_nba_first": 0,
      "hall_of_fame": true
    },
    "play_style": "技术型大前锋",
    "career_stats": { "ppg": 17.0, "rpg": 9.2, "apg": 3.2 },
    "notable_relations": [
      { "player_id": "kobe-bryant", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "kawhi-leonard",
    "name": "科怀·伦纳德",
    "name_en": "Kawhi Leonard",
    "position": "SF",
    "height": 201,
    "weight": 102,
    "nationality": "美国",
    "college": "圣迭戈州立大学",
    "draft_year": 2011,
    "draft_pick": 15,
    "career_start": 2011,
    "career_end": null,
    "jersey_numbers": [2],
    "teams": [
      { "team": "马刺", "start": 2011, "end": 2018 },
      { "team": "猛龙", "start": 2018, "end": 2019 },
      { "team": "快船", "start": 2019, "end": null }
    ],
    "honors": {
      "mvp": 0,
      "championships": 2,
      "all_star": 6,
      "all_nba_first": 3,
      "hall_of_fame": false
    },
    "play_style": "双向全能前锋",
    "career_stats": { "ppg": 20.0, "rpg": 6.4, "apg": 3.0 },
    "notable_relations": [
      { "player_id": "tim-duncan", "relation": "队友" }
    ],
    "difficulty_tier": 1
  },
  {
    "id": "damian-lillard",
    "name": "达米安·利拉德",
    "name_en": "Damian Lillard",
    "position": "PG",
    "height": 188,
    "weight": 88,
    "nationality": "美国",
    "college": "韦伯州立大学",
    "draft_year": 2012,
    "draft_pick": 6,
    "career_start": 2012,
    "career_end": null,
    "jersey_numbers": [0],
    "teams": [
      { "team": "开拓者", "start": 2012, "end": 2023 },
      { "team": "雄鹿", "start": 2023, "end": null }
    ],
    "honors": {
      "mvp": 0,
      "championships": 0,
      "all_star": 8,
      "all_nba_first": 1,
      "hall_of_fame": false
    },
    "play_style": "得分型控卫",
    "career_stats": { "ppg": 25.1, "rpg": 4.2, "apg": 6.7 },
    "notable_relations": [],
    "difficulty_tier": 1
  },
  {
    "id": "dirk-nowitzki",
    "name": "德克·诺维茨基",
    "name_en": "Dirk Nowitzki",
    "position": "PF",
    "height": 213,
    "weight": 111,
    "nationality": "德国",
    "college": null,
    "draft_year": 1998,
    "draft_pick": 9,
    "career_start": 1998,
    "career_end": 2019,
    "jersey_numbers": [41],
    "teams": [
      { "team": "独行侠", "start": 1998, "end": 2019 }
    ],
    "honors": {
      "mvp": 1,
      "championships": 1,
      "all_star": 14,
      "all_nba_first": 4,
      "hall_of_fame": true
    },
    "play_style": "投射型大前锋",
    "career_stats": { "ppg": 20.7, "rpg": 7.5, "apg": 2.4 },
    "notable_relations": [],
    "difficulty_tier": 1
  },
  {
    "id": "alex-caruso",
    "name": "亚历克斯·卡鲁索",
    "name_en": "Alex Caruso",
    "position": "SG",
    "height": 196,
    "weight": 84,
    "nationality": "美国",
    "college": "德克萨斯农工大学",
    "draft_year": 2016,
    "draft_pick": null,
    "career_start": 2017,
    "career_end": null,
    "jersey_numbers": [4, 6],
    "teams": [
      { "team": "湖人", "start": 2017, "end": 2021 },
      { "team": "公牛", "start": 2021, "end": 2024 },
      { "team": "雷霆", "start": 2024, "end": null }
    ],
    "honors": {
      "mvp": 0,
      "championships": 1,
      "all_star": 0,
      "all_nba_first": 0,
      "hall_of_fame": false
    },
    "play_style": "防守型后卫",
    "career_stats": { "ppg": 6.8, "rpg": 2.9, "apg": 2.9 },
    "notable_relations": [
      { "player_id": "lebron-james", "relation": "队友" }
    ],
    "difficulty_tier": 3
  }
]
```

- [ ] **Step 2: 验证 JSON 格式合法**

Run: `python -c "import json; json.load(open('miniprogram/data/players.json')); print('JSON valid,', len(json.load(open('miniprogram/data/players.json'))), 'players')"`
Expected: `JSON valid, 20 players`

- [ ] **Step 3: 提交**

```bash
git add miniprogram/data/players.json
git commit -m "feat: add 20-player test dataset for development"
```

---

### Task 3: 相似度计算引擎

**Files:**
- Create: `miniprogram/utils/similarity.js`
- Create: `tests/test_similarity.js`

- [ ] **Step 1: 编写失败的测试**

```javascript
// tests/test_similarity.js
// 用 Node.js 运行：node tests/test_similarity.js

const { calculateSimilarity } = require('../miniprogram/utils/similarity.js')

const players = require('../miniprogram/data/players.json')
const byName = {}
players.forEach(p => { byName[p.name_en] = p })

// 测试用例 1：同一个人应该返回 100%
function testSamePlayer() {
  const lebron = byName['LeBron James']
  const result = calculateSimilarity(lebron, lebron)
  console.assert(result.score === 100.0,
    `Same player should be 100%, got ${result.score}%`)
  console.log('✓ testSamePlayer passed')
}

// 测试用例 2：当过队友的应该相似度更高
// LeBron James vs Dwyane Wade（热火队友）
function testTeammatesHigherThanNonTeammates() {
  const lebron = byName['LeBron James']
  const wade = byName['Dwyane Wade']
  const yao = byName['Yao Ming']

  const lebronWade = calculateSimilarity(lebron, wade)
  const lebronYao = calculateSimilarity(lebron, yao)

  console.assert(lebronWade.score > lebronYao.score,
    `LeBron-Wade (${lebronWade.score}%) should be higher than LeBron-Yao (${lebronYao.score}%)`)
  console.log(`✓ LeBron-Wade: ${lebronWade.score}%`)
  console.log(`✓ LeBron-Yao: ${lebronYao.score}%`)
  console.log('✓ testTeammatesHigherThanNonTeammates passed')
}

// 测试用例 3：同位置应该有加成
// LeBron James (SF) vs Kevin Durant (SF) > LeBron James vs Stephen Curry (PG)
function testSamePositionHigherThanDifferent() {
  const lebron = byName['LeBron James']
  const durant = byName['Kevin Durant']
  const curry = byName['Stephen Curry']

  const lebronDurant = calculateSimilarity(lebron, durant)
  const lebronCurry = calculateSimilarity(lebron, curry)

  // 只检查位置维度的单独分数（通过 details 查看）
  console.log(`✓ LeBron-Durant position: ${lebronDurant.details.position}`)
  console.log(`✓ LeBron-Curry position: ${lebronCurry.details.position}`)
  console.assert(lebronDurant.details.position > lebronCurry.details.position,
    'Same position should score higher on position dimension')
  console.log('✓ testSamePositionHigherThanDifferent passed')
}

// 测试用例 4：提示文字不能为空且应该有内容
function testHintGeneration() {
  const lebron = byName['LeBron James']
  const wade = byName['Dwyane Wade']
  const result = calculateSimilarity(lebron, wade)
  console.assert(typeof result.hint === 'string' && result.hint.length > 0,
    `Hint should be a non-empty string, got: "${result.hint}"`)
  console.log(`✓ Hint: "${result.hint}"`)
  console.log('✓ testHintGeneration passed')
}

// 测试用例 5：不同类型关系测试
function testNotableRelations() {
  const lebron = byName['LeBron James']
  const curry = byName['Stephen Curry']
  const result = calculateSimilarity(lebron, curry)
  console.log(`✓ LeBron-Curry similarity: ${result.score}%`)
  console.log(`✓ LeBron-Curry hint: "${result.hint}"`)
  // notable_relations 维度的分数应该非零（宿敌关系）
  console.assert(result.details.notableRelations > 0,
    'LeBron and Curry should have notable relation score')
  console.log('✓ testNotableRelations passed')
}

// 运行所有测试
testSamePlayer()
testTeammatesHigherThanNonTeammates()
testSamePositionHigherThanDifferent()
testHintGeneration()
testNotableRelations()
console.log('\nAll tests passed!')
```

- [ ] **Step 2: 运行测试验证失败**

Run: `node tests/test_similarity.js`
Expected: 报错 `Cannot find module '../miniprogram/utils/similarity.js'`

- [ ] **Step 3: 编写完整的 similarity.js**

```javascript
// miniprogram/utils/similarity.js

/**
 * 15 维相似度计算引擎
 * 每个维度返回 [0, 1] 的分数，加权求和后转百分比
 */

// 位置邻接表：相邻位置表示打球风格相近
const POSITION_ADJACENCY = {
  'PG': ['PG', 'SG'],
  'SG': ['SG', 'PG', 'SF'],
  'SF': ['SF', 'SG', 'PF'],
  'PF': ['PF', 'SF', 'C'],
  'C':  ['C', 'PF']
}

const WEIGHTS = {
  position:        0.10,
  heightWeight:    0.08,
  teammate:        0.15,
  sameTeam:        0.10,
  playoffMatchup:  0.10,
  honors:          0.08,
  draft:           0.05,
  jerseyNumber:    0.04,
  careerOverlap:   0.06,
  nationalityCollege: 0.04,
  allStarLevel:    0.06,
  playStyle:       0.06,
  hallOfFame:      0.03,
  careerStats:     0.03,
  notableRelations: 0.02
}

// ─── 各维度计算函数 ───

function positionScore(p1, p2) {
  if (p1 === p2) return 1.0
  const adjacent = POSITION_ADJACENCY[p1] || []
  if (adjacent.includes(p2)) return 0.5
  return 0.0
}

function heightWeightScore(h1, w1, h2, w2) {
  // 高斯衰减：身高差和体重差综合评分
  const heightDiff = Math.abs(h1 - h2) / 30.0  // 归一化到 ~[0, 1]
  const weightDiff = Math.abs(w1 - w2) / 40.0
  const combined = (heightDiff + weightDiff) / 2
  return Math.exp(-combined * combined * 2)  // 高斯衰减
}

function teammateScore(teams1, teams2) {
  for (const t1 of teams1) {
    for (const t2 of teams2) {
      if (t1.team === t2.team) {
        // 检查时间重叠
        const start1 = t1.start
        const end1 = t1.end || 2026
        const start2 = t2.start
        const end2 = t2.end || 2026
        if (start1 <= end2 && start2 <= end1) {
          return 1.0
        }
      }
    }
  }
  return 0.0
}

function sameTeamScore(teams1, teams2) {
  // 不同时期同队（如果已经是队友了，这个会额外计分，但权重总和仍然合理）
  const teamsSet1 = new Set(teams1.map(t => t.team))
  const teamsSet2 = new Set(teams2.map(t => t.team))
  let count = 0
  for (const team of teamsSet1) {
    if (teamsSet2.has(team)) count++
  }
  if (count === 0) return 0.0
  // 有共同球队但没有时间重叠（如果有时间重叠，teammateScore 已覆盖）
  // 这里给一个基础分，每多一个共同球队递增
  return Math.min(0.3 + count * 0.2, 1.0)
}

function playoffMatchupScore(p1, p2) {
  // v1 占位：数据采集阶段暂不实现季后赛交手检测
  // 后续 build_data.py 会为每个球员添加 playoff_matchups 字段
  // 当前返回 0，不影响总体得分计算
  return 0.0
}

function honorsScore(h1, h2) {
  let score = 0.0
  let count = 0

  // MVP 级别对比
  const mvpDiff = Math.abs((h1.mvp || 0) - (h2.mvp || 0))
  score += mvpDiff === 0 ? 1.0 : Math.max(0, 1.0 - mvpDiff * 0.3)
  count++

  // 冠军数对比
  const champDiff = Math.abs((h1.championships || 0) - (h2.championships || 0))
  score += champDiff === 0 ? 1.0 : Math.max(0, 1.0 - champDiff * 0.2)
  count++

  return score / count
}

function draftScore(y1, p1, y2, p2) {
  if (y1 !== y2) return 0.0
  // 同届选秀：顺位越接近分越高
  const diff = Math.abs(p1 - p2)
  if (diff === 0) return 1.0
  return Math.max(0, 1.0 - diff / 60.0)
}

function jerseyNumberScore(nums1, nums2) {
  for (const n1 of nums1) {
    if (nums2.includes(n1)) return 1.0
  }
  return 0.0
}

function careerOverlapScore(start1, end1, start2, end2) {
  const e1 = end1 || 2026
  const e2 = end2 || 2026
  const overlapStart = Math.max(start1, start2)
  const overlapEnd = Math.min(e1, e2)
  if (overlapStart > overlapEnd) return 0.0

  const overlap = overlapEnd - overlapStart
  const totalSpan = Math.max(e1, e2) - Math.min(start1, start2)
  if (totalSpan === 0) return 1.0
  return Math.min(1.0, overlap / totalSpan * 2) // 放大系数
}

function nationalityCollegeScore(nat1, col1, nat2, col2) {
  let score = 0.0
  let count = 0

  if (nat1 && nat2) {
    count++
    if (nat1 === nat2) score += 0.6
  }

  if (col1 && col2) {
    count++
    if (col1 === col2) score += 0.8
  }

  if (count === 0) return 0.0
  return Math.min(1.0, score / count)
}

function allStarLevelScore(as1, as2) {
  const level1 = as1 === 0 ? 0 : as1 <= 3 ? 1 : as1 <= 7 ? 2 : 3
  const level2 = as2 === 0 ? 0 : as2 <= 3 ? 1 : as2 <= 7 ? 2 : 3
  if (level1 === level2) return 1.0
  if (Math.abs(level1 - level2) === 1) return 0.6
  return 0.2
}

function playStyleScore(style1, style2) {
  if (!style1 || !style2) return 0.0
  return style1 === style2 ? 1.0 : 0.0
}

function hallOfFameScore(hof1, hof2) {
  return hof1 === hof2 ? 1.0 : 0.0
}

function careerStatsScore(s1, s2) {
  // 将场均 PTS/REB/AST 各分 5 档
  const stats = ['ppg', 'rpg', 'apg']
  const thresholds = {
    ppg: [5, 10, 15, 20, 25],
    rpg: [2, 4, 6, 8, 10],
    apg: [1, 2, 4, 6, 8]
  }

  let total = 0
  for (const key of stats) {
    const v1 = s1?.[key] || 0
    const v2 = s2?.[key] || 0
    const bracket1 = thresholds[key].findIndex(t => v1 < t)
    const bracket2 = thresholds[key].findIndex(t => v2 < t)
    const b1 = bracket1 === -1 ? 5 : bracket1
    const b2 = bracket2 === -1 ? 5 : bracket2
    total += b1 === b2 ? 1.0 : Math.max(0, 1.0 - Math.abs(b1 - b2) * 0.25)
  }
  return total / 3
}

function notableRelationsScore(p1, p2) {
  const rels = p1.notable_relations || []
  for (const rel of rels) {
    if (rel.player_id === p2.id) {
      // 不同关系类型给不同的基础分
      if (rel.relation === '队友') return 1.0
      if (rel.relation === '宿敌') return 0.8
      return 0.6
    }
  }
  return 0.0
}

// ─── 提示生成 ───

const HINT_TEMPLATES = [
  { dim: 'teammate', gen: (g, a) => {
    for (const t1 of g.teams) {
      for (const t2 of a.teams) {
        const s1 = t1.start, e1 = t1.end || 2026, s2 = t2.start, e2 = t2.end || 2026
        if (t1.team === t2.team && s1 <= e2 && s2 <= e1) {
          return `曾与答案在${t1.team}当过队友`
        }
      }
    }
    return null
  }},
  { dim: 'position', gen: (g, a) => {
    if (g.position === a.position) return `位置相同：${g.position}`
    if ((POSITION_ADJACENCY[g.position] || []).includes(a.position)) {
      return `位置接近：${g.position} 和 ${a.position}`
    }
    return `位置不同：${g.position} vs ${a.position}`
  }},
  { dim: 'sameTeam', gen: (g, a) => {
    const teams1 = new Set(g.teams.map(t => t.team))
    const teams2 = new Set(a.teams.map(t => t.team))
    for (const team of teams1) {
      if (teams2.has(team)) return `也曾效力于${team}`
    }
    return null
  }},
  { dim: 'draft', gen: (g, a) => {
    if (g.draft_year === a.draft_year) return `同届选秀（${g.draft_year} 年）`
    return null
  }},
  { dim: 'jerseyNumber', gen: (g, a) => {
    for (const n of g.jersey_numbers) {
      if (a.jersey_numbers.includes(n)) return `曾穿同一个号码 #${n}`
    }
    return null
  }},
  { dim: 'nationalityCollege', gen: (g, a) => {
    if (g.nationality === a.nationality && g.nationality) return `同样来自${g.nationality}`
    if (g.college && g.college === a.college) return `同为${g.college}校友`
    return null
  }},
  { dim: 'allStarLevel', gen: (g, a) => '全明星次数相近' },
  { dim: 'playStyle', gen: (g, a) => {
    if (g.play_style === a.play_style) return `球风相似：${g.play_style}`
    return null
  }},
  { dim: 'hallOfFame', gen: (g, a) => {
    if (g.honors.hall_of_fame && a.honors.hall_of_fame) return '同为名人堂成员'
    return null
  }},
  { dim: 'heightWeight', gen: () => '身高体重接近' },
  { dim: 'honors', gen: () => '荣誉级别接近' },
  { dim: 'careerOverlap', gen: () => '职业生涯同时期' },
  { dim: 'careerStats', gen: () => '生涯场均数据相近' },
  { dim: 'notableRelations', gen: (g, a) => {
    const rels = g.notable_relations || []
    for (const rel of rels) {
      if (rel.player_id === a.id) return `与答案有过关联：${rel.relation}`
    }
    return null
  }}
]

function generateHint(guess, answer, scores) {
  // 按分数从高到低遍历维度，返回第一个 score >= 0.5 且有非空提示的
  const sorted = Object.entries(scores)
    .filter(([, v]) => v >= 0.3)
    .sort(([, a], [, b]) => b - a)

  for (const [dim] of sorted) {
    const template = HINT_TEMPLATES.find(t => t.dim === dim)
    if (!template) continue
    const hint = template.gen(guess, answer)
    if (hint) return hint
  }

  return '暂无更多提示'
}

// ─── 主计算函数 ───

function calculateSimilarity(guess, answer) {
  const scores = {}

  scores.position = positionScore(guess.position, answer.position)
  scores.heightWeight = heightWeightScore(guess.height, guess.weight, answer.height, answer.weight)
  scores.teammate = teammateScore(guess.teams, answer.teams)
  scores.sameTeam = sameTeamScore(guess.teams, answer.teams)
  scores.playoffMatchup = playoffMatchupScore(guess, answer)
  scores.honors = honorsScore(guess.honors, answer.honors)
  scores.draft = draftScore(guess.draft_year, guess.draft_pick, answer.draft_year, answer.draft_pick)
  scores.jerseyNumber = jerseyNumberScore(guess.jersey_numbers, answer.jersey_numbers)
  scores.careerOverlap = careerOverlapScore(guess.career_start, guess.career_end, answer.career_start, answer.career_end)
  scores.nationalityCollege = nationalityCollegeScore(guess.nationality, guess.college, answer.nationality, answer.college)
  scores.allStarLevel = allStarLevelScore(guess.honors.all_star, answer.honors.all_star)
  scores.playStyle = playStyleScore(guess.play_style, answer.play_style)
  scores.hallOfFame = hallOfFameScore(guess.honors.hall_of_fame, answer.honors.hall_of_fame)
  scores.careerStats = careerStatsScore(guess.career_stats, answer.career_stats)
  scores.notableRelations = notableRelationsScore(guess, answer)

  // 加权求和
  let total = 0.0
  for (const [dim, score] of Object.entries(scores)) {
    total += score * (WEIGHTS[dim] || 0)
  }

  // 转为百分比，保留一位小数
  const percentage = Math.round(total * 1000) / 10

  // 生成提示
  const hint = generateHint(guess, answer, scores)

  return {
    score: percentage,
    hint,
    details: scores
  }
}

module.exports = { calculateSimilarity }
```

- [ ] **Step 4: 运行测试**

Run: `node tests/test_similarity.js`
Expected: 所有 5 个测试用例通过

- [ ] **Step 5: 提交**

```bash
git add miniprogram/utils/similarity.js tests/test_similarity.js
git commit -m "feat: add 15-dimension similarity calculation engine with tests"
```

---

### Task 4: 球员名自动补全引擎

**Files:**
- Create: `miniprogram/utils/autocomplete.js`
- Create: `tests/test_autocomplete.js`

- [ ] **Step 1: 编写失败的测试**

```javascript
// tests/test_autocomplete.js

const { searchPlayers, validatePlayer } = require('../miniprogram/utils/autocomplete.js')

const players = require('../miniprogram/data/players.json')

// 测试：中文搜索"詹"应该找到 LeBron James
function testChineseSearch() {
  const results = searchPlayers('詹', players)
  console.assert(results.length > 0, 'Should find results for "詹"')
  console.assert(results.some(r => r.name_en === 'LeBron James'),
    'Should find LeBron James when searching "詹"')
  console.log(`✓ testChineseSearch: found ${results.length} results for "詹"`)
}

// 测试：英文搜索"james"应该找到 LeBron James 和 James Harden
function testEnglishSearch() {
  const results = searchPlayers('james', players)
  console.assert(results.some(r => r.name_en === 'LeBron James'), 'Should find LeBron James')
  console.assert(results.some(r => r.name_en === 'James Harden'), 'Should find James Harden')
  console.log(`✓ testEnglishSearch: found ${results.length} results for "james"`)
}

// 测试：精确英文名验证
function testExactValidation() {
  const result = validatePlayer('LeBron James', players)
  console.assert(result !== null, 'Should validate "LeBron James"')
  console.assert(result.name_en === 'LeBron James', 'Should return correct player')
  console.log('✓ testExactValidation passed')
}

// 测试：不存在的球员
function testInvalidPlayer() {
  const result = validatePlayer('Nonexistent Player', players)
  console.assert(result === null, 'Should return null for invalid player')
  console.log('✓ testInvalidPlayer passed')
}

// 测试：结果数量限制
function testResultLimit() {
  const results = searchPlayers('a', players)
  console.assert(results.length <= 10, 'Should limit results to 10')
  console.log(`✓ testResultLimit: returned ${results.length} (max 10)`)
}

testChineseSearch()
testEnglishSearch()
testExactValidation()
testInvalidPlayer()
testResultLimit()
console.log('\nAll autocomplete tests passed!')
```

- [ ] **Step 2: 运行测试验证失败**

Run: `node tests/test_autocomplete.js`
Expected: 报错 `Cannot find module`

- [ ] **Step 3: 编写 autocomplete.js**

```javascript
// miniprogram/utils/autocomplete.js

/**
 * 球员名模糊匹配与验证
 * 支持中英文搜索，返回匹配度最高的前 N 个结果
 */

/**
 * 搜索球员：同时匹配中英文名
 * @param {string} query - 用户输入的搜索词
 * @param {Array} players - 全部球员数组
 * @param {number} limit - 最大返回数量，默认 10
 * @returns {Array} 匹配的球员列表
 */
function searchPlayers(query, players, limit = 10) {
  if (!query || query.trim() === '') return []

  const q = query.trim().toLowerCase()

  const scored = players
    .map(p => ({ player: p, score: matchScore(q, p) }))
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)

  return scored.slice(0, limit).map(r => r.player)
}

/**
 * 计算匹配分数
 */
function matchScore(query, player) {
  const nameEn = player.name_en.toLowerCase()
  const nameCn = player.name || ''

  // 完全匹配英文名 → 最高分
  if (nameEn === query) return 100
  // 英文名以查询开头 → 高分
  if (nameEn.startsWith(query)) return 80
  // 英文名包含查询子串
  if (nameEn.includes(query)) return 60

  // 中文名完全匹配
  if (nameCn === query) return 90
  // 中文名包含查询
  if (nameCn.includes(query)) return 70

  // 英文名首字母匹配（如 "lbj" 匹配 LeBron James）
  const initials = nameEn.split(' ').map(w => w[0]).join('')
  if (initials === query) return 50
  if (initials.startsWith(query)) return 40

  // 英文名单词匹配
  const words = nameEn.split(' ')
  for (const word of words) {
    if (word === query) return 75
    if (word.startsWith(query)) return 55
  }

  return 0
}

/**
 * 验证球员名是否有效
 * @param {string} name - 需要验证的球员名（精确匹配）
 * @param {Array} players - 全部球员数组
 * @returns {Object|null} 匹配的球员对象或 null
 */
function validatePlayer(name, players) {
  if (!name) return null
  const lower = name.trim().toLowerCase()
  return players.find(p => p.name_en.toLowerCase() === lower) || null
}

module.exports = { searchPlayers, validatePlayer }
```

- [ ] **Step 4: 运行测试**

Run: `node tests/test_autocomplete.js`
Expected: 所有 5 个测试用例通过

- [ ] **Step 5: 提交**

```bash
git add miniprogram/utils/autocomplete.js tests/test_autocomplete.js
git commit -m "feat: add player name autocomplete with Chinese/English support"
```

---

### Task 5: 每日挑战种子生成

**Files:**
- Create: `miniprogram/utils/daily.js`

- [ ] **Step 1: 编写 daily.js**

```javascript
// miniprogram/utils/daily.js

/**
 * 每日挑战：基于日期哈希确定当日答案球员
 * 保证同一天所有人看到的是同一个球员
 */

/**
 * 生成 UTC+8 日期字符串，格式 "2026-06-01"
 */
function getTodayKey() {
  const now = new Date()
  // UTC+8 偏移
  const offset = 8 * 60 * 60 * 1000
  const local = new Date(now.getTime() + offset)
  const year = local.getUTCFullYear()
  const month = String(local.getUTCMonth() + 1).padStart(2, '0')
  const day = String(local.getUTCDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 简单字符串哈希 → 整数种子
 */
function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // 转为 32 位整数
  }
  return Math.abs(hash)
}

/**
 * 根据日期获取当日球员索引
 * @param {number} playerCount - 可选球员总数
 * @param {string} dateKey - 日期键（可选，默认今天），格式 "YYYY-MM-DD"
 * @returns {number} 球员在数组中的索引
 */
function getDailyIndex(playerCount, dateKey) {
  const key = dateKey || getTodayKey()
  const seed = hashString(key)
  return seed % playerCount
}

/**
 * 根据难度档位筛选球员池，返回当日答案
 * @param {Array} allPlayers - 全部球员
 * @param {number} difficulty - 难度 1/2/3
 * @returns {Object} 当日答案球员
 */
function getDailyPlayer(allPlayers, difficulty = 1) {
  const pool = allPlayers.filter(p => p.difficulty_tier <= difficulty)
  const index = getDailyIndex(pool.length)
  return pool[index]
}

module.exports = { getTodayKey, hashString, getDailyIndex, getDailyPlayer }
```

- [ ] **Step 2: 提交**

```bash
git add miniprogram/utils/daily.js
git commit -m "feat: add daily challenge seed generator"
```

---

### Task 6: 首页（模式 + 难度选择）

**Files:**
- Create: `miniprogram/pages/index/index.wxml`
- Create: `miniprogram/pages/index/index.js`
- Create: `miniprogram/pages/index/index.wxss`

- [ ] **Step 1: 编写 WXML 模板**

```xml
<!-- miniprogram/pages/index/index.wxml -->
<view class="container">
  <view class="header">
    <text class="logo">🏀</text>
    <text class="title">NBA 猜词</text>
    <text class="subtitle">猜猜今天的 NBA 球员是谁？</text>
  </view>

  <view class="mode-section">
    <view class="mode-card {{mode === 'daily' ? 'active' : ''}}" bindtap="selectMode" data-mode="daily">
      <text class="mode-icon">📅</text>
      <text class="mode-title">每日挑战</text>
      <text class="mode-desc">每天一个球员，大家都猜同一个</text>
    </view>

    <view class="mode-card {{mode === 'unlimited' ? 'active' : ''}}" bindtap="selectMode" data-mode="unlimited">
      <text class="mode-icon">♾️</text>
      <text class="mode-title">无限模式</text>
      <text class="mode-desc">随机球员，猜完继续下一局</text>
    </view>
  </view>

  <view class="difficulty-section">
    <text class="section-label">难度选择</text>
    <view class="difficulty-row">
      <view class="diff-btn {{difficulty === 1 ? 'active' : ''}}" bindtap="selectDifficulty" data-level="1">
        <text>⭐</text>
        <text>球星</text>
      </view>
      <view class="diff-btn {{difficulty === 2 ? 'active' : ''}}" bindtap="selectDifficulty" data-level="2">
        <text>⭐⭐</text>
        <text>知名</text>
      </view>
      <view class="diff-btn {{difficulty === 3 ? 'active' : ''}}" bindtap="selectDifficulty" data-level="3">
        <text>⭐⭐⭐</text>
        <text>全部</text>
      </view>
    </view>
  </view>

  <view class="start-btn" bindtap="startGame">
    <text>开始游戏</text>
  </view>
</view>
```

- [ ] **Step 2: 编写 JS 逻辑**

```javascript
// miniprogram/pages/index/index.js

Page({
  data: {
    mode: 'unlimited',
    difficulty: 1
  },

  selectMode(e) {
    this.setData({ mode: e.currentTarget.dataset.mode })
  },

  selectDifficulty(e) {
    this.setData({ difficulty: parseInt(e.currentTarget.dataset.level) })
  },

  startGame() {
    wx.navigateTo({
      url: `/pages/game/game?mode=${this.data.mode}&difficulty=${this.data.difficulty}`
    })
  }
})
```

- [ ] **Step 3: 编写 WXSS 样式**

```css
/* miniprogram/pages/index/index.wxss */
.header {
  text-align: center;
  padding: 80rpx 0 60rpx;
}

.logo {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #ffffff;
  display: block;
}

.subtitle {
  font-size: 28rpx;
  color: #8888aa;
  margin-top: 10rpx;
  display: block;
}

.mode-section {
  margin: 20rpx 0;
}

.mode-card {
  background-color: #16213e;
  border: 2rpx solid #2a2a4a;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  transition: all 0.2s;
}

.mode-card.active {
  border-color: #e94560;
  background-color: #1a1030;
}

.mode-icon {
  font-size: 40rpx;
  display: block;
  margin-bottom: 10rpx;
}

.mode-title {
  font-size: 32rpx;
  font-weight: 600;
  display: block;
  margin-bottom: 6rpx;
}

.mode-desc {
  font-size: 24rpx;
  color: #8888aa;
}

.difficulty-section {
  margin: 40rpx 0;
}

.section-label {
  font-size: 28rpx;
  color: #8888aa;
  margin-bottom: 16rpx;
  display: block;
}

.difficulty-row {
  display: flex;
  gap: 16rpx;
}

.diff-btn {
  flex: 1;
  background-color: #16213e;
  border: 2rpx solid #2a2a4a;
  border-radius: 12rpx;
  padding: 20rpx 0;
  text-align: center;
  font-size: 26rpx;
  transition: all 0.2s;
}

.diff-btn text {
  display: block;
}

.diff-btn.active {
  border-color: #e94560;
  background-color: #1a1030;
}

.start-btn {
  background-color: #e94560;
  color: white;
  border-radius: 16rpx;
  padding: 28rpx 0;
  text-align: center;
  font-size: 36rpx;
  font-weight: 700;
  margin-top: 60rpx;
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/index/
git commit -m "feat: add home page with mode and difficulty selection"
```

---

### Task 7: 游戏页（核心交互）

**Files:**
- Create: `miniprogram/pages/game/game.wxml`
- Create: `miniprogram/pages/game/game.js`
- Create: `miniprogram/pages/game/game.wxss`

- [ ] **Step 1: 编写 WXML 模板**

```xml
<!-- miniprogram/pages/game/game.wxml -->
<view class="container">
  <!-- 顶部状态栏 -->
  <view class="top-bar">
    <text class="mode-badge">{{mode === 'daily' ? '📅 每日挑战' : '♾️ 无限模式'}}</text>
    <text class="diff-badge">{{difficultyStars}}</text>
  </view>

  <!-- 输入区域（猜中前显示） -->
  <view class="input-section" wx:if="{{!gameOver}}">
    <view class="input-wrapper">
      <input
        class="player-input"
        placeholder="输入球员姓名..."
        value="{{inputValue}}"
        bindinput="onInput"
        bindconfirm="onSubmit"
        focus="{{true}}"
        placeholder-style="color: #555"
      />
    </view>

    <!-- 自动补全下拉 -->
    <view class="suggestions" wx:if="{{suggestions.length > 0}}">
      <view
        class="suggestion-item"
        wx:for="{{suggestions}}"
        wx:key="id"
        bindtap="onSelectSuggestion"
        data-name="{{item.name_en}}"
      >
        <text>{{item.name}}</text>
        <text class="suggestion-en">{{item.name_en}} · {{item.position}}</text>
      </view>
    </view>

    <view class="submit-btn {{inputValue ? 'active' : ''}}" bindtap="onSubmit">
      <text>提交猜测</text>
    </view>
  </view>

  <!-- 猜中结果（猜中后显示） -->
  <view class="success-banner" wx:if="{{gameOver}}">
    <text class="success-emoji">🎉</text>
    <text class="success-text">猜对了！</text>
    <text class="success-player">{{answerName}}</text>
    <text class="success-count">共猜测 {{guesses.length}} 次</text>
    <view class="new-game-btn" bindtap="onNewGame">
      <text>再来一局</text>
    </view>
    <view class="back-btn" bindtap="onBackHome">
      <text>返回首页</text>
    </view>
  </view>

  <!-- 历史猜测列表 -->
  <view class="history-section">
    <text class="history-title">历史猜测</text>
    <view class="guess-list" wx:if="{{guesses.length > 0}}">
      <view
        class="guess-item"
        wx:for="{{guesses}}"
        wx:key="id"
      >
        <view class="guess-rank">
          <text class="rank-num">#{{index + 1}}</text>
        </view>
        <view class="guess-info">
          <text class="guess-name">{{item.player.name}}</text>
          <text class="guess-hint">💡 {{item.hint}}</text>
        </view>
        <view class="guess-score">
          <text class="score-value {{item.score > 70 ? 'score-hot' : item.score > 40 ? 'score-warm' : 'score-cool'}}">
            {{item.score}}%
          </text>
        </view>
      </view>
    </view>
    <view class="empty-hint" wx:else>
      <text>输入球员名开始猜测</text>
    </view>
  </view>

  <!-- 底部计数 -->
  <view class="footer" wx:if="{{!gameOver}}">
    <text>已猜 {{guesses.length}} 次</text>
  </view>
</view>
```

- [ ] **Step 2: 编写 JS 逻辑**

```javascript
// miniprogram/pages/game/game.js

const { calculateSimilarity } = require('../../utils/similarity.js')
const { searchPlayers, validatePlayer } = require('../../utils/autocomplete.js')
const { getDailyPlayer } = require('../../utils/daily.js')

Page({
  data: {
    mode: 'unlimited',
    difficulty: 1,
    difficultyStars: '⭐',
    inputValue: '',
    suggestions: [],
    guesses: [],
    gameOver: false,
    answerName: '',
    allPlayers: [],
    answer: null
  },

  onLoad(options) {
    const mode = options.mode || 'unlimited'
    const difficulty = parseInt(options.difficulty) || 1
    const stars = { 1: '⭐', 2: '⭐⭐', 3: '⭐⭐⭐' }

    // 从全局数据获取球员列表
    const app = getApp()
    const allPlayers = app.globalData.players

    // 按难度筛选
    const pool = allPlayers.filter(p => p.difficulty_tier <= difficulty)

    // 抽选答案
    let answer
    if (mode === 'daily') {
      answer = getDailyPlayer(allPlayers, difficulty)
    } else {
      answer = pool[Math.floor(Math.random() * pool.length)]
    }

    this.setData({
      mode,
      difficulty,
      difficultyStars: stars[difficulty],
      allPlayers,
      answer
    })

    // 调试用（发布时注释掉）
    // console.log('Answer:', answer.name, answer.name_en)
  },

  onInput(e) {
    const value = e.detail.value
    this.setData({ inputValue: value })

    if (value.trim().length > 0) {
      const suggestions = searchPlayers(value, this.data.allPlayers, 8)
      this.setData({ suggestions })
    } else {
      this.setData({ suggestions: [] })
    }
  },

  onSelectSuggestion(e) {
    const name = e.currentTarget.dataset.name
    this.setData({
      inputValue: name,
      suggestions: []
    })
  },

  onSubmit() {
    const name = this.data.inputValue.trim()
    if (!name) return

    const player = validatePlayer(name, this.data.allPlayers)
    if (!player) {
      wx.showToast({ title: '请输入有效的球员名', icon: 'none' })
      return
    }

    // 检查是否已经猜过
    const alreadyGuessed = this.data.guesses.some(
      g => g.player.id === player.id
    )
    if (alreadyGuessed) {
      wx.showToast({ title: '已经猜过这个球员了', icon: 'none' })
      return
    }

    // 计算相似度
    const result = calculateSimilarity(player, this.data.answer)

    // 判断是否猜中
    const isCorrect = player.id === this.data.answer.id

    const newGuess = {
      id: player.id,
      player,
      score: isCorrect ? 100.0 : result.score,
      hint: isCorrect ? '🎉 恭喜猜中！' : result.hint
    }

    // 插入并按相似度降序排列
    const guesses = [...this.data.guesses, newGuess]
      .sort((a, b) => b.score - a.score)

    this.setData({
      guesses,
      inputValue: '',
      suggestions: [],
      gameOver: isCorrect,
      answerName: isCorrect ? this.data.answer.name : ''
    })

    if (!isCorrect) {
      wx.showToast({ title: `${result.score}% 相似`, icon: 'none', duration: 1500 })
    }
  },

  onNewGame() {
    // 重新随机选答案
    const pool = this.data.allPlayers.filter(
      p => p.difficulty_tier <= this.data.difficulty
    )
    const answer = pool[Math.floor(Math.random() * pool.length)]

    this.setData({
      inputValue: '',
      suggestions: [],
      guesses: [],
      gameOver: false,
      answerName: '',
      answer
    })
  },

  onBackHome() {
    wx.navigateBack()
  }
})
```

- [ ] **Step 3: 编写 WXSS 样式**

```css
/* miniprogram/pages/game/game.wxss */

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  margin-bottom: 30rpx;
}

.mode-badge, .diff-badge {
  font-size: 26rpx;
  color: #aaa;
}

.input-section {
  margin-bottom: 30rpx;
}

.input-wrapper {
  background-color: #16213e;
  border: 2rpx solid #2a2a4a;
  border-radius: 12rpx;
  padding: 0 24rpx;
}

.player-input {
  height: 88rpx;
  font-size: 32rpx;
  color: #fff;
  width: 100%;
}

.suggestions {
  background-color: #16213e;
  border: 2rpx solid #2a2a4a;
  border-top: none;
  border-radius: 0 0 12rpx 12rpx;
  overflow: hidden;
}

.suggestion-item {
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #2a2a4a;
  display: flex;
  justify-content: space-between;
  font-size: 28rpx;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-en {
  color: #8888aa;
  font-size: 24rpx;
}

.submit-btn {
  background-color: #333355;
  color: #888;
  border-radius: 12rpx;
  padding: 24rpx 0;
  text-align: center;
  font-size: 32rpx;
  font-weight: 600;
  margin-top: 20rpx;
  transition: all 0.2s;
}

.submit-btn.active {
  background-color: #e94560;
  color: white;
}

/* 猜中成功横幅 */
.success-banner {
  text-align: center;
  padding: 40rpx 0;
  background-color: #16213e;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
  border: 2rpx solid #e94560;
}

.success-emoji { font-size: 64rpx; display: block; }
.success-text { font-size: 32rpx; color: #e94560; display: block; margin: 10rpx 0; }
.success-player { font-size: 40rpx; font-weight: 700; display: block; }
.success-count { font-size: 26rpx; color: #888; display: block; margin-top: 10rpx; }

.new-game-btn {
  background-color: #e94560;
  color: white;
  border-radius: 12rpx;
  padding: 20rpx 0;
  margin: 24rpx 40rpx 10rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.back-btn {
  background-color: transparent;
  color: #888;
  border: 2rpx solid #2a2a4a;
  border-radius: 12rpx;
  padding: 20rpx 0;
  margin: 10rpx 40rpx;
  font-size: 28rpx;
}

/* 历史列表 */
.history-section {
  flex: 1;
}

.history-title {
  font-size: 28rpx;
  color: #888;
  margin-bottom: 16rpx;
  display: block;
}

.empty-hint {
  text-align: center;
  color: #555;
  font-size: 28rpx;
  padding: 60rpx 0;
}

.guess-item {
  background-color: #16213e;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 12rpx;
  display: flex;
  align-items: center;
  border: 1rpx solid #2a2a4a;
}

.guess-rank {
  width: 60rpx;
}

.rank-num {
  font-size: 28rpx;
  color: #666;
  font-weight: 600;
}

.guess-info {
  flex: 1;
}

.guess-name {
  font-size: 30rpx;
  font-weight: 500;
  display: block;
  margin-bottom: 4rpx;
}

.guess-hint {
  font-size: 24rpx;
  color: #8888aa;
}

.guess-score {
  margin-left: 16rpx;
}

.score-value {
  font-size: 32rpx;
  font-weight: 700;
}

.score-hot { color: #e94560; }
.score-warm { color: #f0a050; }
.score-cool { color: #6666aa; }

.footer {
  text-align: center;
  padding: 30rpx 0;
  color: #555;
  font-size: 26rpx;
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/game/
git commit -m "feat: add game page with input, autocomplete, similarity display"
```

---

### Task 8: 结果页（猜中后详情）

**Files:**
- Create: `miniprogram/pages/result/result.wxml`
- Create: `miniprogram/pages/result/result.js`
- Create: `miniprogram/pages/result/result.wxss`

> **说明：** 结果页作为独立的详情展示页面（可以从游戏页的"查看详情"按钮进入），展示答案球员的完整信息。

- [ ] **Step 1: 编写 WXML 模板**

```xml
<!-- miniprogram/pages/result/result.wxml -->
<view class="container">
  <view class="result-header">
    <text class="result-emoji">🎉</text>
    <text class="result-title">猜对了！</text>
  </view>

  <view class="player-card">
    <text class="player-name">{{player.name}}</text>
    <text class="player-en">{{player.name_en}}</text>

    <view class="info-grid">
      <view class="info-item">
        <text class="info-label">位置</text>
        <text class="info-value">{{player.position}}</text>
      </view>
      <view class="info-item">
        <text class="info-label">身高/体重</text>
        <text class="info-value">{{player.height}}cm / {{player.weight}}kg</text>
      </view>
      <view class="info-item">
        <text class="info-label">选秀</text>
        <text class="info-value">{{player.draft_year}}年 第{{player.draft_pick}}顺位</text>
      </view>
      <view class="info-item">
        <text class="info-label">国籍</text>
        <text class="info-value">{{player.nationality}}</text>
      </view>
    </view>

    <view class="honors-section" wx:if="{{player.honors}}">
      <text class="section-title">荣誉</text>
      <view class="honor-tags">
        <text class="honor-tag" wx:if="{{player.honors.mvp > 0}}">MVP ×{{player.honors.mvp}}</text>
        <text class="honor-tag" wx:if="{{player.honors.championships > 0}}">🏆 ×{{player.honors.championships}}</text>
        <text class="honor-tag" wx:if="{{player.honors.all_star > 0}}">全明星 ×{{player.honors.all_star}}</text>
        <text class="honor-tag" wx:if="{{player.honors.hall_of_fame}}">名人堂</text>
      </view>
    </view>

    <view class="stats-section" wx:if="{{player.career_stats}}">
      <text class="section-title">生涯场均</text>
      <view class="stats-row">
        <text>{{player.career_stats.ppg}} 分</text>
        <text>{{player.career_stats.rpg}} 板</text>
        <text>{{player.career_stats.apg}} 助</text>
      </view>
    </view>
  </view>

  <view class="guess-summary">
    <text>共猜测 {{guessCount}} 次</text>
  </view>

  <view class="action-btns">
    <view class="btn-primary" bindtap="onNewGame">
      <text>再来一局</text>
    </view>
    <view class="btn-secondary" bindtap="onBackHome">
      <text>返回首页</text>
    </view>
  </view>
</view>
```

- [ ] **Step 2: 编写 JS 逻辑**

```javascript
// miniprogram/pages/result/result.js

Page({
  data: {
    player: {},
    guessCount: 0
  },

  onLoad(options) {
    // 从全局数据中获取球员信息
    const app = getApp()
    const player = app.globalData.playersMap[options.id] || {}
    const guessCount = parseInt(options.count) || 0

    this.setData({ player, guessCount })
  },

  onNewGame() {
    wx.navigateTo({ url: '/pages/game/game?mode=unlimited&difficulty=1' })
  },

  onBackHome() {
    wx.navigateBack({ delta: 2 })
  }
})
```

- [ ] **Step 3: 编写 WXSS 样式**

```css
/* miniprogram/pages/result/result.wxss */

.result-header {
  text-align: center;
  padding: 60rpx 0 40rpx;
}

.result-emoji { font-size: 80rpx; display: block; }
.result-title { font-size: 40rpx; font-weight: 700; display: block; margin-top: 10rpx; }

.player-card {
  background-color: #16213e;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.player-name { font-size: 40rpx; font-weight: 700; display: block; }
.player-en { font-size: 28rpx; color: #888; display: block; margin: 6rpx 0 24rpx; }

.info-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.info-item {
  flex: 0 0 calc(50% - 8rpx);
  background-color: #0f0f1a;
  border-radius: 8rpx;
  padding: 16rpx;
}

.info-label { font-size: 22rpx; color: #666; display: block; }
.info-value { font-size: 28rpx; font-weight: 500; display: block; margin-top: 4rpx; }

.section-title {
  font-size: 24rpx;
  color: #888;
  margin: 24rpx 0 12rpx;
  display: block;
}

.honor-tags { display: flex; flex-wrap: wrap; gap: 10rpx; }
.honor-tag {
  background-color: #e94560;
  color: white;
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.stats-row {
  display: flex;
  gap: 30rpx;
  font-size: 28rpx;
  font-weight: 600;
}

.guess-summary {
  text-align: center;
  color: #888;
  font-size: 28rpx;
  margin: 20rpx 0;
}

.action-btns {
  margin-top: 40rpx;
}
```

- [ ] **Step 4: 提交**

```bash
git add miniprogram/pages/result/
git commit -m "feat: add result page with player details and stats"
```

---

### Task 9: 数据构建脚本（Python）

**Files:**
- Create: `scripts/build_data.py`

> **说明：** 此脚本用于从 Kaggle V2 数据集 + 手工补充数据生成完整的 players.json。v1 阶段生成 20 球员测试集即可投入使用。后续可扩展为爬取全量数据。

- [ ] **Step 1: 编写 build_data.py**

```python
# scripts/build_data.py
"""
NBA 球员数据构建脚本
用途：从数据源生成 miniprogram/data/players.json
v1：手工维护核心球员数据，脚本负责校验和导出

数据来源计划：
- Kaggle V2 NBA Player Database (基础字段)
- Basketball-Reference (队友/荣誉/季后赛 补充)
- 手工整理的 notable_relations

当前 v1 版本：
- 运行此脚本会校验 TEST_PLAYERS 的数据完整性
- 输出到 miniprogram/data/players.json
"""

import json
import sys
from pathlib import Path

# ─── v1 测试数据集（20 球员） ───
# 后续可以从 CSV/API 中导入替换
TEST_PLAYERS = []  # 留空，从已有的 players.json 读取并仅做校验

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


def validate_player(p, index):
    """校验单个球员数据的完整性"""
    errors = []

    # 必填字段检查
    for field in REQUIRED_FIELDS:
        if field not in p:
            errors.append(f"缺少必填字段: {field}")

    if errors:
        return errors

    # 位置校验
    if p["position"] not in VALID_POSITIONS:
        errors.append(f"无效位置: {p['position']}")

    # 数值范围校验
    if not (150 <= p["height"] <= 250):
        errors.append(f"身高异常: {p['height']}cm")
    if not (60 <= p["weight"] <= 200):
        errors.append(f"体重异常: {p['weight']}kg")

    # 选秀校验
    if not (1947 <= p["draft_year"] <= 2026):
        errors.append(f"选秀年份异常: {p['draft_year']}")

    # 生涯时间校验
    if p["career_end"] is not None and p["career_start"] > p["career_end"]:
        errors.append("生涯开始时间晚于结束时间")

    # 荣誉子字段校验
    for hf in HONOR_FIELDS:
        if hf not in p.get("honors", {}):
            errors.append(f"honors 缺少字段: {hf}")

    # 数据统计校验
    for sf in STATS_FIELDS:
        if sf not in p.get("career_stats", {}):
            errors.append(f"career_stats 缺少字段: {sf}")

    # 球队数据校验
    for i, t in enumerate(p.get("teams", [])):
        for tf in TEAM_FIELDS:
            if tf not in t:
                errors.append(f"teams[{i}] 缺少字段: {tf}")

    # 关联关系校验
    for i, r in enumerate(p.get("notable_relations", [])):
        for rf in RELATION_FIELDS:
            if rf not in r:
                errors.append(f"notable_relations[{i}] 缺少字段: {rf}")

    # 难度档位校验
    if p["difficulty_tier"] not in VALID_TIERS:
        errors.append(f"无效难度档位: {p['difficulty_tier']}")

    return errors


def validate_all(players):
    """校验全部球员数据"""
    all_errors = {}
    ids = set()

    for i, p in enumerate(players):
        pid = p.get("id", f"<index {i}>")

        # 检查重复 ID
        if p.get("id") in ids:
            all_errors[pid] = [f"重复的 ID: {p['id']}"]
        ids.add(p.get("id"))

        errs = validate_player(p, i)
        if errs:
            all_errors[pid] = errs

    # 检查 notable_relations 中的 player_id 引用是否有效
    for p in players:
        pid = p.get("id", "")
        for rel in p.get("notable_relations", []):
            if rel["player_id"] not in ids:
                all_errors.setdefault(pid, []).append(
                    f"notable_relations 引用了不存在的球员: {rel['player_id']}"
                )

    # 检查 teammate 关系的双向性（如果是队友，双方都应记录）
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
                            f"队友关系不是双向的: {p['id']} -> {target_id}"
                        )

    return all_errors


def main():
    input_path = Path("miniprogram/data/players.json")

    if not input_path.exists():
        print(f"[ERROR] 输入文件不存在: {input_path}")
        print("请先创建测试数据集（参考实现计划 Task 2）")
        sys.exit(1)

    # 读取数据
    with open(input_path, "r", encoding="utf-8") as f:
        players = json.load(f)

    print(f"读取到 {len(players)} 名球员")

    # 校验
    errors = validate_all(players)

    if errors:
        print(f"\n[ERROR] 发现 {len(errors)} 名球员数据有问题:\n")
        for pid, errs in errors.items():
            print(f"  [{pid}]:")
            for e in errs:
                print(f"    - {e}")
        print(f"\n总计 {len(errors)} 名球员校验失败")
        sys.exit(1)

    # 统计信息
    tiers = {1: 0, 2: 0, 3: 0}
    for p in players:
        tiers[p["difficulty_tier"]] += 1

    print(f"\n[OK] 所有数据校验通过 ✓")
    print(f"  球星 (tier 1): {tiers[1]} 人")
    print(f"  知名 (tier 2): {tiers[2]} 人")
    print(f"  全部 (tier 3): {tiers[3]} 人")
    print(f"\n数据文件已就绪: {input_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行校验**

Run: `python scripts/build_data.py`
Expected: 校验 20 名球员全部通过，显示统计信息

- [ ] **Step 3: 提交**

```bash
git add scripts/build_data.py
git commit -m "feat: add data validation script for players.json"
```

---

### Task 10: README 文档

**Files:**
- Create: `README.md`

- [ ] **Step 1: 编写 README.md**

```markdown
# 🏀 NBA 猜词

基于多维相似度的 NBA 球员猜词微信小程序。

## 玩法

系统随机选一名 NBA 球员，你通过输入球员名来猜测答案。每次猜错都会得到：
- **相似度百分比**：基于 15 个维度（位置、队友、荣誉、选秀…）综合计算
- **关键提示**：告诉你和答案最像的地方

通过不断猜测和对比，逐步缩小范围，最终猜出目标球员。

## 模式

| 模式 | 说明 |
|------|------|
| 📅 每日挑战 | 每天一个球员，所有人猜同一个 |
| ♾️ 无限模式 | 随机球员，无限畅玩 |

## 难度

| 难度 | 范围 |
|------|------|
| ⭐ 球星 | 全明星 / 最佳阵容级别（~200 人） |
| ⭐⭐ 知名 | 首发级别（~500 人） |
| ⭐⭐⭐ 全部 | 所有球员 |

## 开发

```bash
# 运行工具函数测试
node tests/test_similarity.js
node tests/test_autocomplete.js

# 校验球员数据
python scripts/build_data.py
```

## 技术栈

- 微信小程序原生框架
- 纯前端，零服务器成本
- 球员数据打包为本地 JSON

## 项目结构

```
miniprogram/        # 小程序代码
  pages/            # 页面
  utils/            # 工具模块
  data/             # 球员数据
scripts/            # 数据脚本
tests/              # 单元测试
```
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README with game introduction and dev guide"
```

---

### Task 11: 集成验证

- [ ] **Step 1: 运行所有单元测试**

```bash
node tests/test_similarity.js
node tests/test_autocomplete.js
```
Expected: 全部通过

- [ ] **Step 2: 校验球员数据**

```bash
python scripts/build_data.py
```
Expected: 全部 20 名球员数据校验通过

- [ ] **Step 3: 检查文件完整性**

Run: `ls -la miniprogram/pages/*/ miniprogram/utils/ miniprogram/data/`
Expected: 所有文件存在且非空

- [ ] **Step 4: 在微信开发者工具中打开项目**

- 打开微信开发者工具
- 导入项目，选择 `miniprogram/` 目录
- 填写 AppID（测试号即可）
- 验证首页渲染、模式和难度切换
- 验证游戏页的输入、补全、提交、排序功能
- 验证猜中后结果展示

- [ ] **Step 5: 提交（如有修改）**

```bash
git add -A
git commit -m "chore: integration verification and fixes"
```

---

### Task 12: 推送到 GitHub

- [ ] **Step 1: 确保所有修改已提交**

Run: `git status`
Expected: `nothing to commit, working tree clean`

- [ ] **Step 2: 推送到 GitHub**

```bash
git push -u origin master
```

- [ ] **Step 3: 验证推送成功**

打开 `https://github.com/zxc1209/caici` 确认文件已上传

---

## 后续扩展（v2 规划）

- [ ] 数据爬取脚本：从 Basketball-Reference 自动获取全量球员数据
- [ ] 季后赛交手数据：爬取或计算季后赛对阵关系
- [ ] 更多球员：扩展到 500+ 球员
- [ ] 排行榜：本地存储最佳成绩
- [ ] 微信分享：分享每日挑战成绩
- [ ] 音效和动画反馈
