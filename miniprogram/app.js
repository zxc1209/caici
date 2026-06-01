App({
  globalData: {
    players: [],
    playersMap: {}
  },

  onLaunch() {
    const players = require('./data/players.json')
    this.globalData.players = players
    players.forEach(p => {
      this.globalData.playersMap[p.name_en] = p
    })
  }
})
