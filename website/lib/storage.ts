export type Language = "en" | "az" | "ru";

export interface CTFProgress {
  completedChallenges: string[];
  score: number;
  flags: Record<string, string>;
  hintsUsed: Record<string, number[]>;
  sessionId: string;
}

const LANG_KEY = "cme_plus_lang";
const PROGRESS_KEY = "cme_plus_ctf_progress";

export function getStoredLanguage(): Language {
  if (typeof window === "undefined") return "en";
  const stored = localStorage.getItem(LANG_KEY);
  if (stored === "az" || stored === "ru" || stored === "en") {
    return stored;
  }
  return "en";
}

export function setStoredLanguage(lang: Language): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(LANG_KEY, lang);
}

export function getStoredProgress(): CTFProgress {
  const fallback: CTFProgress = {
    completedChallenges: [],
    score: 0,
    flags: {},
    hintsUsed: {},
    sessionId: "sess_" + Math.random().toString(36).substring(2, 9),
  };
  if (typeof window === "undefined") return fallback;
  try {
    const raw = localStorage.getItem(PROGRESS_KEY);
    if (!raw) {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(fallback));
      return fallback;
    }
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export function saveProgress(progress: CTFProgress): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress));
}

export function recordChallengeCompletion(challengeId: string, flag: string, pointsAwarded: number): CTFProgress {
  const prog = getStoredProgress();
  if (!prog.completedChallenges.includes(challengeId)) {
    prog.completedChallenges.push(challengeId);
    prog.score += pointsAwarded;
    prog.flags[challengeId] = flag;
    saveProgress(prog);
  }
  return prog;
}

export function recordHintUsage(challengeId: string, hintIndex: number, penalty: number): CTFProgress {
  const prog = getStoredProgress();
  if (!prog.hintsUsed[challengeId]) {
    prog.hintsUsed[challengeId] = [];
  }
  if (!prog.hintsUsed[challengeId].includes(hintIndex)) {
    prog.hintsUsed[challengeId].push(hintIndex);
    prog.score = Math.max(0, prog.score - penalty);
    saveProgress(prog);
  }
  return prog;
}
