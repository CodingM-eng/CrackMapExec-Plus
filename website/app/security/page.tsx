'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../../lib/storage";
import { ShieldAlert, CheckCircle2, Lock, AlertTriangle } from "lucide-react";

export default function SecurityPage() {
  const [lang, setLang] = useState<Language>("en");

  useEffect(() => {
    setLang(getStoredLanguage());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const t = translations[lang].security;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full space-y-10">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono font-bold">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>ETHICS & RESPONSIBLE USAGE POLICY</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            {t.title}
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl">
            {t.subtitle}
          </p>
        </div>

        <div className="space-y-6 text-xs sm:text-sm text-slate-300 leading-relaxed">
          <div className="p-6 rounded-2xl bg-dark-900 border border-slate-800 space-y-3 shadow-xl">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 font-mono">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              {t.authorizedTitle}
            </h2>
            <p>
              CrackMapExec+ is engineered, maintained, and distributed strictly for authorized security laboratories, educational seminars, academic research, CTF competitions, and computer systems where the operator possesses explicit written permission from the asset owner.
            </p>
            <p className="text-rose-400 font-semibold">
              Conducting network scanning, port probing, or credential evaluation against systems without prior written authorization is illegal.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-dark-900 border border-slate-800 space-y-3 shadow-xl">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 font-mono">
              <Lock className="w-5 h-5 text-cyan-400" />
              {t.simulationTitle}
            </h2>
            <p>
              The interactive Mini-CTF platform on this website operates inside a strictly isolated client-side and API sandbox. The simulated target IP addresses (e.g. 10.13.37.42) are fictitious endpoints. The terminal cannot execute native system shell commands, connect to LAN/public IPs, or access local filesystems.
            </p>
          </div>
        </div>
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
