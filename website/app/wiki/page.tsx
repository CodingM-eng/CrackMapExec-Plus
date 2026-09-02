'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { wikiArticles } from "../../data/wiki-content";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../../lib/storage";
import { BookOpen, Search, ChevronRight, FileText, Terminal, Layers } from "lucide-react";

export default function WikiPage() {
  const [lang, setLang] = useState<Language>("en");
  const [activeSlug, setActiveSlug] = useState(wikiArticles[0].slug);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    setLang(getStoredLanguage());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const t = translations[lang].wiki;

  const filteredArticles = wikiArticles.filter(
    (a) =>
      a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const activeArticle = wikiArticles.find((a) => a.slug === activeSlug) || wikiArticles[0];

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-8">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold">
            <BookOpen className="w-3.5 h-3.5" />
            <span>TECHNICAL SPECIFICATIONS & WIKI</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            {t.title}
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-3xl">
            {t.subtitle}
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative max-w-xl">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t.searchPlaceholder}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-dark-900 border border-slate-800 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Wiki Layout: Sidebar + Article */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Sidebar */}
          <div className="lg:col-span-4 bg-dark-900 border border-slate-800 rounded-xl p-4 space-y-2 sticky top-24">
            <h3 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider px-2 py-1">
              {t.categories}
            </h3>
            <div className="space-y-1">
              {filteredArticles.map((article) => (
                <button
                  key={article.slug}
                  type="button"
                  onClick={() => setActiveSlug(article.slug)}
                  className={`w-full flex items-center justify-between p-2.5 rounded-lg text-left text-xs sm:text-sm font-medium transition-all ${
                    activeSlug === article.slug
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold"
                      : "text-slate-300 hover:bg-dark-800 hover:text-white"
                  }`}
                >
                  <span className="truncate">{article.title}</span>
                  <ChevronRight className="w-3.5 h-3.5 shrink-0 opacity-60" />
                </button>
              ))}
            </div>
          </div>

          {/* Main Article Content */}
          <div className="lg:col-span-8 bg-dark-900 border border-slate-800 rounded-xl p-6 sm:p-8 shadow-xl space-y-6">
            <div className="border-b border-slate-800 pb-4 space-y-2">
              <span className="text-xs font-mono px-2.5 py-0.5 rounded bg-dark-950 text-emerald-400 border border-slate-800">
                {activeArticle.category}
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                {activeArticle.title}
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                {activeArticle.summary}
              </p>
            </div>

            <div className="prose prose-invert max-w-none text-slate-300 font-sans text-xs sm:text-sm leading-relaxed space-y-4">
              <pre className="p-4 rounded-xl bg-dark-950 border border-slate-800 font-mono text-xs text-slate-200 overflow-x-auto whitespace-pre-wrap">
                {activeArticle.content}
              </pre>
            </div>
          </div>
        </div>
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
