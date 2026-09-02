'use client';

import React from "react";
import { Challenge } from "../challenges/types";
import { Language, translations } from "../../lib/i18n";
import { Trophy, CheckCircle2, Lock, ArrowRight, RotateCcw } from "lucide-react";
import Link from "next/link";

interface CtfProgressProps {
  challenges: Challenge[];
  completedIds: string[];
  score: number;
  flags: Record<string, string>;
  lang: Language;
  onReset: () => void;
}

export const CtfProgress: React.FC<CtfProgressProps> = ({
  challenges,
  completedIds,
  score,
  flags,
  lang,
  onReset,
}) => {
  const t = translations[lang].ctf;
  const totalPoints = challenges.reduce((sum, c) => sum + c.points, 0);
  const completionPercentage = Math.round((completedIds.length / challenges.length) * 100);

  const getRank = (scoreVal: number) => {
    if (scoreVal >= 500) return "Master Protocol Operator";
    if (scoreVal >= 250) return "Senior Intelligence Specialist";
    if (scoreVal >= 100) return "Junior Lab Scout";
    return "Recruit Operator";
  };

  return (
    <div className="w-full space-y-6">
      {/* Score and Stats Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-dark-900 border border-slate-800 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">{t.scoreLabel}</div>
            <div className="text-2xl font-bold text-white font-mono">
              {score} <span className="text-xs text-slate-500">/ {totalPoints}</span>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-dark-900 border border-slate-800 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">{t.challengesCount}</div>
            <div className="text-2xl font-bold text-white font-mono">
              {completedIds.length} <span className="text-xs text-slate-500">/ {challenges.length} ({completionPercentage}%)</span>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-dark-900 border border-slate-800 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Trophy className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">{t.rankLabel}</div>
            <div className="text-sm font-bold text-amber-300 font-mono">
              {getRank(score)}
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-dark-900 p-4 rounded-xl border border-slate-800 space-y-2">
        <div className="flex justify-between text-xs text-slate-400">
          <span>{t.yourProgress}</span>
          <span className="font-mono font-bold text-emerald-400">{completionPercentage}%</span>
        </div>
        <div className="w-full h-2.5 rounded-full bg-dark-950 overflow-hidden border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full transition-all duration-500"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Challenge Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {challenges.map((c) => {
          const isDone = completedIds.includes(c.id);

          return (
            <div
              key={c.id}
              className={`p-6 rounded-xl border flex flex-col justify-between transition-all duration-200 ${
                isDone
                  ? "bg-dark-900/90 border-emerald-500/40 shadow-lg shadow-emerald-950/20"
                  : "bg-dark-900 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                      c.difficulty === "Easy"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                        : c.difficulty === "Medium"
                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                    }`}
                  >
                    {c.difficulty}
                  </span>
                  <span className="text-xs font-mono font-semibold text-slate-400">
                    +{c.points} {t.points}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white tracking-tight">
                  {c.title[lang]}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                  {c.description[lang]}
                </p>

                <div className="pt-2 text-xs font-mono text-slate-500">
                  Target: <span className="text-slate-300">{c.targetIp}</span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between">
                {isDone ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" />
                    {t.completed}
                  </span>
                ) : (
                  <span className="text-xs text-slate-500 font-medium">Ready</span>
                )}

                <Link
                  href={`/ctf/${c.id}`}
                  className="flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg bg-dark-800 hover:bg-emerald-500 hover:text-dark-950 text-slate-200 border border-slate-700 transition-all"
                >
                  {isDone ? "Review Room" : t.startChallenge}
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* Flag Vault */}
      <div className="w-full bg-dark-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-emerald-400" />
            {t.vaultTitle}
          </h2>
          {completedIds.length > 0 && (
            <button
              type="button"
              onClick={onReset}
              className="text-xs text-slate-500 hover:text-rose-400 flex items-center gap-1 transition-colors"
            >
              <RotateCcw className="w-3 h-3" />
              {t.resetProgress}
            </button>
          )}
        </div>

        {completedIds.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-2">{t.noFlagsYet}</p>
        ) : (
          <div className="space-y-2">
            {challenges.map((c) => {
              const flag = flags[c.id];
              return (
                <div
                  key={c.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-dark-950 rounded-lg border border-slate-800 text-xs font-mono gap-2"
                >
                  <span className="text-slate-300 font-semibold">{c.title[lang]}:</span>
                  {flag ? (
                    <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      {flag}
                    </span>
                  ) : (
                    <span className="text-slate-600 italic">Locked</span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
