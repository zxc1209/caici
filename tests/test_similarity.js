// tests/test_similarity.js
// Run with: node tests/test_similarity.js

const { calculateSimilarity } = require('../miniprogram/utils/similarity.js')
const players = require('../miniprogram/data/players.json')
const byName = {}
players.forEach(p => { byName[p.name_en] = p })

function testSamePlayer() {
  const lebron = byName['LeBron James']
  const result = calculateSimilarity(lebron, lebron)
  console.assert(result.score === 100.0,
    `Same player should be 100%, got ${result.score}%`)
  console.log('✓ testSamePlayer passed')
}

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

function testSamePositionHigherThanDifferent() {
  const lebron = byName['LeBron James']
  const durant = byName['Kevin Durant']
  const curry = byName['Stephen Curry']
  const lebronDurant = calculateSimilarity(lebron, durant)
  const lebronCurry = calculateSimilarity(lebron, curry)
  console.log(`✓ LeBron-Durant position: ${lebronDurant.details.position}`)
  console.log(`✓ LeBron-Curry position: ${lebronCurry.details.position}`)
  console.assert(lebronDurant.details.position > lebronCurry.details.position,
    'Same position should score higher on position dimension')
  console.log('✓ testSamePositionHigherThanDifferent passed')
}

function testHintGeneration() {
  const lebron = byName['LeBron James']
  const wade = byName['Dwyane Wade']
  const result = calculateSimilarity(lebron, wade)
  console.assert(typeof result.hint === 'string' && result.hint.length > 0,
    `Hint should be a non-empty string, got: "${result.hint}"`)
  console.log(`✓ Hint: "${result.hint}"`)
  console.log('✓ testHintGeneration passed')
}

function testNotableRelations() {
  const lebron = byName['LeBron James']
  const curry = byName['Stephen Curry']
  const result = calculateSimilarity(lebron, curry)
  console.log(`✓ LeBron-Curry similarity: ${result.score}%`)
  console.log(`✓ LeBron-Curry hint: "${result.hint}"`)
  console.assert(result.details.notableRelations > 0,
    'LeBron and Curry should have notable relation score')
  console.log('✓ testNotableRelations passed')
}

testSamePlayer()
testTeammatesHigherThanNonTeammates()
testSamePositionHigherThanDifferent()
testHintGeneration()
testNotableRelations()
console.log('\nAll tests passed!')
