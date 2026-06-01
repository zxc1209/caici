App({
  globalData: {
    players: [],
    playersMap: {}
  },

  onLaunch() {
    try {
      const players = require('./data/players.json')
      this.globalData.players = players
      players.forEach(p => {
        if (p.name_en) {
          this.globalData.playersMap[p.name_en] = p
        }
      })
    } catch (err) {
      console.error('Failed to load players data:', err)
    }
  }
})
