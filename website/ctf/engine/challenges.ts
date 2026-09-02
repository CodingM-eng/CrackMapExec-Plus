import { Challenge } from "../challenges/types";
import { forgottenEndpointChallenge } from "../challenges/forgotten-endpoint";
import { ghostHeadersChallenge } from "../challenges/ghost-headers";
import { brokenGatewayChallenge } from "../challenges/broken-gateway";

export const allChallenges: Challenge[] = [
  forgottenEndpointChallenge,
  ghostHeadersChallenge,
  brokenGatewayChallenge,
];

export function getChallengeById(id: string): Challenge | undefined {
  return allChallenges.find((c) => c.id === id);
}
