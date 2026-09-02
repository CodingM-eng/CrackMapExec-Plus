'use client';

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Navbar } from "../components/Navbar";
import { Footer } from "../components/Footer";
import { HeroTerminal } from "../components/HeroTerminal";
import { FeatureGrid } from "../components/FeatureGrid";
import { DownloadSection } from "../components/DownloadSection";
import { Language, translations } from "../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../lib/storage";
import {
  Download,
  Award,
  Terminal,
  Shield,
  Layers,
  Sparkles,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

export default function LandingPage() {
  const [lang, setLang] = useState<Language>("en");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setLang(getStoredLanguage());
    setMounted(true);
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const t = translations[lang];

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100 overflow-x-hidden">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 flex flex-col">
        {/* HERO SECTION */}
        <section className="relative pt-16 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full flex flex-col items-center text-center space-y-8">
          {/* Subtle Ambient Glow */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-emerald-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />

          {/* Tagline Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold tracking-wide animate-fadeIn shadow-lg shadow-emerald-950/20">
            <Sparkles className="w-3.5 h-3.5" />
            <span>CRACKMAPEXEC+ • MODERN LAB & CTF INTELLIGENCE</span>
          </div>

          {/* Title & Subtitle */}
          <div className="space-y-4 max-w-4xl">
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight font-sans">
              Modern Network Security{" "}
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Intelligence
              </span>
            </h1>
            <p className="text-base sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed font-normal">
              {t.hero.tagline}
            </p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              href="/download"
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl text-sm font-bold text-dark-950 bg-emerald-400 hover:bg-emerald-300 transition-all shadow-xl shadow-emerald-500/25 cursor-pointer transform hover:-translate-y-0.5"
            >
              <Download className="w-4 h-4" />
              {t.hero.downloadBtn}
            </Link>

            <Link
              href="/ctf"
              className="flex items-center gap-2 px-6 py-3.5 rounded-xl text-sm font-bold text-white bg-dark-900 hover:bg-dark-800 border border-slate-700 hover:border-slate-600 transition-all shadow-xl shadow-dark-950/40 cursor-pointer transform hover:-translate-y-0.5"
            >
              <Award className="w-4 h-4 text-amber-400" />
              {t.hero.exploreCtfsBtn}
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </Link>
          </div>

          {/* Protocol Badges */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-3 text-xs font-mono text-slate-400">
            <span className="text-slate-500 font-semibold">{t.hero.supportedProtocols}:</span>
            <span className="px-2.5 py-1 rounded bg-dark-900 border border-slate-800 text-slate-200">SMB 3.1.1</span>
            <span className="px-2.5 py-1 rounded bg-dark-900 border border-slate-800 text-slate-200">LDAP / LDAPS</span>
            <span className="px-2.5 py-1 rounded bg-dark-900 border border-slate-800 text-slate-200">WinRM WS-Man</span>
            <span className="px-2.5 py-1 rounded bg-dark-900 border border-slate-800 text-slate-200">SSH RFC 4253</span>
            <span className="px-2.5 py-1 rounded bg-dark-900 border border-emerald-500/40 text-emerald-400 font-bold">Nmap -oN Engine</span>
          </div>

          {/* Animated Hero Terminal Simulation */}
          <div className="w-full pt-8 flex flex-col items-center space-y-3">
            <HeroTerminal />
            <p className="text-[11px] font-mono text-slate-500 max-w-xl">
              {t.hero.demoNote}
            </p>
          </div>
        </section>

        {/* CTF SPOTLIGHT BANNER */}
        <section className="w-full py-12 bg-dark-900/60 border-y border-slate-800/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-2 text-center md:text-left">
              <div className="inline-flex items-center gap-1.5 text-xs font-mono font-bold text-amber-400 uppercase tracking-wider">
                <Award className="w-4 h-4" />
                <span>Hands-on Learning Track</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                3 Original Interactive Mini-CTF Challenges
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 max-w-2xl">
                Test your reconnaissance, SMB inspection, and HTTP header analysis skills in our virtual browser sandbox.
              </p>
            </div>

            <Link
              href="/ctf"
              className="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-dark-950 bg-amber-400 hover:bg-amber-300 transition-all shadow-lg shadow-amber-500/20 shrink-0"
            >
              Start Challenges
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </section>

        {/* ARCHITECTURAL FEATURE GRID */}
        <FeatureGrid lang={lang} />

        {/* QUICK DOWNLOAD SECTION */}
        <DownloadSection lang={lang} />
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
