'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { CtfProgress } from "../../ctf/components/CtfProgress";
import { allChallenges } from "../../ctf/engine/challenges";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage, getStoredProgress, saveProgress } from "../../lib/storage";
import { Award, Terminal, Shield, AlertTriangle } from "lucide-react";

export default function CtfDashboardPage() {
  const [lang, setLang] = useState<Language>("en");
  const [progress, setProgress] = useState({
    completedChallenges: [] as string[],
    score: 0,
    flags: {} as Record<string, string>,
    hintsUsed: {} as Record<string, number[]>,
    sessionId: "",
  });

  useEffect(() => {
    setLang(getStoredLanguage());
    setProgress(getStoredProgress());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const handleResetProgress = () => {
    if (window.confirm("Are you sure you want to reset all CTF progress and discovered flags?")) {
      const reset = {
        completedChallenges: [],
        score: 0,
        flags: {},
        hintsUsed: {},
        sessionId: "sess_" + Math.random().toString(36).substring(2, 9),
      };
      saveProgress(reset);
      setProgress(reset);
    }
  };

  const t = translations[lang].ctf;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full space-y-10">
        {/* Title Header */}
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold">
            <Award className="w-3.5 h-3.5" />
            <span>CRACKMAPEXEC+ EDUCATIONAL CTF TRACK</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            {t.sectionTitle}
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-3xl leading-relaxed">
            {t.sectionSubtitle}
          </p>
        </div>

        {/* Sandbox Notice Banner */}
        <div className="flex items-start gap-3 p-4 rounded-xl bg-dark-900 border border-amber-500/20 text-xs sm:text-sm text-slate-300">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-300">Isolated Virtual Sandbox:</span>
            <p className="text-slate-400 text-xs leading-relaxed">
              All assigned target IP addresses (e.g. 10.13.37.42) are virtual simulation endpoints within this browser tab. No real network scans, port attacks, or packet injections are executed.
            </p>
          </div>
        </div>

        {/* Progress & Challenge Selector */}
        <CtfProgress
          challenges={allChallenges}
          completedIds={progress.completedChallenges}
          score={progress.score}
          flags={progress.flags}
          lang={lang}
          onReset={handleResetProgress}
        />
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
