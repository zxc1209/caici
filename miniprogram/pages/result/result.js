Page({
  data: {
    player: {},
    guessCount: 0
  },

  onLoad(options) {
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
