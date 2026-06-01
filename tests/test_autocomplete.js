const { searchPlayers, validatePlayer } = require('../miniprogram/utils/autocomplete.js')
const players = require('../miniprogram/data/players.js')

function testChineseSearch() {
  const results = searchPlayers('詹', players)
  console.assert(results.length > 0, 'Should find results for "詹"')
  console.assert(results.some(r => r.name_en === 'LeBron James'), 'Should find LeBron James when searching "詹"')
  console.log(`✓ testChineseSearch: found ${results.length} results for "詹"`)
}

function testEnglishSearch() {
  const results = searchPlayers('james', players)
  console.assert(results.some(r => r.name_en === 'LeBron James'), 'Should find LeBron James')
  console.assert(results.some(r => r.name_en === 'James Harden'), 'Should find James Harden')
  console.log(`✓ testEnglishSearch: found ${results.length} results for "james"`)
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

testChineseSearch()
testEnglishSearch()
testExactValidation()
testInvalidPlayer()
testResultLimit()
console.log('\nAll autocomplete tests passed!')
