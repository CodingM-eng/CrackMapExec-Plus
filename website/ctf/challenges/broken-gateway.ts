import { Challenge } from "./types";

export const brokenGatewayChallenge: Challenge = {
  id: "broken-gateway",
  title: {
    en: "CTF 03 — The Broken Gateway",
    az: "CTF 03 — Sınmış Şlüz",
    ru: "CTF 03 — Сломанный шлюз",
  },
  difficulty: "Hard",
  points: 300,
  theme: {
    en: "Active Directory Multi-Protocol Recon",
    az: "Active Directory Çox-Protokollu Kəşfiyyat",
    ru: "Многопротокольная разведка Active Directory",
  },
  description: {
    en: "An Active Directory Domain Controller and network gateway operates with misconfigured anonymous LDAP and SMB permissions. A service account backup configuration is exposed in the domain SYSVOL/RouterBackup shares.",
    az: "Active Directory Domen Nəzarətçisi və şəbəkə şlüzü səhv konfiqurasiya edilmiş anonim LDAP və SMB icazələri ilə işləyir. Xidməti hesabın ehtiyat nüsxəsi domain paylaşımlarında açıq qalmışdır.",
    ru: "Контроллер домена Active Directory и сетевой шлюз работают с некорректными анонимными правами доступа LDAP и SMB. Резервная копия конфигурации службы осталась в ресурсах домена.",
  },
  objective: {
    en: "Perform an LDAP RootDSE probe, discover the Active Directory naming context and service accounts, interrogate the SMB backup share, and chain the findings to uncover the final flag.",
    az: "LDAP RootDSE sorğusu aparın, Active Directory domen adını və xidməti hesabları tapın, SMB ehtiyat nüsxəsini araşdırın və yekun bayrağı tapın.",
    ru: "Выполните опрос LDAP RootDSE, найдите контекст именования Active Directory и служебные учетные записи, исследуйте резервные копии SMB и найдите флаг.",
  },
  targetIp: "10.13.37.100",
  targetHostname: "GATEWAY-DC01.sec.lab",
  services: [
    { port: 22, protocol: "tcp", service: "ssh", version: "OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (protocol 2.0)", state: "open" },
    { port: 389, protocol: "tcp", service: "ldap", version: "Microsoft Windows Active Directory LDAP (Domain: sec.lab0., Site: Default-First-Site-Name)", state: "open" },
    { port: 445, protocol: "tcp", service: "microsoft-ds", version: "Windows Server 2022 Datacenter 20348 microsoft-ds", state: "open" },
  ],
  hints: [
    {
      index: 1,
      penalty: 30,
      text: {
        en: "Run 'nmap 10.13.37.100' to identify all active Active Directory and management protocols.",
        az: "Bütün aktiv Active Directory və idarəetmə protokollarını müəyyən etmək üçün 'nmap 10.13.37.100' icra edin.",
        ru: "Выполните 'nmap 10.13.37.100', чтобы определить все активные протоколы Active Directory и управления.",
      },
    },
    {
      index: 2,
      penalty: 60,
      text: {
        en: "Execute 'ldap 10.13.37.100' to query the RootDSE and extract the naming contexts and service accounts.",
        az: "RootDSE sorğusu göndərmək və domen adını, xidməti hesabları əldə etmək üçün 'ldap 10.13.37.100' icra edin.",
        ru: "Выполните 'ldap 10.13.37.100' для запроса RootDSE и извлечения контекстов именования и сервисных аккаунтов.",
      },
    },
    {
      index: 3,
      penalty: 90,
      text: {
        en: "Run 'smb 10.13.37.100' and 'inspect RouterBackup$' or 'inspect 445' to read the router recovery configuration file.",
        az: "Router bərpa konfiqurasiya faylını oxumaq üçün 'smb 10.13.37.100' və 'inspect RouterBackup$' istifadə edin.",
        ru: "Используйте 'smb 10.13.37.100' и 'inspect RouterBackup$' или 'inspect 445', чтобы прочитать файл конфигурации восстановления маршрутизатора.",
      },
    },
  ],
  canonicalFlag: "cme+{broken_gateway_full_chain_recon}",
};
