// miniprogram/utils/autocomplete.js

function searchPlayers(query, players, limit = 10) {
  if (!query || query.trim() === '') return []
  const q = query.trim().toLowerCase()
  const scored = players
    .map(p => ({ player: p, score: matchScore(q, p) }))
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score)
  return scored.slice(0, limit).map(r => r.player)
}

function matchScore(query, player) {
  const nameEn = player.name_en.toLowerCase()
  const nameCn = player.name || ''
  if (nameEn === query) return 100
  if (nameEn.startsWith(query)) return 80
  if (nameEn.includes(query)) return 60
  if (nameCn === query) return 90
  if (nameCn.includes(query)) return 70
  const initials = nameEn.split(' ').map(w => w[0]).join('')
  if (initials === query) return 50
  if (initials.startsWith(query)) return 40
  const words = nameEn.split(' ')
  for (const word of words) {
    if (word === query) return 75
    if (word.startsWith(query)) return 55
  }
  return 0
}

function validatePlayer(name, players) {
  if (!name) return null
  const lower = name.trim().toLowerCase()
  // Try exact match against English name, Chinese name, or id
  return players.find(p =>
    p.name_en.toLowerCase() === lower ||
    (p.name && p.name.toLowerCase() === lower) ||
    p.id.toLowerCase() === lower
  ) || null
}

export { searchPlayers, validatePlayer }
