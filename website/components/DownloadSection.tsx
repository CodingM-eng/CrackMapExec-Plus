'use client';

import React, { useState } from "react";
import { Language, translations } from "../lib/i18n";
import { Terminal, Copy, Check, Info } from "lucide-react";

interface DownloadSectionProps {
  lang: Language;
}

export const DownloadSection: React.FC<DownloadSectionProps> = ({ lang }) => {
  const t = translations[lang].download;
  const [activeTab, setActiveTab] = useState<"pipx" | "debian" | "source" | "wsl">("pipx");
  const [copied, setCopied] = useState(false);

  const commands = {
    pipx: "pipx install git+https://github.com/CodingM-eng/CrackMapExec-Plus.git\npipx ensurepath",
    debian: "# Build & install native Debian package:\n./packaging/build_deb.sh\nsudo apt install ../crackmapexec-plus_0.1.0-1_all.deb",
    source: "git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git\ncd CrackMapExec-Plus\n./install.sh",
    wsl: "# Inside WSL2 Ubuntu/Debian:\npipx install git+https://github.com/CodingM-eng/CrackMapExec-Plus.git\npipx ensurepath",
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <section id="download" className="w-full py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-10">
      <div className="text-center space-y-3 max-w-2xl mx-auto">
        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          {t.latestReleaseBadge}
        </span>
        <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          {t.title}
        </h2>
        <p className="text-sm text-slate-400">
          {t.subtitle}
        </p>
      </div>

      <div className="bg-dark-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <div className="flex flex-wrap border-b border-slate-800 bg-dark-950 px-4 pt-3 gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("pipx")}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-all ${
              activeTab === "pipx"
                ? "bg-dark-900 text-emerald-400 border-t border-x border-slate-800 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {t.pipxTab}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("debian")}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-all ${
              activeTab === "debian"
                ? "bg-dark-900 text-emerald-400 border-t border-x border-slate-800 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {t.debianTab}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("source")}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-all ${
              activeTab === "source"
                ? "bg-dark-900 text-emerald-400 border-t border-x border-slate-800 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {t.sourceTab}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("wsl")}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition-all ${
              activeTab === "wsl"
                ? "bg-dark-900 text-emerald-400 border-t border-x border-slate-800 font-bold"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {t.wslTab}
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Terminal Installation Command:</span>
            <button
              type="button"
              onClick={() => handleCopy(commands[activeTab])}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-dark-800 hover:bg-dark-700 text-xs text-slate-300 font-medium border border-slate-700 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>

          <pre className="p-4 rounded-xl bg-dark-950 border border-slate-800 font-mono text-xs sm:text-sm text-emerald-400 overflow-x-auto whitespace-pre-wrap leading-relaxed">
            {commands[activeTab]}
          </pre>

          <div className="flex items-start gap-2.5 p-3 rounded-lg bg-dark-950/80 border border-slate-800 text-xs text-slate-400">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <p>{t.ensurepathTip}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
