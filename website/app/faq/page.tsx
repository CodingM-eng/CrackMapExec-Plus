'use client';

import React, { useState, useEffect } from "react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { faqItems } from "../../data/faq-content";
import { Language, translations } from "../../lib/i18n";
import { getStoredLanguage, setStoredLanguage } from "../../lib/storage";
import { HelpCircle, ChevronDown, Shield, MessageCircle } from "lucide-react";

export default function FaqPage() {
  const [lang, setLang] = useState<Language>("en");
  const [openIds, setOpenIds] = useState<string[]>([faqItems[0].id, faqItems[4].id]);

  useEffect(() => {
    setLang(getStoredLanguage());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  const toggleItem = (id: string) => {
    setOpenIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const t = translations[lang].faq;

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full space-y-8">
        <div className="space-y-3 text-center sm:text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>KNOWLEDGE & FREQUENTLY ASKED QUESTIONS</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
            {t.title}
          </h1>
          <p className="text-sm sm:text-base text-slate-400">
            {t.subtitle}
          </p>
        </div>

        <div className="space-y-4">
          {faqItems.map((item) => {
            const isOpen = openIds.includes(item.id);
            return (
              <div
                key={item.id}
                className="bg-dark-900 border border-slate-800 rounded-xl overflow-hidden transition-all duration-200 shadow-lg"
              >
                <button
                  type="button"
                  onClick={() => toggleItem(item.id)}
                  className="w-full flex items-center justify-between p-5 text-left text-sm sm:text-base font-semibold text-slate-200 hover:text-white transition-colors"
                >
                  <span className="flex items-center gap-2.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    {item.question[lang]}
                  </span>
                  <ChevronDown
                    className={`w-4 h-4 text-slate-400 transition-transform duration-200 shrink-0 ml-2 ${
                      isOpen ? "rotate-180 text-emerald-400" : ""
                    }`}
                  />
                </button>

                {isOpen && (
                  <div className="px-5 pb-5 pt-1 text-xs sm:text-sm text-slate-400 leading-relaxed border-t border-slate-800/60 bg-dark-950/40">
                    <p>{item.answer[lang]}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* GitHub Discussions CTA */}
        <div className="p-6 rounded-2xl bg-dark-900 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">{t.stillQuestions}</h3>
            <p className="text-xs text-slate-400">
              Check our active community discussions or file a suggestion on GitHub.
            </p>
          </div>
          <a
            href="https://github.com/CodingM-eng/CrackMapExec-Plus/discussions"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold text-dark-950 bg-emerald-400 hover:bg-emerald-300 transition-colors shrink-0"
          >
            <MessageCircle className="w-4 h-4" />
            {t.askGithub}
          </a>
        </div>
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
