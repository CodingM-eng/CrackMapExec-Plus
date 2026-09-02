'use client';

import React, { useState } from "react";
import { Language, translations } from "../../lib/i18n";
import { validateFlag } from "../engine/flags";
import { recordChallengeCompletion } from "../../lib/storage";
import { Flag, CheckCircle2, XCircle, Send } from "lucide-react";

interface FlagSubmissionProps {
  challengeId: string;
  points: number;
  lang: Language;
  onSuccess: (flag: string) => void;
  isAlreadyCompleted: boolean;
  discoveredFlag?: string;
}

export const FlagSubmission: React.FC<FlagSubmissionProps> = ({
  challengeId,
  points,
  lang,
  onSuccess,
  isAlreadyCompleted,
  discoveredFlag,
}) => {
  const t = translations[lang].ctf;
  const [flagInput, setFlagInput] = useState(discoveredFlag || "");
  const [status, setStatus] = useState<"idle" | "success" | "error">(
    isAlreadyCompleted ? "success" : "idle"
  );
  const [feedbackMsg, setFeedbackMsg] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!flagInput.trim()) return;

    const isValid = validateFlag(challengeId, flagInput);
    if (isValid) {
      setStatus("success");
      setFeedbackMsg(`${t.flagAccepted} (+${points} ${t.points})`);
      recordChallengeCompletion(challengeId, flagInput.trim(), points);
      onSuccess(flagInput.trim());
    } else {
      setStatus("error");
      setFeedbackMsg(t.flagIncorrect);
    }
  };

  return (
    <div className="w-full bg-dark-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
      <div className="flex items-center gap-2 text-white font-semibold text-base border-b border-slate-800 pb-3">
        <Flag className="w-4 h-4 text-emerald-400" />
        <span>{t.flagPrompt}</span>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={flagInput}
            onChange={(e) => {
              setFlagInput(e.target.value);
              if (status === "error") setStatus("idle");
            }}
            disabled={isAlreadyCompleted}
            placeholder="cme+{...}"
            className={`w-full px-4 py-2.5 bg-dark-950 font-mono text-sm rounded-lg border outline-none transition-all ${
              status === "success"
                ? "border-emerald-500/60 text-emerald-400 bg-emerald-500/5"
                : status === "error"
                ? "border-rose-500/60 text-rose-400 bg-rose-500/5 focus:border-rose-500"
                : "border-slate-700 text-white placeholder:text-slate-600 focus:border-emerald-500"
            }`}
          />
        </div>

        <button
          type="submit"
          disabled={isAlreadyCompleted || !flagInput.trim()}
          className={`flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-lg ${
            isAlreadyCompleted
              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 cursor-not-allowed"
              : "bg-emerald-500 hover:bg-emerald-400 text-dark-950 font-bold shadow-emerald-500/20 cursor-pointer"
          }`}
        >
          {isAlreadyCompleted ? (
            <>
              <CheckCircle2 className="w-4 h-4" />
              {t.completed}
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              {t.submitFlag}
            </>
          )}
        </button>
      </form>

      {status === "success" && (
        <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-lg animate-fadeIn">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          <span>{feedbackMsg || t.flagAccepted}</span>
        </div>
      )}

      {status === "error" && (
        <div className="flex items-center gap-2 text-sm text-rose-400 bg-rose-500/10 border border-rose-500/30 p-3 rounded-lg animate-shake">
          <XCircle className="w-5 h-5 shrink-0" />
          <span>{feedbackMsg || t.flagIncorrect}</span>
        </div>
      )}
    </div>
  );
};
