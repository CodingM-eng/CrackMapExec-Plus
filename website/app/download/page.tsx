'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { DownloadSection } from "../../components/DownloadSection";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../../lib/storage";
import { Download, Terminal, CheckCircle2, ShieldCheck } from "lucide-react";

export default function DownloadPage() {
  const [lang, setLang] = useState<Language>("en");

  useEffect(() => {
    setLang(getStoredLanguage());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const t = translations[lang].download;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 w-full space-y-12">
        <DownloadSection lang={lang} />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2 font-mono">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Verification & Integrity Checks
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-4 rounded-xl bg-dark-900 border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold">1. Verify Diagnostic Health:</span>
              <pre className="p-2.5 rounded bg-dark-950 text-emerald-400">crackmapexec+ doctor</pre>
              <p className="text-slate-500 font-sans text-[11px]">
                Runs all 10 environment, PATH, and dependency integrity checks.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-dark-900 border border-slate-800 space-y-2">
              <span className="text-slate-400 font-bold">2. Check for Updates:</span>
              <pre className="p-2.5 rounded bg-dark-950 text-emerald-400">crackmapexec+ update --check</pre>
              <p className="text-slate-500 font-sans text-[11px]">
                Queries official GitHub Releases with zero system modifications.
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
