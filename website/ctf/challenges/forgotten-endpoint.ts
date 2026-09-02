import { Challenge } from "./types";

export const forgottenEndpointChallenge: Challenge = {
  id: "forgotten-endpoint",
  title: {
    en: "CTF 01 — The Forgotten Endpoint",
    az: "CTF 01 — Unudulmuş Endpoint",
    ru: "CTF 01 — Забытый эндпоинт",
  },
  difficulty: "Easy",
  points: 100,
  theme: {
    en: "Web Enumeration & Shadow API",
    az: "Veb Sayma və Gizli API",
    ru: "Веб-разведка и скрытые API",
  },
  description: {
    en: "A legacy internal corporate server was recently migrated to the testing lab subnet. Intelligence indicates that an unindexed debugging endpoint was left active in the web service configuration.",
    az: "Köhnə daxili korporativ server bu yaxınlarda sınaq laboratoriyası alt şəbəkəsinə köçürülmüşdür. Məlumata görə, veb xidmətində indekslənməmiş sazlama endpoint-i aktiv qalmışdır.",
    ru: "Устаревший внутренний корпоративный сервер был перемещен в лабораторную подсеть. По данным разведки, в веб-сервисе остался активным неиндексированный отладочный эндпоинт.",
  },
  objective: {
    en: "Use Nmap and SMB reconnaissance to identify the target architecture, locate the hidden endpoint, inspect its output, and retrieve the flag.",
    az: "Hədəfin arxitekturasını müəyyənləşdirmək, gizli endpoint-i tapmaq və bayrağı əldə etmək üçün Nmap və SMB kəşfiyyatından istifadə edin.",
    ru: "Используйте Nmap и SMB для определения архитектуры цели, найдите скрытый эндпоинт, изучите его данные и получите флаг.",
  },
  targetIp: "10.13.37.42",
  targetHostname: "PORTAL-SRV01.corp.internal",
  services: [
    { port: 80, protocol: "tcp", service: "http", version: "Apache httpd 2.4.52 ((Ubuntu) OpenSSL/3.0.2)", state: "open" },
    { port: 445, protocol: "tcp", service: "microsoft-ds", version: "Samba smbd 4.15.13-Ubuntu", state: "open" },
  ],
  hints: [
    {
      index: 1,
      penalty: 10,
      text: {
        en: "Start with reconnaissance: run 'nmap 10.13.37.42' to discover all open listening ports and services.",
        az: "Kəşfiyyatdan başlayın: açıq portları və xidmətləri tapmaq üçün 'nmap 10.13.37.42' icra edin.",
        ru: "Начните с разведки: выполните 'nmap 10.13.37.42' для обнаружения всех открытых портов и служб.",
      },
    },
    {
      index: 2,
      penalty: 20,
      text: {
        en: "Check SMB shares and metadata using 'smb 10.13.37.42'. Look for non-standard configuration shares.",
        az: "'smb 10.13.37.42' komandası ilə SMB paylaşımlarını yoxlayın. Qeyri-standart konfiqurasiya qovluğuna baxın.",
        ru: "Проверьте общие ресурсы SMB с помощью 'smb 10.13.37.42'. Обратите внимание на нестандартные ресурсы конфигурации.",
      },
    },
    {
      index: 3,
      penalty: 30,
      text: {
        en: "Inspect the web endpoint discovered in the SMB configuration notes using 'inspect 80' or 'inspect /api/v1/internal-status'.",
        az: "SMB qeydlərində tapılan veb ünvanını 'inspect 80' və ya 'inspect /api/v1/internal-status' komandası ilə yoxlayın.",
        ru: "Изучите веб-эндпоинт, найденный в заметках конфигурации SMB, выполнив 'inspect 80' или 'inspect /api/v1/internal-status'.",
      },
    },
  ],
  canonicalFlag: "cme+{endpoint_discovered_in_shadow_api}",
};
