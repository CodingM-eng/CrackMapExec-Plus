import { NextRequest, NextResponse } from "next/server";
import { validateFlag } from "../../../../ctf/engine/flags";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { challengeId, flag } = body;

    if (!challengeId || !flag) {
      return NextResponse.json({ valid: false, message: "Missing challengeId or flag" }, { status: 400 });
    }

    const isValid = validateFlag(challengeId, flag);

    return NextResponse.json({
      valid: isValid,
      message: isValid ? "Flag accepted" : "Incorrect flag",
    });
  } catch (err) {
    return NextResponse.json({ valid: false, message: "Server error" }, { status: 500 });
  }
}
