'use client';

import React from "react";
import { Challenge } from "../challenges/types";
import { Language, translations } from "../../lib/i18n";
import { Shield, Target, Award, AlertCircle, HelpCircle } from "lucide-react";

interface CtfHeaderProps {
  challenge: Challenge;
  lang: Language;
  onOpenHints: () => void;
  isCompleted: boolean;
}

export const CtfHeader: React.FC<CtfHeaderProps> = ({
  challenge,
  lang,
  onOpenHints,
  isCompleted,
}) => {
  const t = translations[lang].ctf;

  const difficultyColors = {
    Easy: "border-emerald-500/40 text-emerald-400 bg-emerald-500/10",
    Medium: "border-amber-500/40 text-amber-400 bg-amber-500/10",
    Hard: "border-rose-500/40 text-rose-400 bg-rose-500/10",
  };

  return (
    <div className="w-full bg-dark-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              {challenge.title[lang]}
            </h1>
            {isCompleted && (
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">
                {t.completedBadge}
              </span>
            )}
          </div>
          <p className="text-sm text-slate-400 flex items-center gap-2">
            <span className="text-slate-500">Theme:</span>
            <span className="text-slate-300 font-medium">{challenge.theme[lang]}</span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold border ${difficultyColors[challenge.difficulty]}`}
          >
            {challenge.difficulty}
          </span>
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border border-cyan-500/40 text-cyan-400 bg-cyan-500/10">
            <Award className="w-3.5 h-3.5" />
            {challenge.points} {t.points}
          </span>
          <button
            type="button"
            onClick={onOpenHints}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border border-amber-500/40 text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 transition-colors"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            {t.hintsTitle}
          </button>
        </div>
      </div>

      {/* Target & Sandbox Badge */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex items-start gap-3 p-3.5 rounded-lg bg-dark-950 border border-slate-800/80">
          <Target className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <div className="font-semibold text-slate-200">{t.targetAssigned}:</div>
            <div className="font-mono text-emerald-400 text-sm font-bold">
              {challenge.targetIp} <span className="text-slate-500 font-normal">({challenge.targetHostname})</span>
            </div>
          </div>
        </div>

        <div className="flex items-start gap-3 p-3.5 rounded-lg bg-amber-500/5 border border-amber-500/20 text-amber-300 text-xs">
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-amber-200">Simulation Boundary:</div>
            <div>{t.simulatedWarning}</div>
          </div>
        </div>
      </div>

      {/* Objective */}
      <div className="text-sm text-slate-300 bg-dark-950/60 p-4 rounded-lg border border-slate-800">
        <span className="font-semibold text-white block mb-1">Objective:</span>
        <p className="text-slate-400 leading-relaxed">{challenge.objective[lang]}</p>
      </div>
    </div>
  );
};
