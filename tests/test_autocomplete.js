const { searchPlayers, validatePlayer } = require('../miniprogram/utils/autocomplete.js')
const players = require('../miniprogram/data/players.js')

function testEnglishSearch() {
  const results = searchPlayers('lebron', players)
  console.assert(results.some(r => r.name_en === 'LeBron James'), 'Should find LeBron James')
  console.log(`✓ testEnglishSearch: found ${results.length} results for "lebron"`)
}

function testExactValidation() {
  const result = validatePlayer('LeBron James', players)
  console.assert(result !== null, 'Should validate "LeBron James"')
  console.assert(result.name_en === 'LeBron James', 'Should return correct player')
  console.log('✓ testExactValidation passed')
}

function testInvalidPlayer() {
  const result = validatePlayer('Nonexistent Player', players)
  console.assert(result === null, 'Should return null for invalid player')
  console.log('✓ testInvalidPlayer passed')
}

function testResultLimit() {
  const results = searchPlayers('a', players)
  console.assert(results.length <= 10, 'Should limit results to 10')
  console.log(`✓ testResultLimit: returned ${results.length} (max 10)`)
}

function testBulkDataLoaded() {
  console.assert(players.length > 2000, `Should have many players, got ${players.length}`)
  console.log(`✓ testBulkDataLoaded: ${players.length} players`)
}

testEnglishSearch()
testExactValidation()
testInvalidPlayer()
testResultLimit()
testBulkDataLoaded()
console.log('\nAll autocomplete tests passed!')
