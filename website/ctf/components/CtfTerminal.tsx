'use client';

import React, { useState, useRef, useEffect } from "react";
import { Challenge } from "../challenges/types";
import { executeSimulation } from "../engine/simulator";
import { Terminal as TerminalIcon, CornerDownLeft, Trash2 } from "lucide-react";

interface TerminalLine {
  id: string;
  type: "input" | "output";
  text: string;
  isError?: boolean;
}

interface CtfTerminalProps {
  challenge: Challenge;
}

export const CtfTerminal: React.FC<CtfTerminalProps> = ({ challenge }) => {
  const [lines, setLines] = useState<TerminalLine[]>([
    {
      id: "init-1",
      type: "output",
      text: "\x1b[32mCrackMapExec+ Virtual CTF Sandbox v0.1.0\x1b[0m\nType '\x1b[33mhelp\x1b[0m' to list commands, or '\x1b[33mnmap " + challenge.targetIp + "\x1b[0m' to start reconnaissance.",
    },
  ]);
  const [inputVal, setInputVal] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const [isProcessing, setIsProcessing] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines, isProcessing]);

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const rawInput = inputVal.trim();
    if (!rawInput) return;

    const newHistory = [...history, rawInput];
    setHistory(newHistory);
    setHistoryIndex(-1);
    setInputVal("");

    const inputEntry: TerminalLine = {
      id: `in-${Date.now()}`,
      type: "input",
      text: rawInput,
    };

    setLines((prev) => [...prev, inputEntry]);
    setIsProcessing(true);

    setTimeout(() => {
      const res = executeSimulation(rawInput, challenge, newHistory);
      setIsProcessing(false);

      if (res.clearTerminal) {
        setLines([]);
      } else {
        const outputEntry: TerminalLine = {
          id: `out-${Date.now()}`,
          type: "output",
          text: res.output,
          isError: res.isError,
        };
        setLines((prev) => [...prev, outputEntry]);
      }
    }, 180);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length === 0) return;
      const nextIdx = historyIndex === -1 ? history.length - 1 : Math.max(0, historyIndex - 1);
      setHistoryIndex(nextIdx);
      setInputVal(history[nextIdx] || "");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIndex === -1) return;
      const nextIdx = historyIndex + 1;
      if (nextIdx >= history.length) {
        setHistoryIndex(-1);
        setInputVal("");
      } else {
        setHistoryIndex(nextIdx);
        setInputVal(history[nextIdx] || "");
      }
    } else if (e.key === "l" && e.ctrlKey) {
      e.preventDefault();
      setLines([]);
    }
  };

  const renderAnsi = (text: string) => {
    const parts = text.split(/(\x1b\[[0-9;]*m)/g);
    let currentColor = "text-slate-300";

    return parts.map((part, i) => {
      if (part === "\x1b[32m") {
        currentColor = "text-emerald-400 font-semibold";
        return null;
      }
      if (part === "\x1b[31m") {
        currentColor = "text-rose-400 font-semibold";
        return null;
      }
      if (part === "\x1b[33m") {
        currentColor = "text-amber-400 font-semibold";
        return null;
      }
      if (part === "\x1b[34m") {
        currentColor = "text-cyan-400 font-semibold";
        return null;
      }
      if (part === "\x1b[36m") {
        currentColor = "text-teal-300";
        return null;
      }
      if (part === "\x1b[0m") {
        currentColor = "text-slate-300";
        return null;
      }
      return (
        <span key={i} className={currentColor}>
          {part}
        </span>
      );
    });
  };

  return (
    <div className="w-full rounded-xl border border-slate-800 bg-dark-950 font-mono shadow-2xl overflow-hidden flex flex-col">
      {/* Terminal Titlebar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-dark-900 border-b border-slate-800 text-xs text-slate-400 select-none">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          </div>
          <span className="ml-2 font-semibold text-slate-300 flex items-center gap-1.5">
            <TerminalIcon className="w-3.5 h-3.5 text-emerald-400" />
            cme+ virtual-terminal • {challenge.targetIp}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] px-2 py-0.5 rounded bg-dark-800 border border-slate-700 text-emerald-400 font-mono">
            SANDBOX ACTIVE
          </span>
          <button
            type="button"
            onClick={() => setLines([])}
            title="Clear terminal (Ctrl+L)"
            className="hover:text-slate-200 transition-colors p-1"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Output Area */}
      <div
        className="p-4 flex-1 overflow-y-auto space-y-3 min-h-[360px] max-h-[500px] text-xs sm:text-sm leading-relaxed"
        onClick={() => inputRef.current?.focus()}
      >
        {lines.map((line) => (
          <div key={line.id} className="whitespace-pre-wrap font-mono break-all">
            {line.type === "input" ? (
              <div className="flex items-center gap-2 text-emerald-400">
                <span className="text-slate-500 font-bold select-none">cme+ &gt;</span>
                <span className="text-white font-medium">{line.text}</span>
              </div>
            ) : (
              <div className="text-slate-300 pl-4 border-l-2 border-slate-800">
                {renderAnsi(line.text)}
              </div>
            )}
          </div>
        ))}

        {isProcessing && (
          <div className="flex items-center gap-2 text-slate-400 pl-4">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-xs text-emerald-400/80 font-mono">Simulating protocol probe...</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Command Input Prompt */}
      <form
        onSubmit={handleCommandSubmit}
        className="flex items-center gap-2 px-4 py-3 bg-dark-900 border-t border-slate-800"
      >
        <span className="text-emerald-400 font-bold text-xs sm:text-sm select-none">cme+ &gt;</span>
        <input
          ref={inputRef}
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g. nmap 10.13.37.42, smb, inspect, help..."
          className="flex-1 bg-transparent border-none outline-none text-white font-mono text-xs sm:text-sm placeholder:text-slate-600 focus:ring-0"
          autoFocus
          spellCheck={false}
          autoComplete="off"
        />
        <button
          type="submit"
          className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-colors"
          title="Run command (Enter)"
        >
          <CornerDownLeft className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
