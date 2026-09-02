'use client';

import React from "react";
import Link from "next/link";
import { Language, translations } from "../lib/i18n";
import { Terminal, Shield, BookOpen, Download, HelpCircle } from "lucide-react";


interface FooterProps {
  lang: Language;
  onLanguageChange: (lang: Language) => void;
}

export const Footer: React.FC<FooterProps> = ({ lang, onLanguageChange }) => {
  const t = translations[lang].footer;

  return (
    <footer className="w-full border-t border-slate-800/80 bg-dark-950 text-slate-400 text-xs py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <Link href="/" className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                <Terminal className="w-4 h-4" />
              </div>
              <span className="font-bold text-sm text-white font-mono">CrackMapExec+</span>
            </Link>
            <p className="text-slate-500 leading-relaxed">
              {t.tagline}
            </p>
          </div>

          <div className="space-y-3">
            <h4 className="font-semibold text-slate-200 text-xs uppercase tracking-wider font-mono">
              {t.product}
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/#features" className="hover:text-emerald-400 transition-colors">
                  Features Overview
                </Link>
              </li>
              <li>
                <Link href="/ctf" className="hover:text-emerald-400 transition-colors">
                  Interactive Mini-CTFs
                </Link>
              </li>
              <li>
                <Link href="/download" className="hover:text-emerald-400 transition-colors">
                  Download & Setup
                </Link>
              </li>
              <li>
                <Link href="/releases" className="hover:text-emerald-400 transition-colors">
                  Releases & Changelog
                </Link>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="font-semibold text-slate-200 text-xs uppercase tracking-wider font-mono">
              {t.resources}
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/wiki" className="hover:text-emerald-400 transition-colors">
                  Technical Wiki
                </Link>
              </li>
              <li>
                <Link href="/faq" className="hover:text-emerald-400 transition-colors">
                  Frequently Asked Questions
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/CodingM-eng/CrackMapExec-Plus"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-emerald-400 transition-colors"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <Link href="/about" className="hover:text-emerald-400 transition-colors">
                  About the Project
                </Link>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="font-semibold text-slate-200 text-xs uppercase tracking-wider font-mono">
              {t.legal}
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/security" className="hover:text-emerald-400 transition-colors">
                  Responsible Use Policy
                </Link>
              </li>
              <li>
                <span className="text-slate-500">MIT Open Source License</span>
              </li>
            </ul>

            <div className="pt-2 flex items-center gap-2">
              <span className="text-slate-500 text-[11px]">{t.languages}:</span>
              <button
                type="button"
                onClick={() => onLanguageChange("en")}
                className={`px-2 py-0.5 rounded text-[11px] font-mono ${
                  lang === "en" ? "bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => onLanguageChange("az")}
                className={`px-2 py-0.5 rounded text-[11px] font-mono ${
                  lang === "az" ? "bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                AZ
              </button>
              <button
                type="button"
                onClick={() => onLanguageChange("ru")}
                className={`px-2 py-0.5 rounded text-[11px] font-mono ${
                  lang === "ru" ? "bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                RU
              </button>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-900 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-slate-500 text-[11px]">
          <div>{t.copyright}</div>
          <div className="flex items-center gap-4">
            <span className="text-slate-600">Official Home: CodingM-eng/CrackMapExec-Plus</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
