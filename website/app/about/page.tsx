'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../../lib/storage";
import { Terminal, Shield, Layers, Users, BookOpen } from "lucide-react";

export default function AboutPage() {
  const [lang, setLang] = useState<Language>("en");

  useEffect(() => {
    setLang(getStoredLanguage());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const t = translations[lang].about;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full space-y-10">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
            <Terminal className="w-3.5 h-3.5" />
            <span>PROJECT BACKGROUND & ARCHITECTURE</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            {t.title}
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl">
            {t.subtitle}
          </p>
        </div>

        <div className="space-y-8 text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
          <div className="p-6 rounded-2xl bg-dark-900 border border-slate-800 space-y-3 shadow-xl">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 font-mono">
              <Shield className="w-5 h-5 text-emerald-400" />
              {t.missionTitle}
            </h2>
            <p>
              CrackMapExec+ was created to provide a modern, reliable, and decoupled security assessment framework tailored for authorized educational testing, CTF competitions (such as TryHackMe and Hack The Box), academic research, and defensive evaluation.
            </p>
            <p>
              Unlike legacy architectures that mix network transport, authentication routines, and database writes in monolithic objects, CrackMapExec+ enforces clean layer separation.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-dark-900 border border-slate-800 space-y-3 shadow-xl">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 font-mono">
              <Layers className="w-5 h-5 text-cyan-400" />
              {t.architectureTitle}
            </h2>
            <p>
              The core framework consists of strictly decoupled components:
            </p>
            <ul className="list-disc pl-5 space-y-1 text-slate-400">
              <li><strong>Nmap Intelligence Engine</strong>: First-class ingestion of standard -oN text reports with protocol resolution.</li>
              <li><strong>Universal TransportEngine</strong>: 8-stage connection state machine distinguishing L4 TCP states from L7 protocol states.</li>
              <li><strong>Memory-Only Credentials</strong>: Zero plaintext password persistence on disk, ensuring student safety on shared systems.</li>
              <li><strong>Doctor Diagnostics</strong>: 10-point health verification preventing silent dependency or configuration failures.</li>
            </ul>
          </div>
        </div>
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
