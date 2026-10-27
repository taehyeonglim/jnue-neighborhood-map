(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const appMessage = $('#app-message');
  const announce = (message) => { appMessage.textContent = message; };

  const lesson = $('#lesson');
  const home = $('#home');
  const slides = $$('.slide[data-slide]');
  const stepButtons = $$('.stepper [data-step]');
  const lessonCounter = $('#lesson-counter');
  const previousButton = $('[data-prev]');
  const nextButton = $('[data-next]');
  const stageData = [
    { name: '탐험 시작', minutes: 5, tip: '주변 장소를 자유롭게 이야기하며 탐험에 대한 기대를 열어 주세요.' },
    { name: '방위 익히기', minutes: 8, tip: '북쪽을 먼저 찾고 반대편과 양옆의 방향을 함께 말해 보세요.' },
    { name: '기호와 범례', minutes: 7, tip: '기호는 지도의 약속이며, 범례에서 뜻을 확인한다는 점을 짚어 주세요.' },
    { name: '지도 미션', minutes: 15, tip: '먼저 학생 스스로 답과 근거를 찾게 한 뒤 정답을 공개해 주세요.' },
    { name: '탐험 마무리', minutes: 5, tip: '자기 점검 뒤 방위표와 범례 중 하나의 쓰임을 말하게 해 주세요.' }
  ];
  let currentStep = 0;
  let lessonActive = false;

  const timerDisplay = $('#timer-display');
  const timerMessage = $('#timer-message');
  const timerStage = $('#timer-stage');
  const timerStartButton = $('[data-timer-start]');
  let remaining = stageData[0].minutes * 60;
  let deadline = 0;
  let timerInterval = null;

  function renderTime() {
    const safe = Math.max(0, Math.ceil(remaining));
    timerDisplay.textContent = `${String(Math.floor(safe / 60)).padStart(2, '0')}:${String(safe % 60).padStart(2, '0')}`;
  }

  function stopInterval() {
    if (timerInterval !== null) window.clearInterval(timerInterval);
    timerInterval = null;
  }

  function resetTimer() {
    stopInterval();
    remaining = stageData[currentStep].minutes * 60;
    timerStartButton.textContent = '시작';
    timerMessage.textContent = '준비되면 시작을 눌러 주세요.';
    timerStage.textContent = `${stageData[currentStep].name} · ${stageData[currentStep].minutes}분`;
    renderTime();
  }

  function timerTick() {
    remaining = Math.max(0, (deadline - Date.now()) / 1000);
    renderTime();
    if (remaining <= 0) {
      stopInterval();
      timerStartButton.textContent = '다시 시작';
      timerMessage.textContent = '시간이 끝났어요! 다음 활동으로 넘어가 보세요.';
      announce(`${stageData[currentStep].name} 시간이 끝났어요.`);
    }
  }

  timerStartButton.addEventListener('click', () => {
    if (timerInterval !== null) {
      remaining = Math.max(0, (deadline - Date.now()) / 1000);
      stopInterval();
      renderTime();
      timerStartButton.textContent = '계속';
      timerMessage.textContent = '잠시 쉬는 중이에요.';
      return;
    }
    if (remaining <= 0) remaining = stageData[currentStep].minutes * 60;
    deadline = Date.now() + remaining * 1000;
    timerStartButton.textContent = '일시정지';
    timerMessage.textContent = '탐험을 진행하고 있어요.';
    timerInterval = window.setInterval(timerTick, 250);
    timerTick();
  });
  $('[data-timer-reset]').addEventListener('click', resetTimer);

  function showStep(index, options = {}) {
    currentStep = Math.max(0, Math.min(stageData.length - 1, index));
    slides.forEach((slide, position) => { slide.hidden = position !== currentStep; });
    stepButtons.forEach((button, position) => {
      if (position === currentStep) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
    });
    previousButton.disabled = currentStep === 0;
    nextButton.textContent = currentStep === stageData.length - 1 ? '처음 화면으로 ↗' : '다음 단계 →';
    lessonCounter.textContent = `${String(currentStep + 1).padStart(2, '0')} / ${String(stageData.length).padStart(2, '0')}`;
    $('#teacher-tip').textContent = stageData[currentStep].tip;
    resetTimer();
    if (!options.keepPosition) {
      window.requestAnimationFrame(() => {
        const heading = $('h2', slides[currentStep]);
        if (heading) heading.focus({ preventScroll: true });
        lesson.scrollIntoView({ block: 'start', behavior: 'auto' });
      });
    }
  }

  function startLesson() {
    home.hidden = true;
    lesson.hidden = false;
    lessonActive = true;
    showStep(0);
    announce('수업을 시작합니다. 첫 번째 단계는 탐험 시작입니다.');
  }

  function returnHome(event) {
    if (event) event.preventDefault();
    lessonActive = false;
    lesson.hidden = true;
    home.hidden = false;
    stopInterval();
    window.scrollTo({ top: 0, behavior: 'auto' });
    $('[data-start]').focus({ preventScroll: true });
  }

  $('[data-start]').addEventListener('click', startLesson);
  $$('[data-home]').forEach((button) => button.addEventListener('click', returnHome));
  previousButton.addEventListener('click', () => showStep(currentStep - 1));
  nextButton.addEventListener('click', () => {
    if (currentStep === stageData.length - 1) returnHome();
    else showStep(currentStep + 1);
  });
  stepButtons.forEach((button) => button.addEventListener('click', () => showStep(Number(button.dataset.step))));
  document.addEventListener('keydown', (event) => {
    if (!lessonActive || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const target = event.target;
    if (target instanceof Element && (target.closest('input, textarea, select, [contenteditable="true"], .map-frame') || target.tagName === 'SUMMARY')) return;
    if (event.key === 'ArrowRight' && currentStep < stageData.length - 1) { event.preventDefault(); showStep(currentStep + 1); }
    if (event.key === 'ArrowLeft' && currentStep > 0) { event.preventDefault(); showStep(currentStep - 1); }
  });

  const fullscreenButton = $('[data-fullscreen]');
  const fullscreenLabel = $('[data-fullscreen-label]');
  if (!document.fullscreenEnabled || !document.documentElement.requestFullscreen) {
    fullscreenButton.disabled = true;
    fullscreenButton.title = '이 브라우저는 전체 화면을 지원하지 않아요.';
  } else {
    fullscreenButton.addEventListener('click', async () => {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await document.documentElement.requestFullscreen();
      } catch (_) {
        announce('전체 화면을 열 수 없어요. 브라우저의 전체 화면 기능을 이용해 주세요.');
      }
    });
    document.addEventListener('fullscreenchange', () => {
      fullscreenLabel.textContent = document.fullscreenElement ? '전체 화면 종료' : '전체 화면';
    });
  }
  $('[data-print]').addEventListener('click', () => window.print());

  const mapObject = $('#neighborhood-map');
  const mapFrame = $('.map-frame');
  const labelsButton = $('[data-labels]');
  const legendButton = $('[data-legend]');
  const zoomOut = $('[data-zoom-out]');
  const zoomIn = $('[data-zoom-in]');
  const zoomValue = $('.zoom-value');
  const placeButtons = $('#place-buttons');
  const placeInfo = $('#place-info');
  let zoom = 1;
  let showLabels = true;
  let showLegend = true;
  let places = [];
  let attachedSvgDocument = null;

  function renderZoom() {
    mapFrame.style.setProperty('--map-zoom', `${zoom * 100}%`);
    zoomValue.textContent = `${Math.round(zoom * 100)}%`;
    zoomOut.disabled = zoom <= 1;
    zoomIn.disabled = zoom >= 2;
  }

  function currentSvg() {
    try { return mapObject.contentDocument; } catch (_) { return null; }
  }

  function syncMapOptions() {
    labelsButton.setAttribute('aria-pressed', String(showLabels));
    labelsButton.textContent = `장소 이름 ${showLabels ? '켜짐' : '꺼짐'}`;
    legendButton.setAttribute('aria-pressed', String(showLegend));
    legendButton.textContent = `범례 ${showLegend ? '켜짐' : '꺼짐'}`;
    const mapDocument = currentSvg();
    if (!mapDocument || !mapDocument.documentElement) return;
    mapDocument.documentElement.classList.toggle('labels-hidden', !showLabels);
    mapDocument.documentElement.classList.toggle('legend-hidden', !showLegend);
    // Inline display also works in SVG viewers that do not apply root selector styles.
    mapDocument.querySelectorAll('[id^="label-"]').forEach((item) => { item.style.display = showLabels ? '' : 'none'; });
    const legend = mapDocument.getElementById('map-legend');
    if (legend) legend.style.display = showLegend ? '' : 'none';
  }

  function selectPlace(placeId) {
    const place = places.find((item) => item.id === placeId);
    if (!place) return;
    $$('#place-buttons button').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.place === placeId)));
    placeInfo.textContent = `${place.name} · ${place.category} — ${place.description || '지도에서 기호와 범례를 살펴보세요.'}`;
  }

  function attachMapEvents() {
    const svgDocument = currentSvg();
    if (!svgDocument || !svgDocument.documentElement) return;
    syncMapOptions();
    if (attachedSvgDocument === svgDocument) return;
    attachedSvgDocument = svgDocument;
    svgDocument.addEventListener('click', (event) => {
      const target = event.target;
      if (!target || typeof target.closest !== 'function') return;
      const marker = target.closest('[id^="place-"], [id^="label-"]');
      if (!marker) return;
      const id = marker.id.replace(/^(place|label)-/, '');
      selectPlace(id);
    });
    svgDocument.querySelectorAll('[id^="place-"]').forEach((element) => { element.style.cursor = 'pointer'; });
  }

  mapObject.addEventListener('load', attachMapEvents);
  zoomIn.addEventListener('click', () => { zoom = Math.min(2, zoom + 0.25); renderZoom(); });
  zoomOut.addEventListener('click', () => { zoom = Math.max(1, zoom - 0.25); renderZoom(); });
  labelsButton.addEventListener('click', () => { showLabels = !showLabels; syncMapOptions(); });
  legendButton.addEventListener('click', () => { showLegend = !showLegend; syncMapOptions(); });
  renderZoom();
  syncMapOptions();
  attachMapEvents();

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function appendAnswer(container, answer, explanation) {
    const details = node('details', 'answer-block');
    details.append(node('summary', '', '정답과 설명 보기'));
    const paragraph = node('p');
    paragraph.append(node('strong', '', `정답: ${answer}`), document.createElement('br'), document.createTextNode(explanation));
    details.append(paragraph);
    container.append(details);
  }

  function renderPlaces(data) {
    places = data;
    placeButtons.replaceChildren();
    places.forEach((place) => {
      const button = node('button', '', place.id === 'school' ? '우리 학교' : place.name);
      button.type = 'button';
      button.dataset.place = place.id;
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => selectPlace(place.id));
      placeButtons.append(button);
    });
  }

  function renderMissions(missions) {
    const parent = $('#map-missions');
    parent.replaceChildren();
    missions.forEach((mission, index) => {
      const card = node('article', 'mission-card');
      card.append(node('span', 'mission-number', `MAP MISSION 0${index + 1}`), node('h4', '', mission.question));
      card.append(node('p', 'choices', mission.choices.join('  /  ')));
      appendAnswer(card, mission.answer, mission.explanation);
      parent.append(card);
    });
  }

  function renderQuizzes(missions) {
    const quizzes = [
      { question: '북쪽이 위인 지도에서 오른쪽은 어느 방향일까요?', choices: ['동쪽', '서쪽'], answer: '동쪽', explanation: '북쪽이 위인 지도에서 오른쪽이 동쪽이에요.' },
      { question: '범례에서는 무엇을 알 수 있을까요?', choices: ['기호의 뜻', '오늘의 날씨'], answer: '기호의 뜻', explanation: '범례는 지도에 쓰인 기호가 무엇을 뜻하는지 알려 줘요.' },
      missions[0]
    ].filter(Boolean);
    const parent = $('#quiz-list');
    parent.replaceChildren();
    quizzes.forEach((quiz, index) => {
      const card = node('article', 'quiz-card');
      const head = node('div', 'quiz-head');
      head.append(node('span', 'quiz-number', `0${index + 1}`), node('h3', '', quiz.question));
      const options = node('div', 'quiz-options');
      options.setAttribute('role', 'group');
      options.setAttribute('aria-label', `${index + 1}번 문제 선택지`);
      quiz.choices.forEach((choice) => {
        const button = node('button', 'quiz-option', choice);
        button.type = 'button';
        button.setAttribute('aria-pressed', 'false');
        button.addEventListener('click', () => {
          $$('.quiz-option', options).forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
          announce(`${choice} 선택. 정답은 정답과 설명 보기에서 확인하세요.`);
        });
        options.append(button);
      });
      card.append(head, options);
      appendAnswer(card, quiz.answer, quiz.explanation);
      parent.append(card);
    });
  }

  async function loadLessonData() {
    try {
      const response = await fetch('assets/lesson.json');
      if (!response.ok) throw new Error('lesson data unavailable');
      const data = await response.json();
      if (!Array.isArray(data.places) || !Array.isArray(data.missions) || data.missions.length < 2) throw new Error('lesson data incomplete');
      renderPlaces(data.places);
      renderMissions(data.missions);
      renderQuizzes(data.missions);
      attachMapEvents();
    } catch (_) {
      $('#map-missions').textContent = '지도 자료를 불러오지 못했어요. 페이지를 새로고침하거나 PDF 활동지를 확인해 주세요.';
      placeInfo.textContent = '장소 설명을 불러오지 못했어요. 지도 안의 범례를 확인해 주세요.';
      renderQuizzes([]);
      announce('수업 자료 일부를 불러오지 못했습니다. 페이지를 새로고침해 주세요.');
    }
  }

  showStep(0, { keepPosition: true });
  loadLessonData();
})();
