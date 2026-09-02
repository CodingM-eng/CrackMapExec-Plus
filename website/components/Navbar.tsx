'use client';

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Language, translations } from "../lib/i18n";
import { Terminal, Shield, Menu, X, ChevronDown, Download, Award } from "lucide-react";

interface NavbarProps {
  lang: Language;
  onLanguageChange: (lang: Language) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ lang, onLanguageChange }) => {
  const t = translations[lang].nav;
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);

  const navLinks = [
    { href: "/#features", label: t.features },
    { href: "/ctf", label: t.ctfs, highlight: true },
    { href: "/wiki", label: t.wiki },
    { href: "/faq", label: t.faq },
    { href: "/download", label: t.download },
    { href: "/releases", label: t.releases },
    { href: "https://github.com/CodingM-eng/CrackMapExec-Plus", label: t.github, external: true },
  ];

  const languages: { code: Language; label: string; flag: string }[] = [
    { code: "en", label: "English", flag: "🇬🇧" },
    { code: "az", label: "Azərbaycan", flag: "🇦🇿" },
    { code: "ru", label: "Русский", flag: "🇷🇺" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-dark-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 group-hover:bg-emerald-500/20 group-hover:border-emerald-400 transition-all">
            <Terminal className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base text-white tracking-tight flex items-center gap-1 font-mono">
              CrackMapExec<span className="text-emerald-400 font-extrabold">+</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono tracking-wider -mt-0.5">
              LAB EDITION
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-1.5 lg:gap-3 text-sm">
          {navLinks.map((link) => (
            link.external ? (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-dark-900 transition-colors"
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 font-medium ${
                  pathname === link.href
                    ? "text-emerald-400 bg-emerald-500/10 border border-emerald-500/20"
                    : link.highlight
                    ? "text-amber-300 hover:text-amber-200 bg-amber-500/10 border border-amber-500/20 hover:bg-amber-500/20"
                    : "text-slate-300 hover:text-white hover:bg-dark-900"
                }`}
              >
                {link.highlight && <Award className="w-3.5 h-3.5 text-amber-400" />}
                {link.label}
              </Link>
            )
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <div className="relative">
            <button
              type="button"
              onClick={() => setLangMenuOpen(!langMenuOpen)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-dark-900 border border-slate-700 text-xs font-semibold text-slate-200 hover:border-slate-600 transition-colors"
            >
              <span>{languages.find((l) => l.code === lang)?.flag}</span>
              <span className="uppercase font-mono">{lang}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {langMenuOpen && (
              <div className="absolute right-0 mt-2 w-36 rounded-xl bg-dark-900 border border-slate-800 shadow-2xl py-1 z-50 animate-fadeIn">
                {languages.map((l) => (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => {
                      onLanguageChange(l.code);
                      setLangMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-2 px-3 py-2 text-xs text-left hover:bg-dark-800 transition-colors ${
                      lang === l.code ? "text-emerald-400 font-bold bg-emerald-500/5" : "text-slate-300"
                    }`}
                  >
                    <span>{l.flag}</span>
                    <span>{l.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <Link
            href="/download"
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold text-dark-950 bg-emerald-400 hover:bg-emerald-300 transition-all shadow-lg shadow-emerald-500/20"
          >
            <Download className="w-3.5 h-3.5" />
            {t.download}
          </Link>
        </div>

        <div className="flex md:hidden items-center gap-2">
          <button
            type="button"
            onClick={() => onLanguageChange(lang === "en" ? "az" : lang === "az" ? "ru" : "en")}
            className="px-2 py-1 rounded bg-dark-900 border border-slate-700 text-xs font-mono font-bold text-slate-300"
          >
            {languages.find((l) => l.code === lang)?.flag} {lang.toUpperCase()}
          </button>
          <button
            type="button"
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-dark-900"
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-b border-slate-800 bg-dark-950 px-4 pt-2 pb-6 space-y-2 animate-fadeIn">
          {navLinks.map((link) => (
            link.external ? (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noreferrer"
                onClick={() => setMobileOpen(false)}
                className="block px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-dark-900 font-medium text-sm"
              >
                {link.label}
              </a>
            ) : (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className={`block px-3 py-2.5 rounded-lg font-medium text-sm ${
                  pathname === link.href
                    ? "text-emerald-400 bg-emerald-500/10 font-bold"
                    : "text-slate-300 hover:text-white hover:bg-dark-900"
                }`}
              >
                {link.label}
              </Link>
            )
          ))}
          <div className="pt-4">
            <Link
              href="/download"
              onClick={() => setMobileOpen(false)}
              className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-bold text-dark-950 bg-emerald-400"
            >
              <Download className="w-4 h-4" />
              {t.download}
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
