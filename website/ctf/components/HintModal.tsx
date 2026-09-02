'use client';

import React, { useState } from "react";
import { ChallengeHint } from "../challenges/types";
import { Language, translations } from "../../lib/i18n";
import { recordHintUsage } from "../../lib/storage";
import { HelpCircle, AlertTriangle, Lock, Unlock, X } from "lucide-react";

interface HintModalProps {
  challengeId: string;
  hints: ChallengeHint[];
  unlockedHints: number[];
  lang: Language;
  isOpen: boolean;
  onClose: () => void;
  onHintUnlocked: (index: number) => void;
}

export const HintModal: React.FC<HintModalProps> = ({
  challengeId,
  hints,
  unlockedHints,
  lang,
  isOpen,
  onClose,
  onHintUnlocked,
}) => {
  const t = translations[lang].ctf;
  const [confirmIndex, setConfirmIndex] = useState<number | null>(null);

  if (!isOpen) return null;

  const handleUnlock = (hint: ChallengeHint) => {
    recordHintUsage(challengeId, hint.index, hint.penalty);
    onHintUnlocked(hint.index);
    setConfirmIndex(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg bg-dark-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-5 relative">
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-dark-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 text-white font-bold text-lg border-b border-slate-800 pb-3">
          <HelpCircle className="w-5 h-5 text-amber-400" />
          <span>{t.hintsTitle}</span>
        </div>

        <div className="space-y-4">
          {hints.map((hint) => {
            const isUnlocked = unlockedHints.includes(hint.index);
            const isConfirming = confirmIndex === hint.index;

            return (
              <div
                key={hint.index}
                className={`p-4 rounded-xl border transition-all ${
                  isUnlocked
                    ? "bg-dark-950 border-slate-700 text-slate-200"
                    : "bg-dark-950/50 border-slate-800 text-slate-400"
                }`}
              >
                <div className="flex items-center justify-between gap-3 mb-2">
                  <span className="font-semibold text-sm flex items-center gap-1.5 text-slate-200">
                    {isUnlocked ? (
                      <Unlock className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Lock className="w-4 h-4 text-slate-500" />
                    )}
                    Hint {hint.index}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
                    -{hint.penalty} {t.points}
                  </span>
                </div>

                {isUnlocked ? (
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                    {hint.text[lang]}
                  </p>
                ) : isConfirming ? (
                  <div className="mt-3 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg space-y-3">
                    <div className="flex items-start gap-2 text-xs text-amber-300">
                      <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                      <span>
                        {t.unlockHintWarning} <strong>-{hint.penalty} {t.points}</strong>
                      </span>
                    </div>
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setConfirmIndex(null)}
                        className="px-3 py-1 rounded text-xs text-slate-400 hover:text-white bg-dark-800 hover:bg-dark-700"
                      >
                        {t.cancel}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleUnlock(hint)}
                        className="px-3 py-1 rounded text-xs font-semibold text-dark-950 bg-amber-400 hover:bg-amber-300"
                      >
                        {t.confirm}
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setConfirmIndex(hint.index)}
                    className="mt-2 w-full py-2 rounded-lg bg-dark-800 hover:bg-dark-700 text-xs font-semibold text-amber-400 border border-slate-700 transition-colors"
                  >
                    {t.useHint} (-{hint.penalty} {t.points})
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
