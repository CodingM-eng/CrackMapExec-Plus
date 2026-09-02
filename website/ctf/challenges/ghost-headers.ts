import { Challenge } from "./types";

export const ghostHeadersChallenge: Challenge = {
  id: "ghost-headers",
  title: {
    en: "CTF 02 — Ghost in the Headers",
    az: "CTF 02 — Başlıqlardakı Ruh",
    ru: "CTF 02 — Призрак в заголовках",
  },
  difficulty: "Medium",
  points: 200,
  theme: {
    en: "HTTP Metadata & Header Analysis",
    az: "HTTP Meta-məlumat və Başlıq Analizi",
    ru: "Метаданные HTTP и анализ заголовков",
  },
  description: {
    en: "A management workstation in the staging environment communicates with backend orchestrators. Proprietary diagnostic telemetry and staging tokens were accidentally leaked inside server response headers.",
    az: "Sınaq mühitindəki idarəetmə stansiyası arxa fon orkestratorları ilə əlaqə saxlayır. Server cavab başlıqlarında xüsusi diaqnostik telemetriya və tokenlər sızmışdır.",
    ru: "Рабочая станция управления в тестовой среде взаимодействует с оркестраторами. В заголовках ответов сервера были случайно раскрыты отладочные метаданные и токены.",
  },
  objective: {
    en: "Enumerate WinRM and HTTP services, perform deep response header analysis, extract the custom debug headers, and recover the flag.",
    az: "WinRM və HTTP xidmətlərini sayın, dərin başlıq analizi aparın, xüsusi sazlama başlıqlarını çıxarın və bayrağı bərpa edin.",
    ru: "Выполните перечисление служб WinRM и HTTP, проведите глубокий анализ заголовков ответов, извлеките отладочные параметры и найдите флаг.",
  },
  targetIp: "10.13.37.77",
  targetHostname: "MGMT-NODE02.lab.internal",
  services: [
    { port: 80, protocol: "tcp", service: "http", version: "Microsoft-IIS/10.0", state: "open" },
    { port: 5985, protocol: "tcp", service: "wsman", version: "Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)", state: "open" },
  ],
  hints: [
    {
      index: 1,
      penalty: 20,
      text: {
        en: "Run 'nmap 10.13.37.77' to scan for remote management and web ports.",
        az: "Uzaqdan idarəetmə və veb portlarını skan etmək üçün 'nmap 10.13.37.77' icra edin.",
        ru: "Выполните 'nmap 10.13.37.77' для сканирования портов управления и веб-сервисов.",
      },
    },
    {
      index: 2,
      penalty: 40,
      text: {
        en: "Probe WinRM using 'winrm 10.13.37.77' and analyze the WWW-Authenticate challenge mechanisms.",
        az: "'winrm 10.13.37.77' ilə WinRM xidmətini yoxlayın və WWW-Authenticate mexanizmlərini təhlil edin.",
        ru: "Проверьте WinRM командой 'winrm 10.13.37.77' и проанализируйте параметры WWW-Authenticate.",
      },
    },
    {
      index: 3,
      penalty: 60,
      text: {
        en: "Use 'inspect 5985' or 'inspect headers' to view full HTTP response headers including the custom X-Debug headers.",
        az: "Xüsusi X-Debug başlıqları da daxil olmaqla bütün başlıqları görmək üçün 'inspect 5985' və ya 'inspect headers' istifadə edin.",
        ru: "Используйте 'inspect 5985' или 'inspect headers', чтобы увидеть полные заголовки ответа, включая нестандартные X-Debug заголовки.",
      },
    },
  ],
  canonicalFlag: "cme+{ghost_metadata_leaked_in_headers}",
};
