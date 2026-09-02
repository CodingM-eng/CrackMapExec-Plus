import { getChallengeById } from "./challenges";

export function validateFlag(challengeId: string, submittedFlag: string): boolean {
  if (!submittedFlag || typeof submittedFlag !== "string") return false;
  const clean = submittedFlag.trim();
  const challenge = getChallengeById(challengeId);
  if (!challenge) return false;

  return clean.toLowerCase() === challenge.canonicalFlag.toLowerCase();
}
