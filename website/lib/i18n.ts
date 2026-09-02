export type Language = "en" | "az" | "ru";

export interface Translations {
  nav: {
    brand: string;
    features: string;
    ctfs: string;
    wiki: string;
    faq: string;
    download: string;
    releases: string;
    github: string;
    security: string;
    about: string;
  };
  hero: {
    title: string;
    subtitle: string;
    tagline: string;
    downloadBtn: string;
    exploreCtfsBtn: string;
    supportedProtocols: string;
    terminalBadge: string;
    demoNote: string;
  };
  features: {
    sectionTitle: string;
    sectionSubtitle: string;
    nmapTitle: string;
    nmapDesc: string;
    transportTitle: string;
    transportDesc: string;
    smbTitle: string;
    smbDesc: string;
    multiTargetTitle: string;
    multiTargetDesc: string;
    protocolsTitle: string;
    protocolsDesc: string;
    diagnosticsTitle: string;
    diagnosticsDesc: string;
    bugTrackerTitle: string;
    bugTrackerDesc: string;
    videoCenterTitle: string;
    videoCenterDesc: string;
  };
  ctf: {
    sectionTitle: string;
    sectionSubtitle: string;
    dashboardTitle: string;
    yourProgress: string;
    difficulty: string;
    points: string;
    startChallenge: string;
    terminalTitle: string;
    availableCommands: string;
    targetAssigned: string;
    simulatedWarning: string;
    flagPrompt: string;
    submitFlag: string;
    flagAccepted: string;
    flagIncorrect: string;
    hintsTitle: string;
    useHint: string;
    hintPenalty: string;
    completed: string;
    locked: string;
    vaultTitle: string;
    noFlagsYet: string;
    challengesCount: string;
    scoreLabel: string;
    rankLabel: string;
    completedBadge: string;
    resetProgress: string;
    hintUnlocked: string;
    unlockHintWarning: string;
    cancel: string;
    confirm: string;
  };
  download: {
    title: string;
    subtitle: string;
    pipxTab: string;
    debianTab: string;
    sourceTab: string;
    wslTab: string;
    ensurepathTip: string;
    reloadTip: string;
    releaseInfo: string;
    latestReleaseBadge: string;
    quickInstallTitle: string;
    recommendedMethod: string;
    requirementsTitle: string;
  };
  wiki: {
    title: string;
    subtitle: string;
    searchPlaceholder: string;
    categories: string;
    readDoc: string;
  };
  faq: {
    title: string;
    subtitle: string;
    stillQuestions: string;
    askGithub: string;
  };
  releases: {
    title: string;
    subtitle: string;
    latestBadge: string;
    viewOnGithub: string;
    publishedOn: string;
    changelog: string;
    assets: string;
    noReleases: string;
  };
  about: {
    title: string;
    subtitle: string;
    missionTitle: string;
    architectureTitle: string;
    ethicsTitle: string;
  };
  security: {
    title: string;
    subtitle: string;
    authorizedTitle: string;
    simulationTitle: string;
    reportingTitle: string;
  };
  footer: {
    tagline: string;
    product: string;
    resources: string;
    legal: string;
    languages: string;
    copyright: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    nav: {
      brand: "CrackMapExec+",
      features: "Features",
      ctfs: "CTFs",
      wiki: "Wiki",
      faq: "FAQ",
      download: "Download",
      releases: "Releases",
      github: "GitHub",
      security: "Security",
      about: "About",
    },
    hero: {
      title: "CrackMapExec+",
      subtitle: "Modern Network Security Intelligence & Enumeration Framework",
      tagline: "Engineered for authorized security laboratories, CTFs, TryHackMe, Hack The Box, academic research, and educational seminars.",
      downloadBtn: "Download Now",
      exploreCtfsBtn: "Explore Mini-CTFs",
      supportedProtocols: "Supported Protocols",
      terminalBadge: "LIVE CME+ TERMINAL SIMULATION",
      demoNote: "All preview commands run in an isolated in-browser simulation. Zero external network packets transmitted.",
    },
    features: {
      sectionTitle: "Engineered For Precision & Reliability",
      sectionSubtitle: "Discover the architectural innovations powering next-generation Active Directory and network protocol interrogation.",
      nmapTitle: "Nmap Intelligence Engine",
      nmapDesc: "Ingest standard -oN scan reports, automatically resolve supported protocols, inventory services, and preview execution plans before probe transmission.",
      transportTitle: "Universal TransportEngine",
      transportDesc: "Strict 8-stage connection state machine decoupling Layer 4 TCP reachability from Layer 7 protocol handshakes, session setup, and authentication.",
      smbTitle: "Rich SMB Intelligence",
      smbDesc: "Deep NTLMSSP TargetInfo AV_PAIR extraction revealing authentic hostnames, domains, forests, Windows NT builds, SMB dialect negotiation, and signing policies.",
      multiTargetTitle: "Advanced Target Management",
      multiTargetDesc: "Full support for single IPs, CIDR blocks (/24, /29), octet ranges (10.0.0.1-50), comma-separated lists, and target files with comment parsing.",
      protocolsTitle: "Native Multi-Protocol Support",
      protocolsDesc: "Modular protocol drivers for SMB, LDAP (RootDSE & SASL), WinRM (WS-Man WWW-Authenticate), and SSH (RFC 4253 banner analysis).",
      diagnosticsTitle: "10-Point Doctor Diagnostics",
      diagnosticsDesc: "Comprehensive health check verifying Python version, installation integrity, PATH binaries, core dependencies, protocol adapters, and Git state.",
      bugTrackerTitle: "Automated Bug Tracker",
      bugTrackerDesc: "Privacy-conscious local bug registry generating sanitized markdown reports with deterministic fingerprint deduplication.",
      videoCenterTitle: "Built-in Video Guide Center",
      videoCenterDesc: "Integrated CLI tutorial library with deep-link timestamp calculation (&t=143s) and dynamic protocol recommendations.",
    },
    ctf: {
      sectionTitle: "Interactive Educational Mini-CTF Platform",
      sectionSubtitle: "Practice network protocol enumeration, header analysis, and reconnaissance techniques inside our safe, fully simulated sandbox.",
      dashboardTitle: "CTF Challenges & Flag Vault",
      yourProgress: "Your Progress",
      difficulty: "Difficulty",
      points: "Points",
      startChallenge: "Start Challenge",
      terminalTitle: "CrackMapExec+ Virtual Terminal",
      availableCommands: "Available simulated commands: help, target, scan, nmap, smb, ldap, winrm, ssh, inspect, history, clear",
      targetAssigned: "Target Assigned",
      simulatedWarning: "SIMULATED TARGET: This address exists only inside the CrackMapExec+ CTF simulation. No external network traffic is generated.",
      flagPrompt: "Submit Discovered Flag",
      submitFlag: "Submit Flag",
      flagAccepted: "✓ FLAG ACCEPTED! Challenge completed.",
      flagIncorrect: "✕ Incorrect flag. Keep investigating the simulated target.",
      hintsTitle: "Progressive Hints",
      useHint: "Unlock Hint",
      hintPenalty: "penalty",
      completed: "Completed",
      locked: "Locked",
      vaultTitle: "Flag Vault",
      noFlagsYet: "No flags captured yet. Start a challenge above to begin!",
      challengesCount: "Challenges Completed",
      scoreLabel: "Total Score",
      rankLabel: "Operator Rank",
      completedBadge: "COMPLETED",
      resetProgress: "Reset Progress",
      hintUnlocked: "Hint Unlocked",
      unlockHintWarning: "Unlocking this hint will deduct points from your final score:",
      cancel: "Cancel",
      confirm: "Unlock",
    },
    download: {
      title: "Download & Installation",
      subtitle: "Choose the installation method suited for your environment. CrackMapExec+ is ready for Linux, Kali, macOS, and Windows WSL.",
      pipxTab: "pipx (Recommended)",
      debianTab: "Debian / Kali (.deb)",
      sourceTab: "Git Source",
      wslTab: "Windows / WSL",
      ensurepathTip: "If 'crackmapexec+' is not recognized after install, execute 'pipx ensurepath' and restart your terminal.",
      reloadTip: "Always reload your shell or source your rc file after installing global Python binaries.",
      releaseInfo: "Official GitHub Repository: CodingM-eng/CrackMapExec-Plus",
      latestReleaseBadge: "Stable v0.1.0",
      quickInstallTitle: "One-Command Automated Install",
      recommendedMethod: "Recommended for isolated, conflict-free global execution.",
      requirementsTitle: "System Requirements: Python 3.11+, Git, and terminal emulator.",
    },
    wiki: {
      title: "Documentation & Technical Wiki",
      subtitle: "Comprehensive architectural specifications, protocol driver guides, CLI reference, and troubleshooting tutorials.",
      searchPlaceholder: "Search documentation articles...",
      categories: "Categories",
      readDoc: "Read Article",
    },
    faq: {
      title: "Frequently Asked Questions",
      subtitle: "Common questions regarding CrackMapExec+, usage policies, CTF simulation, and comparisons.",
      stillQuestions: "Have additional questions?",
      askGithub: "Ask the Community on GitHub Discussions",
    },
    releases: {
      title: "Official Releases & Changelog",
      subtitle: "Track version history, bug fixes, feature milestones, and published assets from the official repository.",
      latestBadge: "Latest Release",
      viewOnGithub: "View Release on GitHub",
      publishedOn: "Published on",
      changelog: "Changelog & Highlights",
      assets: "Assets & Downloads",
      noReleases: "Fetching latest release data from GitHub API...",
    },
    about: {
      title: "About CrackMapExec+",
      subtitle: "An independent, clean-room educational and security assessment framework designed for authorized environments.",
      missionTitle: "Our Mission",
      architectureTitle: "Decoupled Architecture",
      ethicsTitle: "Ethics & Responsible Security",
    },
    security: {
      title: "Security & Responsible Use Policy",
      subtitle: "Commitment to ethical research, strict target authorization, and educational sandbox isolation.",
      authorizedTitle: "Authorized Testing Scope",
      simulationTitle: "CTF Sandbox Isolation Guarantee",
      reportingTitle: "Responsible Vulnerability Disclosure",
    },
    footer: {
      tagline: "Modern network security intelligence framework for authorized labs, CTFs, and educational research.",
      product: "Product",
      resources: "Resources",
      legal: "Legal & Ethics",
      languages: "Language",
      copyright: "© 2026 CrackMapExec+. Distributed under the MIT License.",
    },
  },
  az: {
    nav: {
      brand: "CrackMapExec+",
      features: "Xüsusiyyətlər",
      ctfs: "CTF-lər",
      wiki: "Bilik Bazası",
      faq: "FAQ",
      download: "Yüklə",
      releases: "Buraxılışlar",
      github: "GitHub",
      security: "Təhlükəsizlik",
      about: "Haqqında",
    },
    hero: {
      title: "CrackMapExec+",
      subtitle: "Müasir Şəbəkə Təhlükəsizliyi Kəşfiyyatı və Sayma Framework-ü",
      tagline: "Səlahiyyətli təhlükəsizlik laboratoriyaları, CTF yarışları, TryHackMe, Hack The Box, elmi araşdırmalar və tədris seminarları üçün xüsusi hazırlanmışdır.",
      downloadBtn: "İndi Yüklə",
      exploreCtfsBtn: "Mini-CTF-ləri Kəşf Et",
      supportedProtocols: "Dəstəklənən Protokollar",
      terminalBadge: "CANLI CME+ TERMİNAL SİMULYASİYASI",
      demoNote: "Bütün önbaxış komandaları təcrid olunmuş brauzer simulyasiyasında işləyir. Xarici şəbəkəyə heç bir paket ötürülmür.",
    },
    features: {
      sectionTitle: "Dəqiqlik və Etibarlılıq Üçün Dizayn Edilmişdir",
      sectionSubtitle: "Yeni nəsil Active Directory və şəbəkə protokollarının yoxlanılmasını təmin edən memarlıq yenilikləri ilə tanış olun.",
      nmapTitle: "Nmap Kəşfiyyat Mühərriki",
      nmapDesc: "Standart -oN skan hesabatlarını təhlil edir, dəstəklənən protokolları avtomatik təyin edir və skandan öncə icra planını nümayiş etdirir.",
      transportTitle: "Universal TransportEngine",
      transportDesc: "Layer 4 TCP əlaqəsini Layer 7 protokol danışıqlarından, sessiya qurulmasından və autentifikasiyadan ayıran 8 mərhələli vəziyyət maşını.",
      smbTitle: "Zəngin SMB Kəşfiyyatı",
      smbDesc: "Dərin NTLMSSP TargetInfo AV_PAIR analizi ilə real kompüter adı, domen, meşə adı, Windows NT versiyası və imzalama siyasəti aşkarlanır.",
      multiTargetTitle: "Təkmil Hədəf İdarəetməsi",
      multiTargetDesc: "Tək IP-lər, CIDR blokları (/24, /29), oktet diapazonları (10.0.0.1-50), vergüllə ayrılmış siyahılar və fayl siyahıları dəstəklənir.",
      protocolsTitle: "Yerli Çox-Protokollu Dəstək",
      protocolsDesc: "SMB, LDAP (RootDSE və SASL), WinRM (WS-Man WWW-Authenticate) və SSH (RFC 4253 banner analizi) üçün xüsusi drayverlər.",
      diagnosticsTitle: "10-Nöqtəli Həkim Diaqnostikası",
      diagnosticsDesc: "Python versiyasını, quraşdırma bütövlüyünü, PATH dəyişənlərini, əsas asılılıqları və Git vəziyyətini yoxlayan tam sağlamlıq testi.",
      bugTrackerTitle: "Avtomatlaşdırılmış Xəta İzləyicisi",
      bugTrackerDesc: "Məxfiliyi qoruyan, həssas məlumatları təmizləyən və dublikatları aradan qaldıran lokal Markdown xəta qeydiyyat sistemi.",
      videoCenterTitle: "Daxili Video Bələdçi Mərkəzi",
      videoCenterDesc: "Dəqiq zaman damğası (&t=143s) hesablaması və dinamik protokol tövsiyələri ilə CLI video tədris bələdçisi.",
    },
    ctf: {
      sectionTitle: "İnteraktiv Tədris Mini-CTF Platforması",
      sectionSubtitle: "Təhlükəsiz, tam simulyasiya edilmiş laboratoriya mühitində şəbəkə protokollarının sayılması və kəşfiyyat vərdişlərinizi inkişaf etdirin.",
      dashboardTitle: "CTF Tapşırıqları və Bayraq Kassası",
      yourProgress: "Sizin İnkişafınız",
      difficulty: "Çətinlik",
      points: "Xallar",
      startChallenge: "Tapşırığa Başla",
      terminalTitle: "CrackMapExec+ Virtual Terminalı",
      availableCommands: "Əlçatan simulyasiya komandaları: help, target, scan, nmap, smb, ldap, winrm, ssh, inspect, history, clear",
      targetAssigned: "Təyin Olunmuş Hədəf",
      simulatedWarning: "SİMULYASİYA HƏDƏFİ: Bu ünvan yalnız CrackMapExec+ CTF simulyasiyasında mövcuddur. Real xarici şəbəkə trafiki yaradılmır.",
      flagPrompt: "Aşkar Edilmiş Bayrağı Təqdim Edin",
      submitFlag: "Bayrağı Göndər",
      flagAccepted: "✓ BAYRAQ QƏBUL EDİLDİ! Tapşırıq uğurla tamamlandı.",
      flagIncorrect: "✕ Yanlış bayraq. Simulyasiya hədəfini araşdırmağa davam edin.",
      hintsTitle: "Mərhələli İpucları",
      useHint: "İpucunu Aç",
      hintPenalty: "cərimə",
      completed: "Tamamlandı",
      locked: "Bağlıdır",
      vaultTitle: "Bayraq Kassası",
      noFlagsYet: "Hələ heç bir bayraq tapılmayıb. Başlamaq üçün yuxarıdakı tapşırıqlardan birini seçin!",
      challengesCount: "Tamamlanan Tapşırıqlar",
      scoreLabel: "Ümumi Xal",
      rankLabel: "Operator Rütbəsi",
      completedBadge: "TAMAMLANDI",
      resetProgress: "İnkişafı Sıfırla",
      hintUnlocked: "İpucu Açıldı",
      unlockHintWarning: "Bu ipucunu açmaq yekun xalınızdan çıxılacaq:",
      cancel: "Ləğv et",
      confirm: "Aç",
    },
    download: {
      title: "Yükləmə və Quraşdırma",
      subtitle: "Mühitinizə uyğun quraşdırma üsulunu seçin. CrackMapExec+ Linux, Kali, macOS və Windows WSL mühitləri üçün tam hazırdır.",
      pipxTab: "pipx (Tövsiyə olunur)",
      debianTab: "Debian / Kali (.deb)",
      sourceTab: "Git Mənbə Kodu",
      wslTab: "Windows / WSL",
      ensurepathTip: "Quraşdırmadan sonra 'crackmapexec+' tapılmazsa, 'pipx ensurepath' icra edin və terminalı yenidən başladın.",
      reloadTip: "Qlobal Python paketlərini quraşdırdıqdan sonra terminal mühitini yeniləyin.",
      releaseInfo: "Rəsmi GitHub Repozitoriyası: CodingM-eng/CrackMapExec-Plus",
      latestReleaseBadge: "Stabil v0.1.0",
      quickInstallTitle: "Tək Komanda ilə Avtomatik Quraşdırma",
      recommendedMethod: "Sistem paketləri ilə toqquşmadan qlobal istifadə üçün ən yaxşı üsul.",
      requirementsTitle: "Sistem Tələbləri: Python 3.11+, Git və terminal emulyatoru.",
    },
    wiki: {
      title: "Texniki Sənədləşmə və Bilik Bazası",
      subtitle: "Memarlıq spesifikasiyaları, protokol drayverləri üzrə bələdçilər, CLI referansı və xəta həlli məqalələri.",
      searchPlaceholder: "Sənədlər üzrə axtarış...",
      categories: "Kateqoriyalar",
      readDoc: "Məqaləni Oxu",
    },
    faq: {
      title: "Tez-Tez Verilən Suallar",
      subtitle: "CrackMapExec+, istifadə qaydaları, CTF simulyasiyası və təhlükəsizlik barədə ümumi suallar.",
      stillQuestions: "Əlavə suallarınız var?",
      askGithub: "GitHub Müzakirələrində İcma ilə Əlaqə Saxlayın",
    },
    releases: {
      title: "Rəsmi Buraxılışlar və Yeniliklər",
      subtitle: "Versiya tarixçəsi, xəta düzəlişləri, yeni funksiyalar və rəsmi repozitoriya faylları.",
      latestBadge: "Son Buraxılış",
      viewOnGithub: "GitHub-da Bax",
      publishedOn: "Yayımlanma tarixi",
      changelog: "Yeniliklər Siyahısı",
      assets: "Fayllar və Yükləmələr",
      noReleases: "GitHub API-dən məlumatlar əldə edilir...",
    },
    about: {
      title: "CrackMapExec+ Haqqında",
      subtitle: "Səlahiyyətli mühitlər üçün sıfırdan müasir memarlıqla yazılmış müstəqil tədris və təhlükəsizlik framework-ü.",
      missionTitle: "Missiyamız",
      architectureTitle: "Modul Memarlıq",
      ethicsTitle: "Etika və Məsuliyyətli Təhlükəsizlik",
    },
    security: {
      title: "Təhlükəsizlik və Məsuliyyətli İstifadə Siyasəti",
      subtitle: "Etik tədqiqatlara, səlahiyyətli sınaqlara və təhsil simulyasiyasının təcridinə sadiqlik.",
      authorizedTitle: "Səlahiyyətli Test Çərçivəsi",
      simulationTitle: "CTF Sandbox Təcrid Zəmanəti",
      reportingTitle: "Məsuliyyətli Xəta Bildirişi",
    },
    footer: {
      tagline: "Səlahiyyətli laboratoriyalar, CTF və təhsil araşdırmaları üçün müasir şəbəkə təhlükəsizliyi kəşfiyyat framework-ü.",
      product: "Məhsul",
      resources: "Resurslar",
      legal: "Hüquqi və Etika",
      languages: "Dil",
      copyright: "© 2026 CrackMapExec+. MIT Lisenziyası altında yayımlanır.",
    },
  },
  ru: {
    nav: {
      brand: "CrackMapExec+",
      features: "Возможности",
      ctfs: "CTF",
      wiki: "База знаний",
      faq: "FAQ",
      download: "Скачать",
      releases: "Релизы",
      github: "GitHub",
      security: "Безопасность",
      about: "О проекте",
    },
    hero: {
      title: "CrackMapExec+",
      subtitle: "Современный фреймворк разведки и аудита сетевой безопасности",
      tagline: "Разработан для авторизованных лабораторий, CTF-соревнований, TryHackMe, Hack The Box, академических исследований и учебных семинаров.",
      downloadBtn: "Скачать сейчас",
      exploreCtfsBtn: "Открыть Mini-CTF",
      supportedProtocols: "Поддерживаемые протоколы",
      terminalBadge: "СИМУЛЯТОР ТЕРМИНАЛА CME+",
      demoNote: "Все команды выполняются в изолированной браузерной песочнице. Сетевые пакеты во внешнюю сеть не передаются.",
    },
    features: {
      sectionTitle: "Создан для точности и надежности",
      sectionSubtitle: "Ознакомьтесь с архитектурными решениями для аудита Active Directory и сетевых протоколов.",
      nmapTitle: "Движок Nmap Intelligence",
      nmapDesc: "Парсинг стандартных отчетов -oN, автоматическое сопоставление протоколов, инвентаризация сервисов и предпросмотр плана выполнения.",
      transportTitle: "Универсальный TransportEngine",
      transportDesc: "Строгий 8-этапный автомат состояний, разделяющий TCP-доступность уровня L4 и протокольное взаимодействие уровня L7.",
      smbTitle: "Глубокая разведка SMB",
      smbDesc: "Извлечение параметров NTLMSSP TargetInfo AV_PAIR: имя хоста, домен, лес, номер сборки Windows NT и статус подписи SMB.",
      multiTargetTitle: "Гибкое управление целями",
      multiTargetDesc: "Поддержка одиночных IP, подсетей CIDR (/24, /29), диапазонов октетов (10.0.0.1-50), списков и файлов целей с комментариями.",
      protocolsTitle: "Поддержка ключевых протоколов",
      protocolsDesc: "Модульные драйверы для SMB, LDAP (RootDSE и SASL), WinRM (WS-Man WWW-Authenticate) и SSH (анализ баннеров RFC 4253).",
      diagnosticsTitle: "Диагностика Doctor (10 проверок)",
      diagnosticsDesc: "Комплексная проверка версии Python, целостности установки, переменной PATH, библиотек зависимостей и состояния Git.",
      bugTrackerTitle: "Автоматический трекер багов",
      bugTrackerDesc: "Локальный реестр отчетов Markdown с очисткой конфиденциальных данных и дедупликацией по цифровым отпечаткам.",
      videoCenterTitle: "Встроенный видеоцентр",
      videoCenterDesc: "Библиотека видеоруководств CLI с точным расчетом меток времени (&t=143s) и динамическими рекомендациями протоколов.",
    },
    ctf: {
      sectionTitle: "Интерактивная образовательная платформа Mini-CTF",
      sectionSubtitle: "Отрабатывайте навыки перечисления протоколов, анализа заголовков и разведки в безопасной песочнице.",
      dashboardTitle: "Задания CTF и Хранилище флагов",
      yourProgress: "Ваш прогресс",
      difficulty: "Сложность",
      points: "Очки",
      startChallenge: "Начать задание",
      terminalTitle: "Виртуальный терминал CrackMapExec+",
      availableCommands: "Доступные команды симулятора: help, target, scan, nmap, smb, ldap, winrm, ssh, inspect, history, clear",
      targetAssigned: "Назначенная цель",
      simulatedWarning: "СИМУЛИРОВАННАЯ ЦЕЛЬ: Этот адрес существует исключительно внутри песочницы CTF. Реальный сетевой трафик не генерируется.",
      flagPrompt: "Отправить найденный флаг",
      submitFlag: "Отправить флаг",
      flagAccepted: "✓ ФЛАГ ПРИНЯТ! Задание успешно завершено.",
      flagIncorrect: "✕ Неверный флаг. Продолжайте исследование виртуальной цели.",
      hintsTitle: "Пошаговые подсказки",
      useHint: "Открыть подсказку",
      hintPenalty: "штраф",
      completed: "Выполнено",
      locked: "Заблокировано",
      vaultTitle: "Хранилище флагов",
      noFlagsYet: "Флаги пока не найдены. Выберите задание выше, чтобы начать!",
      challengesCount: "Выполнено заданий",
      scoreLabel: "Общий счет",
      rankLabel: "Ранг оператора",
      completedBadge: "ВЫПОЛНЕНО",
      resetProgress: "Сбросить прогресс",
      hintUnlocked: "Подсказка открыта",
      unlockHintWarning: "Открытие этой подсказки снизит итоговый счет на:",
      cancel: "Отмена",
      confirm: "Открыть",
    },
    download: {
      title: "Загрузка и установка",
      subtitle: "Выберите способ установки для вашей системы. CrackMapExec+ поддерживает Linux, Kali Linux, macOS и Windows WSL.",
      pipxTab: "pipx (Рекомендуется)",
      debianTab: "Пакет Debian / Kali (.deb)",
      sourceTab: "Исходный код Git",
      wslTab: "Windows / WSL",
      ensurepathTip: "Если команда 'crackmapexec+' не найдена после установки, выполните 'pipx ensurepath' и перезапустите терминал.",
      reloadTip: "Всегда обновляйте сессию терминала после глобальной установки Python-утилит.",
      releaseInfo: "Официальный репозиторий GitHub: CodingM-eng/CrackMapExec-Plus",
      latestReleaseBadge: "Стабильная v0.1.0",
      quickInstallTitle: "Быстрая автоматическая установка",
      recommendedMethod: "Рекомендуется для изолированного использования без конфликтов зависимостей.",
      requirementsTitle: "Системные требования: Python 3.11+, Git и эмулятор терминала.",
    },
    wiki: {
      title: "Техническая документация и база знаний",
      subtitle: "Архитектурные спецификации, руководства по протоколам, справочник CLI и инструкции по решению проблем.",
      searchPlaceholder: "Поиск по статьям базы знаний...",
      categories: "Категории",
      readDoc: "Читать статью",
    },
    faq: {
      title: "Часто задаваемые вопросы",
      subtitle: "Ответы на вопросы о CrackMapExec+, политике использования, симуляторе CTF и безопасности.",
      stillQuestions: "Остались вопросы?",
      askGithub: "Задайте вопрос в обсуждениях на GitHub",
    },
    releases: {
      title: "Официальные релизы и журнал изменений",
      subtitle: "История версий, исправления ошибок, новые возможности и файлы с официального репозитория.",
      latestBadge: "Последний релиз",
      viewOnGithub: "Смотреть релиз на GitHub",
      publishedOn: "Дата публикации",
      changelog: "Журнал изменений",
      assets: "Файлы и сборки",
      noReleases: "Получение данных о релизах через GitHub API...",
    },
    about: {
      title: "О проекте CrackMapExec+",
      subtitle: "Независимый фреймворк с чистой архитектурой для образовательных целей и авторизованного аудита безопасности.",
      missionTitle: "Наша миссия",
      architectureTitle: "Модульная архитектура",
      ethicsTitle: "Этика и ответственность",
    },
    security: {
      title: "Политика безопасности и ответственного использования",
      subtitle: "Следование этическим нормам исследований, строгая авторизация целей и изоляция учебной песочницы.",
      authorizedTitle: "Авторизованная область тестирования",
      simulationTitle: "Гарантия изоляции песочницы CTF",
      reportingTitle: "Ответственное раскрытие уязвимостей",
    },
    footer: {
      tagline: "Современный фреймворк разведки сетевой безопасности для учебных лабораторий, CTF и исследований.",
      product: "Продукт",
      resources: "Ресурсы",
      legal: "Этика и право",
      languages: "Язык",
      copyright: "© 2026 CrackMapExec+. Распространяется под лицензией MIT.",
    },
  },
};
