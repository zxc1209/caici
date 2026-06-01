// miniprogram/utils/daily.js

function getTodayKey() {
  const now = new Date()
  const offset = 8 * 60 * 60 * 1000  // UTC+8
  const local = new Date(now.getTime() + offset)
  const year = local.getUTCFullYear()
  const month = String(local.getUTCMonth() + 1).padStart(2, '0')
  const day = String(local.getUTCDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function hashString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash)
}

function getDailyIndex(playerCount, dateKey) {
  const key = dateKey || getTodayKey()
  const seed = hashString(key)
  return seed % playerCount
}

function getDailyPlayer(allPlayers, difficulty = 1) {
  const pool = allPlayers.filter(p => p.difficulty_tier <= difficulty)
  const index = getDailyIndex(pool.length)
  return pool[index]
}

module.exports = { getTodayKey, hashString, getDailyIndex, getDailyPlayer }
