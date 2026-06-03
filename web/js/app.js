import players from './players.js';
import { calculateSimilarity } from './similarity.js';
import { searchPlayers, validatePlayer } from './autocomplete.js';
import { getTodayKey, getDailyPlayer } from './daily.js';

// ============================================================
// State
// ============================================================
const state = {
  mode: 'daily',
  difficulty: 1,
  answer: null,
  guesses: [],
  gameOver: false,
  suggestionsVisible: false,
};

// ============================================================
// DOM References
// ============================================================
const screens = {
  home: document.getElementById('home-screen'),
  game: document.getElementById('game-screen'),
  result: document.getElementById('result-screen'),
};

// Home screen elements
const modeSelector = document.getElementById('mode-selector');
const difficultySelector = document.getElementById('difficulty-selector');
const startBtn = document.getElementById('start-btn');

// Game screen elements
const backHomeBtn = document.getElementById('back-home-btn');
const newGameBtn = document.getElementById('new-game-btn');
const giveUpBtn = document.getElementById('give-up-btn');
const modeLabel = document.getElementById('mode-label');
const playerInput = document.getElementById('player-input');
const submitBtn = document.getElementById('submit-btn');
const autocompleteDropdown = document.getElementById('autocomplete-dropdown');
const historySection = document.getElementById('history-section');
const historyList = document.getElementById('history-list');
const successBanner = document.getElementById('success-banner');
const successPlayerName = document.getElementById('success-player-name');
const successGuessCount = document.getElementById('success-guess-count');
const viewResultBtn = document.getElementById('view-result-btn');
const playAgainBtn = document.getElementById('play-again-btn');
const backHome2Btn = document.getElementById('back-home-2-btn');

// Result screen elements
const playerDetailCard = document.getElementById('player-detail-card');
const guessCountInfo = document.getElementById('guess-count-info');
const resultPlayAgain = document.getElementById('result-play-again');
const resultBackHome = document.getElementById('result-back-home');

// ============================================================
// Screen Management
// ============================================================
function showScreen(id) {
  Object.values(screens).forEach(function (el) {
    el.classList.remove('active');
  });
  var target = document.getElementById(id);
  if (target) {
    target.classList.add('active');
  }
  window.scrollTo(0, 0);
}

// ============================================================
// Toast
// ============================================================
function showToast(msg) {
  var toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  document.body.appendChild(toast);

  // Trigger reflow for transition
  void toast.offsetWidth;
  toast.classList.add('show');

  setTimeout(function () {
    toast.classList.remove('show');
    setTimeout(function () {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }, 1500);
}

// ============================================================
// Home Screen Logic
// ============================================================
function setupHome() {
  // Mode selection
  modeSelector.querySelectorAll('.mode-card').forEach(function (card) {
    card.addEventListener('click', function () {
      modeSelector.querySelectorAll('.mode-card').forEach(function (c) {
        c.classList.remove('selected');
      });
      card.classList.add('selected');
      state.mode = card.dataset.mode;
    });
  });

  // Difficulty selection
  difficultySelector.querySelectorAll('.diff-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      difficultySelector.querySelectorAll('.diff-btn').forEach(function (b) {
        b.classList.remove('selected');
      });
      btn.classList.add('selected');
      state.difficulty = parseInt(btn.dataset.diff, 10);
    });
  });

  // Start button
  startBtn.addEventListener('click', startGame);
}

// ============================================================
// Game Logic
// ============================================================
function getRandomPlayer(difficulty) {
  var pool = players.filter(function (p) {
    return p.difficulty_tier <= difficulty;
  });
  if (pool.length === 0) {
    pool = players;
  }
  var idx = Math.floor(Math.random() * pool.length);
  return pool[idx];
}

function startGame() {
  // Reset game state
  state.guesses = [];
  state.gameOver = false;
  state.suggestionsVisible = false;

  // Pick answer
  if (state.mode === 'daily') {
    state.answer = getDailyPlayer(players, state.difficulty);
  } else {
    state.answer = getRandomPlayer(state.difficulty);
  }

  // Update mode label
  var modeText = state.mode === 'daily'
    ? '每日挑战（' + getTodayKey() + '）'
    : '无限模式';
  var diffText = ['', '简单', '中等', '困难'][state.difficulty];
  modeLabel.textContent = modeText + ' · ' + diffText;

  // Clear UI
  playerInput.value = '';
  playerInput.disabled = false;
  autocompleteDropdown.classList.add('hidden');
  autocompleteDropdown.textContent = '';
  historySection.classList.add('hidden');
  historyList.textContent = '';
  successBanner.classList.add('hidden');
  successPlayerName.textContent = '';
  successGuessCount.textContent = '';

  // Focus input
  showScreen('game-screen');
  setTimeout(function () {
    playerInput.focus();
  }, 100);
}

function processGuess(player) {
  // Duplicate check
  var isDuplicate = state.guesses.some(function (g) {
    return g.player.id === player.id;
  });
  if (isDuplicate) {
    showToast('已经猜过这个球员了');
    return;
  }

  // Calculate similarity
  var result = calculateSimilarity(player, state.answer);

  // Check if correct
  if (player.id === state.answer.id) {
    // Add to guesses first
    state.guesses.push({
      player: player,
      similarity: result.score,
      hint: '这就是正确答案！',
      hints: ['这就是正确答案！'],
    });
    state.gameOver = true;
    renderHistory();
    disableInput();
    showSuccessBanner();
  } else {
    // Add wrong guess
    state.guesses.push({
      player: player,
      similarity: result.score,
      hint: result.hint,
      hints: result.hints || [result.hint],
    });
    renderHistory();
    var hintMsg = result.hints ? result.hints.join(' | ') : result.hint;
    showToast('相似度：' + result.score + '% — ' + hintMsg);
  }

  // Clear input and suggestions
  playerInput.value = '';
  autocompleteDropdown.classList.add('hidden');
  autocompleteDropdown.textContent = '';
  state.suggestionsVisible = false;
}

function disableInput() {
  playerInput.disabled = true;
  submitBtn.disabled = true;
}

function enableInput() {
  playerInput.disabled = false;
  submitBtn.disabled = false;
}

// ============================================================
// Autocomplete
// ============================================================
function handleInput(e) {
  var query = playerInput.value.trim();

  if (query.length === 0) {
    autocompleteDropdown.classList.add('hidden');
    autocompleteDropdown.textContent = '';
    state.suggestionsVisible = false;
    return;
  }

  var results = searchPlayers(query, players, 8);

  if (results.length === 0) {
    autocompleteDropdown.classList.add('hidden');
    autocompleteDropdown.textContent = '';
    state.suggestionsVisible = false;
    return;
  }

  renderSuggestions(results);
}

function renderSuggestions(results) {
  autocompleteDropdown.textContent = '';

  results.forEach(function (player) {
    var item = document.createElement('div');
    item.className = 'autocomplete-item';

    var cnSpan = document.createElement('span');
    cnSpan.className = 'cn-name';
    cnSpan.textContent = player.name;

    var enSpan = document.createElement('span');
    enSpan.className = 'en-name';
    enSpan.textContent = player.name_en;

    item.appendChild(cnSpan);
    item.appendChild(enSpan);

    item.addEventListener('click', function () {
      selectSuggestion(player);
    });

    autocompleteDropdown.appendChild(item);
  });

  autocompleteDropdown.classList.remove('hidden');
  state.suggestionsVisible = true;
}

function selectSuggestion(player) {
  playerInput.value = player.name_en;
  autocompleteDropdown.classList.add('hidden');
  autocompleteDropdown.textContent = '';
  state.suggestionsVisible = false;
  // Auto-submit for better mobile UX
  submitGuess();
}

function closeSuggestions() {
  autocompleteDropdown.classList.add('hidden');
  autocompleteDropdown.textContent = '';
  state.suggestionsVisible = false;
}

// ============================================================
// Submit Guess
// ============================================================
function submitGuess() {
  if (state.gameOver) return;

  var inputValue = playerInput.value.trim();

  if (inputValue === '') {
    showToast('请输入球员名称');
    return;
  }

  // Try exact match
  var player = validatePlayer(inputValue, players);

  // Fallback: if no exact match but suggestions exist, use first suggestion
  if (!player && state.suggestionsVisible) {
    var suggestions = searchPlayers(inputValue, players, 1);
    if (suggestions.length > 0) {
      player = suggestions[0];
    }
  }

  if (!player) {
    showToast('未找到该球员，请从列表中选择');
    return;
  }

  processGuess(player);
}

// ============================================================
// History Rendering
// ============================================================
function renderHistory() {
  historyList.textContent = '';

  if (state.guesses.length === 0) {
    historySection.classList.add('hidden');
    return;
  }

  historySection.classList.remove('hidden');

  // Sort by similarity DESC
  var sorted = state.guesses.slice().sort(function (a, b) {
    return b.similarity - a.similarity;
  });

  sorted.forEach(function (entry, index) {
    var item = document.createElement('div');
    item.className = 'history-item';

    // Rank
    var rank = document.createElement('span');
    rank.className = 'history-rank';
    rank.textContent = '#' + (index + 1);

    // Info
    var info = document.createElement('div');
    info.className = 'history-info';

    var nameEl = document.createElement('div');
    nameEl.className = 'history-name';
    nameEl.textContent = entry.player.name;

    var hintEl = document.createElement('div');
    hintEl.className = 'history-hint';
    var hintText = entry.hints ? entry.hints.join(' · ') : entry.hint;
    hintEl.textContent = '💡 ' + hintText;

    info.appendChild(nameEl);
    info.appendChild(hintEl);

    // Score
    var score = document.createElement('span');
    score.className = 'history-score';
    score.textContent = entry.similarity + '%';

    if (entry.similarity > 70) {
      score.classList.add('hot');
    } else if (entry.similarity >= 40) {
      score.classList.add('warm');
    } else {
      score.classList.add('cool');
    }

    item.appendChild(rank);
    item.appendChild(info);
    item.appendChild(score);

    historyList.appendChild(item);
  });

  historySection.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================
// Success Banner
// ============================================================
function showSuccessBanner() {
  successPlayerName.textContent = state.answer.name + '（' + state.answer.name_en + '）';
  var count = state.guesses.length;
  successGuessCount.textContent = '你用了 ' + count + ' 次猜测找到了答案';
  successBanner.classList.remove('hidden');
  successBanner.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================
// Give Up
// ============================================================
function giveUp() {
  if (state.gameOver) return
  state.gameOver = true
  state.guesses.push({
    player: state.answer,
    similarity: 100.0,
    hint: '🏳️ 放弃'
  })
  renderHistory()
  disableInput()
  successPlayerName.textContent = state.answer.name + '（' + state.answer.name_en + '）'
  var count = state.guesses.length
  successGuessCount.textContent = '答案是 ' + state.answer.name + '，共猜测 ' + count + ' 次'
  successBanner.classList.remove('hidden')
  successBanner.scrollIntoView({ behavior: 'smooth' })
}

// New Game / Navigation
// ============================================================
function newGame() {
  enableInput();
  if (state.mode === 'daily') {
    // Daily mode: same answer, reset guesses
    state.guesses = [];
    state.gameOver = false;
    state.suggestionsVisible = false;
    playerInput.value = '';
    playerInput.disabled = false;
    submitBtn.disabled = false;
    autocompleteDropdown.classList.add('hidden');
    autocompleteDropdown.textContent = '';
    historySection.classList.add('hidden');
    historyList.textContent = '';
    successBanner.classList.add('hidden');
    successPlayerName.textContent = '';
    successGuessCount.textContent = '';
    setTimeout(function () {
      playerInput.focus();
    }, 100);
  } else {
    // Unlimited mode: pick new random answer
    startGame();
  }
}

function goHome() {
  enableInput();
  state.guesses = [];
  state.gameOver = false;
  state.answer = null;
  state.suggestionsVisible = false;
  playerInput.value = '';
  autocompleteDropdown.classList.add('hidden');
  autocompleteDropdown.textContent = '';
  historySection.classList.add('hidden');
  historyList.textContent = '';
  successBanner.classList.add('hidden');
  showScreen('home-screen');
}

// ============================================================
// Result Screen
// ============================================================
function showResult() {
  if (!state.answer) return;

  playerDetailCard.textContent = '';

  // Player name
  var nameEl = document.createElement('div');
  nameEl.className = 'detail-name';
  nameEl.textContent = state.answer.name;

  var nameEnEl = document.createElement('div');
  nameEnEl.className = 'detail-name-en';
  nameEnEl.textContent = state.answer.name_en;

  playerDetailCard.appendChild(nameEl);
  playerDetailCard.appendChild(nameEnEl);

  // Detail grid
  var grid = document.createElement('div');
  grid.className = 'detail-grid';

  // Position + Play Style
  var posItem = createDetailItem('位置', state.answer.position + ' - ' + (state.answer.play_style || ''));
  grid.appendChild(posItem);

  // Height / Weight
  var hwItem = createDetailItem('身高 / 体重', state.answer.height + 'cm / ' + state.answer.weight + 'kg');
  grid.appendChild(hwItem);

  // Nationality
  var natItem = createDetailItem('国籍', state.answer.nationality || '未知');
  grid.appendChild(natItem);

  // College
  var colItem = createDetailItem('大学', state.answer.college || '无');
  grid.appendChild(colItem);

  // Draft
  var draftText = state.answer.draft_year + ' 年';
  if (state.answer.draft_pick != null) {
    draftText += ' · 第 ' + state.answer.draft_pick + ' 顺位';
  } else {
    draftText += ' · 落选秀';
  }
  var draftItem = createDetailItem('选秀', draftText);
  grid.appendChild(draftItem);

  // Career span
  var careerText = state.answer.career_start + ' - ' + (state.answer.career_end || '至今');
  var careerItem = createDetailItem('职业生涯', careerText);
  grid.appendChild(careerItem);

  // Jersey numbers
  var jerseys = (state.answer.jersey_numbers || []).map(function (n) { return '#' + n; }).join(' / ');
  var jerseyItem = createDetailItem('球衣号码', jerseys || '无');
  grid.appendChild(jerseyItem);

  // Teams
  var teamNames = (state.answer.teams || []).map(function (t) { return t.team; });
  var teamsItem = createDetailItemFull('效力球队', teamNames.join('、'));
  grid.appendChild(teamsItem);

  playerDetailCard.appendChild(grid);

  // Honors
  if (state.answer.honors) {
    var honorsDiv = document.createElement('div');
    honorsDiv.className = 'detail-honors';

    var h = state.answer.honors;
    if (h.mvp > 0) {
      addHonorTag(honorsDiv, 'MVP × ' + h.mvp);
    }
    if (h.championships > 0) {
      addHonorTag(honorsDiv, '总冠军 × ' + h.championships);
    }
    if (h.all_star > 0) {
      addHonorTag(honorsDiv, '全明星 × ' + h.all_star);
    }
    if (h.all_nba_first > 0) {
      addHonorTag(honorsDiv, '一阵 × ' + h.all_nba_first);
    }
    if (h.hall_of_fame) {
      var hofTag = document.createElement('span');
      hofTag.className = 'honor-tag hof';
      hofTag.textContent = '名人堂';
      honorsDiv.appendChild(hofTag);
    }

    playerDetailCard.appendChild(honorsDiv);
  }

  // Career stats
  if (state.answer.career_stats) {
    var statsDiv = document.createElement('div');
    statsDiv.className = 'detail-stats';

    var s = state.answer.career_stats;
    statsDiv.appendChild(createStatItem(s.ppg, '分'));
    statsDiv.appendChild(createStatItem(s.rpg, '板'));
    statsDiv.appendChild(createStatItem(s.apg, '助'));

    playerDetailCard.appendChild(statsDiv);
  }

  // Guess count
  guessCountInfo.textContent = '';
  var countSpan = document.createElement('span');
  countSpan.textContent = state.guesses.length;
  guessCountInfo.appendChild(document.createTextNode('猜测次数：'));
  guessCountInfo.appendChild(countSpan);
  guessCountInfo.appendChild(document.createTextNode(' 次'));

  // Difficulty tier
  var tierEl = document.createElement('div');
  tierEl.style.cssText = 'text-align:center;font-size:0.8rem;color:#8888aa;margin-top:0.5rem;';
  var tierNames = ['', '简单', '中等', '困难'];
  tierEl.textContent = '难度等级：' + (tierNames[state.answer.difficulty_tier] || state.answer.difficulty_tier);
  playerDetailCard.appendChild(tierEl);

  showScreen('result-screen');
}

function createDetailItem(label, value) {
  var div = document.createElement('div');
  div.className = 'detail-item';

  var labelEl = document.createElement('div');
  labelEl.className = 'detail-label';
  labelEl.textContent = label;

  var valueEl = document.createElement('div');
  valueEl.className = 'detail-value';
  valueEl.textContent = value;

  div.appendChild(labelEl);
  div.appendChild(valueEl);
  return div;
}

function createDetailItemFull(label, value) {
  var div = document.createElement('div');
  div.className = 'detail-item full-width';

  var labelEl = document.createElement('div');
  labelEl.className = 'detail-label';
  labelEl.textContent = label;

  var valueEl = document.createElement('div');
  valueEl.className = 'detail-value';
  valueEl.textContent = value;

  div.appendChild(labelEl);
  div.appendChild(valueEl);
  return div;
}

function addHonorTag(container, text) {
  var tag = document.createElement('span');
  tag.className = 'honor-tag';
  tag.textContent = text;
  container.appendChild(tag);
}

function createStatItem(value, label) {
  var div = document.createElement('div');
  div.className = 'stat-item';

  var valEl = document.createElement('div');
  valEl.className = 'stat-value';
  valEl.textContent = typeof value === 'number' ? value.toFixed(1) : (value || '0');

  var labelEl = document.createElement('div');
  labelEl.className = 'stat-label';
  labelEl.textContent = label;

  div.appendChild(valEl);
  div.appendChild(labelEl);
  return div;
}

// ============================================================
// Event Bindings
// ============================================================
function bindEvents() {
  // Input events
  playerInput.addEventListener('input', handleInput);
  playerInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      submitGuess();
    } else if (e.key === 'Escape') {
      closeSuggestions();
    }
  });

  // Submit button
  submitBtn.addEventListener('click', submitGuess);

  // Click outside closes autocomplete
  document.addEventListener('click', function (e) {
    if (!playerInput.contains(e.target) &&
        !autocompleteDropdown.contains(e.target) &&
        e.target !== submitBtn) {
      closeSuggestions();
    }
  });

  // Game navigation buttons
  backHomeBtn.addEventListener('click', goHome);
  newGameBtn.addEventListener('click', newGame);
  giveUpBtn.addEventListener('click', giveUp);

  // Success banner buttons
  viewResultBtn.addEventListener('click', showResult);
  playAgainBtn.addEventListener('click', newGame);
  backHome2Btn.addEventListener('click', goHome);

  // Result screen buttons
  resultPlayAgain.addEventListener('click', newGame);
  resultBackHome.addEventListener('click', goHome);
}

// ============================================================
// Initialize
// ============================================================
function init() {
  setupHome();
  bindEvents();
  showScreen('home-screen');
}

init();
