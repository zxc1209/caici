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

    const app = getApp()
    const allPlayers = app.globalData.players

    let answer
    if (mode === 'daily') {
      answer = getDailyPlayer(allPlayers, difficulty)
    } else {
      const pool = allPlayers.filter(p => p.difficulty_tier <= difficulty)
      answer = pool[Math.floor(Math.random() * pool.length)]
    }

    this.setData({
      mode,
      difficulty,
      difficultyStars: stars[difficulty],
      allPlayers,
      answer
    })
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

    const alreadyGuessed = this.data.guesses.some(
      g => g.player.id === player.id
    )
    if (alreadyGuessed) {
      wx.showToast({ title: '已经猜过这个球员了', icon: 'none' })
      return
    }

    const result = calculateSimilarity(player, this.data.answer)
    const isCorrect = player.id === this.data.answer.id

    const newGuess = {
      id: player.id,
      player,
      score: isCorrect ? 100.0 : result.score,
      hint: isCorrect ? '🎉 恭喜猜中！' : result.hint
    }

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
