import { Language } from "../lib/i18n";

export interface FaqItem {
  id: string;
  category: "general" | "usage" | "safety" | "ctf";
  question: Record<Language, string>;
  answer: Record<Language, string>;
}

export const faqItems: FaqItem[] = [
  {
    id: "what-is-cme-plus",
    category: "general",
    question: {
      en: "What is CrackMapExec+?",
      az: "CrackMapExec+ nədir?",
      ru: "Что такое CrackMapExec+?",
    },
    answer: {
      en: "CrackMapExec+ is a next-generation network security intelligence and enumeration framework engineered for authorized laboratories, CTFs (TryHackMe, Hack The Box), academic research, and educational seminars. It provides a modular, clean-room architecture in typed Python 3.11+.",
      az: "CrackMapExec+ səlahiyyətli laboratoriyalar, CTF yarışları (TryHackMe, Hack The Box), elmi araşdırmalar və tədris seminarları üçün yazılmış yeni nəsil şəbəkə təhlükəsizliyi kəşfiyyat framework-üdür.",
      ru: "CrackMapExec+ — это современный фреймворк разведки сетевой безопасности, разработанный для авторизованных лабораторий, CTF (TryHackMe, Hack The Box), исследований и учебных семинаров на базе Python 3.11+.",
    },
  },
  {
    id: "is-it-free-open-source",
    category: "general",
    question: {
      en: "Is CrackMapExec+ free and open source?",
      az: "CrackMapExec+ pulsuzdur və açıq mənbəlidirmi?",
      ru: "Является ли CrackMapExec+ бесплатным и с открытым исходным кодом?",
    },
    answer: {
      en: "Yes. CrackMapExec+ is 100% free and open source, distributed under the MIT License on GitHub: https://github.com/CodingM-eng/CrackMapExec-Plus.",
      az: "Bəli. CrackMapExec+ 100% pulsuz və açıq mənbəlidir, MIT lisenziyası altında GitHub-da paylaşılır: https://github.com/CodingM-eng/CrackMapExec-Plus.",
      ru: "Да. CrackMapExec+ на 100% бесплатен и имеет открытый исходный код под лицензией MIT на GitHub: https://github.com/CodingM-eng/CrackMapExec-Plus.",
    },
  },
  {
    id: "is-cme-plus-netexec-replacement",
    category: "general",
    question: {
      en: "Is CrackMapExec+ a replacement for NetExec or original CrackMapExec?",
      az: "CrackMapExec+ NetExec və ya ilkin CrackMapExec-in əvəzləyicisidirmi?",
      ru: "Является ли CrackMapExec+ заменой NetExec или оригинального CrackMapExec?",
    },
    answer: {
      en: "CrackMapExec+ is an independent, clean-room project inspired by the protocol-oriented ergonomics of historical tools, but built with a decoupled architecture, explicit connection state machines, native Nmap intelligence, and zero plaintext credential disk persistence. It does not claim to be NetExec or CrackMapExec.",
      az: "CrackMapExec+ tarixi alətlərdən ilhamlanan, lakin modul memarlıq, Nmap kəşfiyyatı və məxfilik tələbləri ilə sıfırdan yazılmış müstəqil bir layihədir. NetExec və ya CrackMapExec olduğunu iddia etmir.",
      ru: "CrackMapExec+ — это независимый проект, вдохновленный эргономикой классических утилит, но созданный с модульной архитектурой, автоматом состояний соединений, интеграцией с Nmap и защитой учетных данных. Он не заявляет себя как NetExec или CrackMapExec.",
    },
  },
  {
    id: "supported-os",
    category: "usage",
    question: {
      en: "What operating systems are supported?",
      az: "Hansı əməliyyat sistemləri dəstəklənir?",
      ru: "Какие операционные системы поддерживаются?",
    },
    answer: {
      en: "CrackMapExec+ runs natively on Linux (including Kali Linux, Ubuntu, Debian, Arch), macOS, and Windows via Windows Subsystem for Linux (WSL) or native Python virtual environments.",
      az: "CrackMapExec+ Linux (Kali Linux, Ubuntu, Debian, Arch), macOS və Windows (WSL və ya virtualenv) mühitlərində problemsiz işləyir.",
      ru: "CrackMapExec+ работает на Linux (включая Kali Linux, Ubuntu, Debian, Arch), macOS и Windows через подсистему WSL или виртуальные окружения Python.",
    },
  },
  {
    id: "safety-authorization",
    category: "safety",
    question: {
      en: "Can I use CrackMapExec+ against arbitrary public IP addresses?",
      az: "CrackMapExec+ proqramını istənilən ictimai IP ünvanlarına qarşı istifadə edə bilərəmmi?",
      ru: "Могу ли я использовать CrackMapExec+ против произвольных публичных IP-адресов?",
    },
    answer: {
      en: "No. Unauthorized security testing against systems without explicit written permission from the owner is illegal. CrackMapExec+ is strictly intended for authorized labs, CTFs, private research environments, and explicitly authorized testing.",
      az: "Xeyr. Sahibinin rəsmi yazılı icazəsi olmadan sistemlərin sınaqdan keçirilməsi qanunsuzdur. Alət yalnız səlahiyyətli laboratoriyalar, CTF-lər və şəxsi sınaq mühitləri üçündür.",
      ru: "Нет. Несанкционированное сканирование и аудит систем без письменного разрешения владельца незаконны. Утилита предназначена исключительно для авторизованных лабораторий, CTF и исследовательских стендов.",
    },
  },
  {
    id: "ctf-simulation-safety",
    category: "ctf",
    question: {
      en: "Does the website CTF platform generate real network traffic or scan real systems?",
      az: "Veb-saytın CTF platforması real şəbəkə trafiki yaradırmı və ya real sistemləri skan edirmi?",
      ru: "Генерирует ли платформа CTF на сайте реальный сетевой трафик и сканирует ли реальные системы?",
    },
    answer: {
      en: "No. The entire web CTF experience runs in a sandboxed, in-browser simulation environment. All IP addresses (such as 10.13.37.42) and protocol responses exist purely inside the virtual simulator. No external network sockets are opened.",
      az: "Xeyr. Bütün veb CTF tapşırıqları brauzer daxilində təcrid olunmuş simulyasiyada icra edilir. Bütün IP ünvanları və cavablar sırf virtual mühitdə mövcuddur.",
      ru: "Нет. Весь веб-CTF работает в полностью изолированной браузерной симуляции. Все IP-адреса и ответы служб существуют только внутри виртуального симулятора.",
    },
  },
  {
    id: "where-can-i-test",
    category: "usage",
    question: {
      en: "Where can I legitimately test CrackMapExec+?",
      az: "CrackMapExec+ proqramını qanuni olaraq harada sınaqdan keçirə bilərəm?",
      ru: "Где можно легально тестировать CrackMapExec+?",
    },
    answer: {
      en: "You can practice in dedicated cybersecurity platforms such as TryHackMe, Hack The Box, VulnHub, PortSwigger Web Security Academy, personal Active Directory home labs, and local virtual machines.",
      az: "TryHackMe, Hack The Box, VulnHub, PortSwigger Akademiyası kimi təhsil platformalarında, şəxsi Active Directory laboratoriyalarında və virtual maşınlarda təcrübə edə bilərsiniz.",
      ru: "Вы можете практиковаться на платформах TryHackMe, Hack The Box, VulnHub, PortSwigger Academy, в домашних лабораториях Active Directory и на локальных виртуальных машинах.",
    },
  },
];
