(() => {
  const root = document.documentElement;
  const body = document.body;
  const header = document.querySelector('.site-header');
  const themeButton = document.querySelector('.theme-toggle');
  const languageButton = document.querySelector('.language-toggle');
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  const cvLink = document.querySelector('.nav-cv');
  const cvLabel = document.querySelector('.cv-label');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const copy = {
    en: {
      navResearch: 'Research', navProjects: 'Projects', navProfile: 'Education',
      heroEyebrow: 'Mathematics × Trustworthy AI',
      heroTitle: 'I build AI systems that <span class="gradient-text">test before they trust.</span>',
      heroLede: 'I am <strong>Xihang Shan</strong> (单夕航), a mathematics undergraduate at Xiamen University. My research connects trustworthy machine learning, AI agents, causal decision-making, neural algorithmic reasoning, and knowledge graphs. I am grateful to my undergraduate mentors, <a class="mentor-link" href="https://zhoudalab.github.io/" target="_blank" rel="noopener">Prof. Da Zhou</a> and <a class="mentor-link" href="https://github.com/luoye-group/" target="_blank" rel="noopener">Prof. Ye Luo</a>, for their guidance.',
      exploreResearch: 'Explore research', getInTouch: 'Get in touch',
      localTime: 'Beijing time', lastUpdated: 'Updated', pageViews: 'Views', visitorIp: 'IP', locationHongKong: 'Hong Kong, China',
      selectedManuscripts: 'Selected manuscripts', researchTitle: 'Research that questions its assumptions.',
      researchIntro: 'Across causal learning, agents, and graphs, I design controls that reveal when external knowledge helps—and when a model should refuse it.',
      filterAll: 'All', filterCausal: 'Causal AI', filterAgents: 'Agents', filterGraphs: 'Graphs & reasoning',
      venueNeurips: 'NeurIPS 2026 · Under review', venueAaai: 'AAAI 2027 · Under review',
      venueEmnlp: 'EMNLP 2026 · Under review', venuePricai: 'PRICAI 2026 · Under review',
      reviewNote: '<span></span>Post-rebuttal reviews: <strong>4/4/5</strong>', corresponding: '<sup>*</sup> Corresponding author.',
      prcdDiagramTitle: 'Calibrate trust before using a prior', prcdData: 'Observational data', prcdPrior: 'Imperfect prior',
      prcdFeatures: 'Local edge features', prcdTrust: 'EB + topology MLP<br><small>per-edge trust τ</small>',
      prcdMap: 'Prior-aware MAP<br><small>adaptive ℓ₁ + ℓ₂</small>', prcdGraph: 'Calibrated causal graph',
      prcdNote: 'Useful structure is retained; contradictions suppress trust.',
      prcdDesc: 'Learns edge-specific trust from data, using useful prior structure while safely reverting to data-only discovery when the prior is misleading.',
      cdvDiagramTitle: 'Test competing causal worlds online', cdvLogs: 'Historical logs', cdvAssumptions: 'Unreliable graph',
      cdvWorlds: 'Candidate worlds<br><small>naive · causal · cold</small>', cdvProbe: 'Diagnostic action', cdvEvidence: 'Online evidence',
      cdvDecision: 'Rescue or veto<br><small>then choose an arm</small>', cdvNote: 'Prediction error continuously updates trust in every world.',
      cdvDesc: 'Treats historical causal knowledge as a hypothesis to be tested online; diagnostic falsification and a causal veto keep misleading graphs from steering decisions.',
      deltaDiagramTitle: 'Copy what is safe; repair what changed', deltaGraph: 'Post-edit graph', deltaMemory: 'Previous solution', deltaEdit: 'Edit event',
      deltaProcess: 'Edit encoder<br><small>semiring messages</small>', deltaGates: 'Two gates<br><small>affected · copy-safe</small>',
      deltaCopy: 'Safe → copy', deltaRepair: 'Unsafe → recompute', deltaOutput: 'Updated solution',
      deltaNote: 'The old witness becomes a first-class computational resource.',
      deltaDesc: 'Separates state that remains valid after a graph update from state that must be recomputed, enabling incremental reasoning without unsafe copying.',
      claimDiagramTitle: 'Name the claim before choosing the score', claimFailure: 'Failed source plan',
      claimTargets: 'Changed targets<br><small>positive · contrastive</small>', claimPrompts: 'Evaluation probes<br><small>trace · reflection · invariant</small>',
      claimOutputs: 'Frozen agent outputs', claimMetrics: 'Metric stack<br><small>exact · core · transfer · execution</small>',
      claimReport: 'Auditable claim report', claimNote: 'The same output can support different conclusions under different controls.',
      claimDesc: 'Uses claim-matched controls to distinguish repair, transfer, target-solving, and executable validity from ordinary task success.',
      bpcDiagramTitle: 'Keep full paths; expose only what routing needs', bpcQuestion: 'Question + start entities',
      bpcMemory: 'Symbolic beam memory<br><small>complete paths retained</small>', bpcWindow: 'Visible suffix h<sub>K</sub><br><small>at most K hops</small>',
      bpcSelect: 'LLM relation selection', bpcExpand: 'Expand + retain beam', bpcAnswer: 'Full-path answer extraction',
      bpcNote: 'Routing repeats with bounded text while exact state stays outside the prompt.',
      bpcDesc: 'Uses bounded visible path history to reduce prompt exposure while preserving effective, auditable symbolic reasoning.',
      rcdaDiagramTitle: 'Hold the recipe fixed; expose hidden levers', rcdaDatasets: 'Knowledge-graph datasets', rcdaRecipe: 'One fixed training recipe',
      rcdaGrid: 'Matched grid<br><small>decoder × encoder depth</small>', rcdaMetrics: 'MRR / Hits with seeds',
      rcdaDescriptors: 'Audit descriptors<br><small>e/r · symmetry · provenance</small>', rcdaChecklist: 'Controlled reporting checklist',
      rcdaNote: 'Architectural conclusions are conditioned on decoder, depth, data, and recipe.',
      rcdaDesc: 'Shows how decoder choice and training recipe can confound structural KGC comparisons, motivating controlled reporting across architectures and datasets.',
      selectedProjects: 'Other projects', projectsTitle: 'Open, inspectable research systems.',
      locsourceType: '03 / Spatial AI', locsourceDesc: 'Conservative, auditable transcript-ownership proposals for Xenium post-segmentation analysis.',
      booleanType: '02 / Discrete structure', booleanDesc: 'Walsh-spectral affine approximation, derivative-guided affine covers, and feedforward sequence recovery.',
      memoryType: '01 / Research agents', memoryDesc: 'Bounded, claim-relevant memory views and fail-closed evidence auditing for research agents.',
      repoReport: 'Repository & report ↗', openRepository: 'Open repository ↗', educationRecognition: 'Education & recognition', educationLabel: 'Education', recognitionLabel: 'Recognition',
      xmu: 'Xiamen University', educationDegree: 'B.S. in Mathematics and Applied Mathematics<br>School of Mathematical Sciences',
      honorOne: '<b>Fujian First Prize</b><br>National Undergraduate Mathematical Modeling Contest · Team Leader',
      honorTwo: '<b>Fujian Third Prize</b><br>National Undergraduate Mathematical Modeling Contest · Team Leader',
      honorThree: '<b>Outstanding Student</b><br>Cryptography & Mathematics Summer School',
      hobbies: 'Beyond research', hobbiesTitle: 'Things I enjoy away from the screen.', basketball: 'Basketball', basketballNote: 'Long-time NBA fan · Always happy to talk basketball', billiards: 'Billiards', piano: 'Piano', bridge: 'Bridge', touchRugby: 'Touch Rugby',
      contact: 'Contact', contactTitle: 'Open to conversation<br>and collaboration.', emailMe: 'Email me',
      wechat: 'WeChat', wechatTitle: 'Scan to connect', wechatNote: 'Add a short note with your name and research interests.',
      footerLine: 'Built for clarity, motion, and evidence.', backTop: 'Back to top ↑',
      orbitCausal: 'Causal AI', orbitAgents: 'Agents', orbitGraphs: 'Graphs',
      signalPrior: 'Prior', signalCalibrate: 'calibrate', signalState: 'State', signalRecompute: 'recompute', signalClaim: 'Claim', signalControl: 'control'
    },
    zh: {
      navResearch: '研究', navProjects: '项目', navProfile: '教育',
      heroEyebrow: '数学 × 可信人工智能',
      heroTitle: '我构建<span class="gradient-text">先验证、再信任的人工智能系统。</span>',
      heroLede: '我是<strong>单夕航（Xihang Shan）</strong>，厦门大学数学与应用数学专业本科生。我的研究涉及可信机器学习、智能体、因果决策、神经算法推理与知识图谱。感谢本科导师<a class="mentor-link" href="https://zhoudalab.github.io/" target="_blank" rel="noopener">周达教授</a>与<a class="mentor-link" href="https://github.com/luoye-group/" target="_blank" rel="noopener">罗晔副教授</a>的指导。',
      exploreResearch: '查看研究', getInTouch: '联系我',
      localTime: '北京时间', lastUpdated: '最后更新', pageViews: '浏览量', visitorIp: 'IP', locationHongKong: '中国香港',
      selectedManuscripts: '代表性论文', researchTitle: '让模型先检验，再相信。',
      researchIntro: '围绕因果学习、智能体与图推理，我研究如何判断外部知识何时有效，以及模型何时应当拒绝使用它。',
      filterAll: '全部', filterCausal: '因果 AI', filterAgents: '智能体', filterGraphs: '图与推理',
      venueNeurips: 'NeurIPS 2026 · 审稿中', venueAaai: 'AAAI 2027 · 审稿中',
      venueEmnlp: 'EMNLP 2026 · 审稿中', venuePricai: 'PRICAI 2026 · 审稿中',
      reviewNote: '<span></span>Rebuttal 后评分：<strong>4/4/5</strong>', corresponding: '<sup>*</sup> 通讯作者。',
      prcdDiagramTitle: '先校准信任，再使用先验', prcdData: '观测数据', prcdPrior: '不可靠先验',
      prcdFeatures: '局部边特征', prcdTrust: '经验贝叶斯 + 拓扑 MLP<br><small>逐边信任度 τ</small>',
      prcdMap: '先验感知 MAP<br><small>自适应 ℓ₁ + ℓ₂</small>', prcdGraph: '校准后的因果图',
      prcdNote: '保留有用结构；数据矛盾会压低信任。',
      prcdDesc: '从数据中学习逐边信任度：先验可靠时利用其结构，先验误导时自动退回以数据为主的因果发现。',
      cdvDiagramTitle: '在线检验相互竞争的因果世界', cdvLogs: '历史日志', cdvAssumptions: '不可靠因果图',
      cdvWorlds: '候选世界<br><small>朴素 · 因果 · 冷启动</small>', cdvProbe: '诊断性动作', cdvEvidence: '在线干预证据',
      cdvDecision: '救援或否决<br><small>随后选择动作</small>', cdvNote: '预测误差持续更新每个候选世界的信任权重。',
      cdvDesc: '把历史因果知识视为需要在线检验的假设；通过诊断性证伪和因果否决，避免错误图结构主导决策。',
      deltaDiagramTitle: '安全的状态直接复用，变化的部分局部修复', deltaGraph: '编辑后的图', deltaMemory: '上一时刻解', deltaEdit: '局部编辑事件',
      deltaProcess: '编辑编码器<br><small>半环消息传递</small>', deltaGates: '双门控<br><small>受影响区 · 复制安全</small>',
      deltaCopy: '安全 → 复制', deltaRepair: '不安全 → 重算', deltaOutput: '更新后的解',
      deltaNote: '将旧解从普通特征变成可直接复用的计算资源。',
      deltaDesc: '区分图更新后仍然有效的状态与必须重新计算的状态，实现避免不安全复制的增量推理。',
      claimDiagramTitle: '先明确科学主张，再选择评价指标', claimFailure: '失败的源任务计划',
      claimTargets: '发生变化的目标任务<br><small>正迁移 · 对照迁移</small>', claimPrompts: '评价探针<br><small>轨迹 · 反思 · 不变量</small>',
      claimOutputs: '冻结的智能体输出', claimMetrics: '指标栈<br><small>精确 · 核心 · 迁移 · 执行</small>',
      claimReport: '可审计的主张报告', claimNote: '同一输出在不同控制条件下可能支持完全不同的结论。',
      claimDesc: '以主张匹配的控制实验，将修复、迁移、目标求解与可执行有效性从普通任务成功率中分离出来。',
      bpcDiagramTitle: '保留完整路径，只向模型暴露路由所需部分', bpcQuestion: '问题 + 起始实体',
      bpcMemory: '符号化束搜索记忆<br><small>完整路径始终保留</small>', bpcWindow: '可见后缀 h<sub>K</sub><br><small>最多 K 跳</small>',
      bpcSelect: 'LLM 关系选择', bpcExpand: '扩展并保留候选路径', bpcAnswer: '基于完整路径提取答案',
      bpcNote: '路由时重复使用有界文本，精确符号状态始终保存在提示词之外。',
      bpcDesc: '限制模型可见的路径历史，在减少提示词暴露的同时保留有效且可审计的符号推理。',
      rcdaDiagramTitle: '固定训练配方，暴露被隐藏的结构变量', rcdaDatasets: '知识图谱数据集', rcdaRecipe: '统一训练配方',
      rcdaGrid: '匹配实验网格<br><small>解码器 × 编码器深度</small>', rcdaMetrics: '多随机种子的 MRR / Hits',
      rcdaDescriptors: '审计描述量<br><small>边/关系 · 对称性 · 数据来源</small>', rcdaChecklist: '受控报告清单',
      rcdaNote: '架构结论取决于解码器、深度、数据集与训练配方。',
      rcdaDesc: '揭示解码器选择与训练配方如何混淆结构化知识图谱补全比较，并推动跨架构、跨数据集的受控报告。',
      selectedProjects: '其它项目', projectsTitle: '开放且可审查的研究系统。',
      locsourceType: '03 / 空间组学 AI', locsourceDesc: '面向 Xenium 后分割分析的保守、可审计转录本归属提案。',
      booleanType: '02 / 离散结构', booleanDesc: 'Walsh 谱仿射逼近、导数引导的仿射覆盖与前馈序列恢复。',
      memoryType: '01 / 研究智能体', memoryDesc: '面向研究智能体的有界、主张相关记忆视图，以及失败关闭式证据审计。',
      repoReport: '代码与报告 ↗', openRepository: '查看代码仓库 ↗', educationRecognition: '教育经历与荣誉', educationLabel: '教育经历', recognitionLabel: '荣誉',
      xmu: '厦门大学', educationDegree: '数学与应用数学 理学学士<br>数学科学学院',
      honorOne: '<b>福建省一等奖</b><br>全国大学生数学建模竞赛 · 队长',
      honorTwo: '<b>福建省三等奖</b><br>全国大学生数学建模竞赛 · 队长',
      honorThree: '<b>优秀学员</b><br>密码与数学暑期学校',
      hobbies: '个人爱好', hobbiesTitle: '研究之外，也认真享受生活。', basketball: '篮球', basketballNote: 'NBA 资深球迷 · 欢迎一起聊球', billiards: '台球', piano: '钢琴', bridge: '桥牌', touchRugby: '触式橄榄球',
      contact: '联系', contactTitle: '欢迎交流与合作。', emailMe: '发送邮件',
      wechat: '微信', wechatTitle: '扫码添加微信', wechatNote: '添加时请简单备注姓名与研究方向。',
      footerLine: '为清晰、证据与可审查性而构建。', backTop: '返回顶部 ↑',
      orbitCausal: '因果 AI', orbitAgents: '智能体', orbitGraphs: '图推理',
      signalPrior: '先验', signalCalibrate: '校准', signalState: '状态', signalRecompute: '重算', signalClaim: '主张', signalControl: '控制'
    }
  };

  let currentLanguage = localStorage.getItem('xihang-language') === 'zh' ? 'zh' : 'en';

  function navigationLabel(open) {
    if (currentLanguage === 'zh') return open ? '关闭导航' : '打开导航';
    return open ? 'Close navigation' : 'Open navigation';
  }

  function formatBeijing(date) {
    const parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    }).formatToParts(date).reduce((map, part) => ((map[part.type] = part.value), map), {});
    return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second} UTC+8`;
  }

  function refreshTimes() {
    document.getElementById('current-time').textContent = formatBeijing(new Date());
    const updatedAt = document.querySelector('.hero-meta').dataset.updated;
    document.getElementById('last-updated').textContent = formatBeijing(new Date(updatedAt));
  }

  function applyLanguage(language) {
    currentLanguage = language;
    root.lang = language === 'zh' ? 'zh-CN' : 'en';
    root.dataset.language = language;
    document.querySelectorAll('[data-i18n]').forEach(element => {
      const value = copy[language][element.dataset.i18n];
      if (value) element.textContent = value;
    });
    document.querySelectorAll('[data-i18n-html]').forEach(element => {
      const value = copy[language][element.dataset.i18nHtml];
      if (value) element.innerHTML = value;
    });
    languageButton.textContent = language === 'zh' ? 'English' : '中文版';
    languageButton.setAttribute('aria-label', language === 'zh' ? 'Switch to English' : '切换到中文');
    cvLink.href = language === 'zh' ? 'assets/Xihang_Shan_CV_CN.pdf' : 'assets/Xihang_Shan_CV_EN.pdf';
    cvLabel.textContent = language === 'zh' ? '简历' : 'CV';
    navToggle.setAttribute('aria-label', navigationLabel(navToggle.getAttribute('aria-expanded') === 'true'));
    document.querySelector('.skip-link').textContent = language === 'zh' ? '跳到正文' : 'Skip to content';
    document.title = language === 'zh' ? 'ShanXihang — 可信与结构化人工智能' : 'ShanXihang — Trustworthy & Structured AI';
    localStorage.setItem('xihang-language', language);
    refreshTimes();
  }

  const savedTheme = localStorage.getItem('xihang-theme');
  const initialTheme = savedTheme || 'dark';
  root.dataset.theme = initialTheme;
  themeMeta.setAttribute('content', initialTheme === 'light' ? '#f8f5fc' : '#07050a');

  themeButton.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('xihang-theme', next);
    themeMeta.setAttribute('content', next === 'light' ? '#f8f5fc' : '#07050a');
  });

  languageButton.addEventListener('click', () => applyLanguage(currentLanguage === 'en' ? 'zh' : 'en'));
  applyLanguage(currentLanguage);
  refreshTimes();
  setInterval(refreshTimes, 1000);

  async function loadLiveMeta() {
    const viewElement = document.getElementById('page-views');
    const site = 'andyshan11.github.io';
    const path = '/';
    const base = 'https://page-views-api.ratneshc.com/api/v1';
    try {
      if (location.hostname === site) {
        await fetch(`${base}/track?site=${encodeURIComponent(site)}&path=${encodeURIComponent(path)}`, { cache: 'no-store', keepalive: true });
      }
      const response = await fetch(`${base}/views?site=${encodeURIComponent(site)}&path=${encodeURIComponent(path)}`, { cache: 'no-store' });
      const data = await response.json();
      if (Number.isFinite(Number(data.views))) viewElement.textContent = Number(data.views).toLocaleString('en-US');
    } catch (_) {
      viewElement.textContent = '—';
    }
  }
  loadLiveMeta();

  const closeNav = () => {
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', navigationLabel(false));
    navLinks.classList.remove('open');
    body.classList.remove('nav-open');
  };

  navToggle.addEventListener('click', () => {
    const open = navToggle.getAttribute('aria-expanded') !== 'true';
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', navigationLabel(open));
    navLinks.classList.toggle('open', open);
    body.classList.toggle('nav-open', open);
  });
  navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));

  window.addEventListener('scroll', () => header.classList.toggle('scrolled', window.scrollY > 16), { passive: true });
  document.getElementById('year').textContent = new Date().getFullYear();

  const wechatDialog = document.querySelector('.wechat-dialog');
  const wechatTrigger = document.querySelector('.wechat-trigger');
  const wechatClose = document.querySelector('.wechat-close');
  wechatTrigger?.addEventListener('click', () => {
    if (typeof wechatDialog.showModal === 'function') wechatDialog.showModal();
    else wechatDialog.setAttribute('open', '');
  });
  wechatClose?.addEventListener('click', () => wechatDialog.close());
  wechatDialog?.addEventListener('click', event => {
    const rect = wechatDialog.getBoundingClientRect();
    const inside = event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom;
    if (!inside) wechatDialog.close();
  });

  if (!reducedMotion) {
    window.addEventListener('pointermove', event => {
      root.style.setProperty('--pointer-x', `${event.clientX}px`);
      root.style.setProperty('--pointer-y', `${event.clientY}px`);
    }, { passive: true });
  }

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reducedMotion) {
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.11, rootMargin: '0px 0px -40px' });
    revealItems.forEach((item, index) => {
      item.style.transitionDelay = `${Math.min((index % 4) * 55, 165)}ms`;
      revealObserver.observe(item);
    });
  } else {
    revealItems.forEach(item => item.classList.add('visible'));
  }

  const filters = document.querySelectorAll('.filter');
  const publications = document.querySelectorAll('.pub-card');
  filters.forEach(filter => {
    filter.addEventListener('click', () => {
      filters.forEach(button => button.classList.remove('active'));
      filter.classList.add('active');
      const topic = filter.dataset.filter;
      publications.forEach(card => {
        const show = topic === 'all' || card.dataset.topic === topic;
        card.classList.toggle('hidden', !show);
      });
    });
  });

  const methodVideos = [...document.querySelectorAll('.publication-animation')];
  const playMethodVideo = video => video.play().catch(() => {
    video.closest('.publication-figure')?.classList.add('video-unavailable');
  });
  methodVideos.forEach(video => {
    video.addEventListener('error', () => video.closest('.publication-figure')?.classList.add('video-unavailable'));
  });
  if (reducedMotion) {
    methodVideos.forEach(video => {
      video.pause();
      video.removeAttribute('autoplay');
    });
  } else if ('IntersectionObserver' in window) {
    const videoObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const video = entry.target;
        if (entry.isIntersecting && document.visibilityState === 'visible') playMethodVideo(video);
        else video.pause();
      });
    }, { threshold: 0.08, rootMargin: '180px 0px' });
    methodVideos.forEach(video => {
      video.pause();
      videoObserver.observe(video);
    });
    document.addEventListener('visibilitychange', () => {
      methodVideos.forEach(video => {
        if (document.hidden) video.pause();
        else if (video.getBoundingClientRect().top < innerHeight && video.getBoundingClientRect().bottom > 0) playMethodVideo(video);
      });
    });
  } else {
    methodVideos.forEach(playMethodVideo);
  }

  if (!reducedMotion && matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('.pub-card').forEach(card => {
      card.addEventListener('pointermove', event => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - .5;
        const y = (event.clientY - rect.top) / rect.height - .5;
        card.style.transform = `perspective(900px) rotateX(${-y * 2.2}deg) rotateY(${x * 2.2}deg) translateY(-2px)`;
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });
  }

  const sections = [...document.querySelectorAll('main section[id]')];
  const navAnchors = [...document.querySelectorAll('.nav-links a')];
  const sectionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navAnchors.forEach(anchor => anchor.classList.toggle('active', anchor.getAttribute('href') === `#${entry.target.id}`));
      }
    });
  }, { rootMargin: '-35% 0px -58%', threshold: 0 });
  sections.forEach(section => sectionObserver.observe(section));

  const canvas = document.getElementById('network-canvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let frame;
  let pointer = { x: -9999, y: -9999 };

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.min(devicePixelRatio, 2);
    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    const count = Math.min(72, Math.max(34, Math.floor(rect.width / 19)));
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height * .86,
      vx: (Math.random() - .5) * .16,
      vy: (Math.random() - .5) * .16,
      r: Math.random() * 1.15 + .45
    }));
  }

  function drawNetwork() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    ctx.clearRect(0, 0, width, height);
    const light = root.dataset.theme === 'light';
    particles.forEach((particle, index) => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      if (particle.x < 0 || particle.x > width) particle.vx *= -1;
      if (particle.y < 0 || particle.y > height * .9) particle.vy *= -1;
      const dxPointer = pointer.x - particle.x;
      const dyPointer = pointer.y - particle.y;
      const pointerDistance = Math.hypot(dxPointer, dyPointer);
      if (pointerDistance < 140) {
        particle.x -= dxPointer * .0007;
        particle.y -= dyPointer * .0007;
      }
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.r, 0, Math.PI * 2);
      ctx.fillStyle = light ? 'rgba(118,80,173,.36)' : 'rgba(197,163,255,.44)';
      ctx.fill();
      for (let j = index + 1; j < particles.length; j++) {
        const other = particles[j];
        const distance = Math.hypot(particle.x - other.x, particle.y - other.y);
        if (distance < 118) {
          ctx.beginPath();
          ctx.moveTo(particle.x, particle.y);
          ctx.lineTo(other.x, other.y);
          ctx.strokeStyle = light
            ? `rgba(118,80,173,${(1 - distance / 118) * .13})`
            : `rgba(197,163,255,${(1 - distance / 118) * .16})`;
          ctx.lineWidth = .6;
          ctx.stroke();
        }
      }
    });
    frame = requestAnimationFrame(drawNetwork);
  }

  canvas.addEventListener('pointermove', event => {
    const rect = canvas.getBoundingClientRect();
    pointer = { x: event.clientX - rect.left, y: event.clientY - rect.top };
  });
  canvas.addEventListener('pointerleave', () => { pointer = { x: -9999, y: -9999 }; });
  resizeCanvas();
  if (!reducedMotion) drawNetwork(); else drawNetwork(), cancelAnimationFrame(frame);
  window.addEventListener('resize', resizeCanvas, { passive: true });
})();
