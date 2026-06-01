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
