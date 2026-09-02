'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { releasesData } from "../../data/releases";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../../lib/storage";
import { Tag, Calendar, Download, ExternalLink, CheckCircle2 } from "lucide-react";

export default function ReleasesPage() {
  const [lang, setLang] = useState<Language>("en");

  useEffect(() => {
    setLang(getStoredLanguage());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const t = translations[lang].releases;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full space-y-10">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
            <Tag className="w-3.5 h-3.5" />
            <span>VERSION HISTORY & RELEASES</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            {t.title}
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl">
            {t.subtitle}
          </p>
        </div>

        <div className="space-y-8">
          {releasesData.map((rel) => (
            <div
              key={rel.version}
              className="bg-dark-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-extrabold text-white font-mono">
                      {rel.version}
                    </span>
                    {rel.isLatest && (
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-mono">
                        {t.latestBadge}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{t.publishedOn} {rel.date}</span>
                  </div>
                </div>

                <a
                  href={rel.githubUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold text-dark-950 bg-emerald-400 hover:bg-emerald-300 transition-colors"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  {t.viewOnGithub}
                </a>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
                  {t.changelog}
                </h3>
                <ul className="space-y-2 text-xs sm:text-sm text-slate-300">
                  {rel.highlights.map((h, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-800/80">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
                  {t.assets}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {rel.assets.map((asset, i) => (
                    <a
                      key={i}
                      href={asset.url}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-dark-950 border border-slate-800 hover:border-slate-700 text-xs font-mono text-slate-300 hover:text-white transition-colors"
                    >
                      <Download className="w-3.5 h-3.5 text-slate-500" />
                      {asset.name}
                    </a>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
