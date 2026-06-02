// miniprogram/utils/similarity.js

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

function positionScore(p1, p2) {
  if (p1 === p2) return 1.0
  const adjacent = POSITION_ADJACENCY[p1] || []
  if (adjacent.includes(p2)) return 0.5
  return 0.0
}

function heightWeightScore(h1, w1, h2, w2) {
  const heightDiff = Math.abs(h1 - h2) / 30.0
  const weightDiff = Math.abs(w1 - w2) / 40.0
  const combined = (heightDiff + weightDiff) / 2
  return Math.exp(-combined * combined * 2)
}

function teammateScore(teams1, teams2) {
  for (const t1 of teams1) {
    for (const t2 of teams2) {
      if (t1.team === t2.team) {
        const start1 = t1.start, end1 = t1.end || 2026
        const start2 = t2.start, end2 = t2.end || 2026
        if (start1 <= end2 && start2 <= end1) {
          return 1.0
        }
      }
    }
  }
  return 0.0
}

function sameTeamScore(teams1, teams2) {
  const teamsSet1 = new Set(teams1.map(t => t.team))
  const teamsSet2 = new Set(teams2.map(t => t.team))
  let count = 0
  for (const team of teamsSet1) {
    if (teamsSet2.has(team)) count++
  }
  if (count === 0) return 0.0
  return Math.min(0.3 + count * 0.2, 1.0)
}

function playoffMatchupScore(p1, p2) {
  return 0.0
}

function honorsScore(h1, h2) {
  let score = 0.0
  let count = 0
  const mvpDiff = Math.abs((h1.mvp || 0) - (h2.mvp || 0))
  score += mvpDiff === 0 ? 1.0 : Math.max(0, 1.0 - mvpDiff * 0.3)
  count++
  const champDiff = Math.abs((h1.championships || 0) - (h2.championships || 0))
  score += champDiff === 0 ? 1.0 : Math.max(0, 1.0 - champDiff * 0.2)
  count++
  return score / count
}

function draftScore(y1, p1, y2, p2) {
  if (y1 !== y2) return 0.0
  if (p1 == null || p2 == null) return 0.3
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
  return Math.min(1.0, overlap / totalSpan * 2)
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

function allStarLevel(count) {
  const safe = count ?? 0
  if (safe === 0) return 0
  if (safe <= 3) return 1
  if (safe <= 7) return 2
  return 3
}

function allStarLevelScore(as1, as2) {
  const level1 = allStarLevel(as1)
  const level2 = allStarLevel(as2)
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
      if (rel.relation === '队友') return 1.0
      if (rel.relation === '宿敌') return 0.8
      return 0.6
    }
  }
  return 0.0
}

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
  { dim: 'allStarLevel', gen: () => '全明星次数相近' },
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

function calculateSimilarity(guess, answer) {
  if (!guess || !answer) {
    return { score: 0, hint: '数据错误', details: {} }
  }

  if (guess.id === answer.id) {
    return { score: 100.0, hint: '这就是正确答案！', details: {} }
  }

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

  let total = 0.0
  for (const [dim, score] of Object.entries(scores)) {
    total += score * (WEIGHTS[dim] || 0)
  }

  const percentage = Math.round(total * 1000) / 10

  // Guard against NaN from bad data
  if (isNaN(percentage)) {
    return { score: 0, hint: '数据异常', details: scores }
  }

  const hint = generateHint(guess, answer, scores)

  return { score: percentage, hint, details: scores }
}

export { calculateSimilarity }
