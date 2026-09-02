'use client';

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Navbar } from "../../../components/Navbar";
import { Footer } from "../../../components/Footer";
import { CtfHeader } from "../../../ctf/components/CtfHeader";
import { CtfTerminal } from "../../../ctf/components/CtfTerminal";
import { FlagSubmission } from "../../../ctf/components/FlagSubmission";
import { HintModal } from "../../../ctf/components/HintModal";
import { getChallengeById, allChallenges } from "../../../ctf/engine/challenges";
import { Language, translations } from "../../../lib/i18n";
import {
  getStoredLanguage,
  setStoredLanguage,
  getStoredProgress,
} from "../../../lib/storage";
import { ArrowLeft, ChevronRight, Award } from "lucide-react";

export default function ChallengeRoomPage() {
  const params = useParams();
  const router = useRouter();
  const challengeId = params.id as string;
  const challenge = getChallengeById(challengeId);

  const [lang, setLang] = useState<Language>("en");
  const [hintsOpen, setHintsOpen] = useState(false);
  const [progress, setProgress] = useState({
    completedChallenges: [] as string[],
    score: 0,
    flags: {} as Record<string, string>,
    hintsUsed: {} as Record<string, number[]>,
    sessionId: "",
  });

  useEffect(() => {
    setLang(getStoredLanguage());
    setProgress(getStoredProgress());
  }, []);

  const handleLanguageChange = (newLang: Language) => {
    setLang(newLang);
    setStoredLanguage(newLang);
  };

  if (!challenge) {
    return (
      <div className="min-h-screen flex flex-col bg-dark-950 text-white">
        <Navbar lang={lang} onLanguageChange={handleLanguageChange} />
        <main className="flex-1 flex flex-col items-center justify-center p-6 space-y-4 text-center">
          <h1 className="text-2xl font-bold">Challenge Not Found</h1>
          <p className="text-sm text-slate-400">The requested CTF challenge does not exist.</p>
          <Link
            href="/ctf"
            className="px-4 py-2 bg-emerald-500 text-dark-950 font-bold rounded-lg text-sm"
          >
            Return to CTF Dashboard
          </Link>
        </main>
        <Footer lang={lang} onLanguageChange={handleLanguageChange} />
      </div>
    );
  }

  const isCompleted = progress.completedChallenges.includes(challenge.id);
  const unlockedHints = progress.hintsUsed[challenge.id] || [];

  const handleFlagSuccess = (flag: string) => {
    setProgress(getStoredProgress());
  };

  const handleHintUnlocked = (index: number) => {
    setProgress(getStoredProgress());
  };

  return (
    <div className="min-h-screen flex flex-col bg-dark-950 text-slate-100">
      <Navbar lang={lang} onLanguageChange={handleLanguageChange} />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
          <Link href="/ctf" className="hover:text-emerald-400 flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" />
            CTF Challenges
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
          <span className="text-slate-200 font-semibold">{challenge.title[lang]}</span>
        </div>

        {/* Challenge Header & Target Info */}
        <CtfHeader
          challenge={challenge}
          lang={lang}
          onOpenHints={() => setHintsOpen(true)}
          isCompleted={isCompleted}
        />

        {/* Interactive Virtual Terminal Sandbox */}
        <div className="space-y-2">
          <CtfTerminal challenge={challenge} />
        </div>

        {/* Flag Submission Box */}
        <FlagSubmission
          challengeId={challenge.id}
          points={challenge.points}
          lang={lang}
          onSuccess={handleFlagSuccess}
          isAlreadyCompleted={isCompleted}
          discoveredFlag={progress.flags[challenge.id]}
        />

        {/* Hints Modal */}
        <HintModal
          challengeId={challenge.id}
          hints={challenge.hints}
          unlockedHints={unlockedHints}
          lang={lang}
          isOpen={hintsOpen}
          onClose={() => setHintsOpen(false)}
          onHintUnlocked={handleHintUnlocked}
        />
      </main>

      <Footer lang={lang} onLanguageChange={handleLanguageChange} />
    </div>
  );
}
