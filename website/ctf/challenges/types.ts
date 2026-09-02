export type Difficulty = "Easy" | "Medium" | "Hard";

export interface ChallengeHint {
  index: number;
  penalty: number;
  text: {
    en: string;
    az: string;
    ru: string;
  };
}

export interface ChallengeService {
  port: number;
  protocol: string;
  service: string;
  version: string;
  state: "open" | "filtered" | "closed";
}

export interface Challenge {
  id: string;
  title: {
    en: string;
    az: string;
    ru: string;
  };
  difficulty: Difficulty;
  points: number;
  theme: {
    en: string;
    az: string;
    ru: string;
  };
  description: {
    en: string;
    az: string;
    ru: string;
  };
  objective: {
    en: string;
    az: string;
    ru: string;
  };
  targetIp: string;
  targetHostname: string;
  services: ChallengeService[];
  hints: ChallengeHint[];
  canonicalFlag: string;
}
