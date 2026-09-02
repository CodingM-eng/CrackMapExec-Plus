'use client';

import React, { useState } from "react";
import { Terminal, Copy, Check } from "lucide-react";

export const HeroTerminal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"smb" | "nmap">("smb");
  const [copied, setCopied] = useState(false);

  const smbCommand = "crackmapexec+ smb 10.10.10.10";
  const nmapCommand = "crackmapexec+ --nmap scan.txt";

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="w-full max-w-3xl rounded-2xl border border-slate-800 bg-dark-950 font-mono shadow-2xl shadow-emerald-950/20 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 bg-dark-900 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          </div>
          <span className="text-slate-400 font-semibold ml-2 flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            terminal • crackmapexec-plus
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex bg-dark-950 rounded-lg p-0.5 border border-slate-800">
            <button
              type="button"
              onClick={() => setActiveTab("smb")}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-all ${
                activeTab === "smb"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              SMB Probe
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("nmap")}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-all ${
                activeTab === "nmap"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Nmap Plan
            </button>
          </div>

          <button
            type="button"
            onClick={() => handleCopy(activeTab === "smb" ? smbCommand : nmapCommand)}
            title="Copy command"
            className="p-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 text-slate-300 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div className="p-5 text-xs sm:text-sm leading-relaxed space-y-4 min-h-[300px] text-slate-300">
        {activeTab === "smb" ? (
          <div className="space-y-3 animate-fadeIn">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold">
              <span className="text-slate-500 select-none">$</span>
              <span>crackmapexec+ smb 10.10.10.10</span>
            </div>

            <div className="p-3.5 rounded-lg bg-dark-900/90 border border-slate-800/80 space-y-1.5 font-mono text-[12px] sm:text-xs">
              <div className="text-teal-300 font-bold border-b border-slate-800 pb-1">
                ╭── SMB • 10.10.10.10:445 ──╮
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-x-4 gap-y-1 pt-1 text-slate-300">
                <div><span className="text-slate-500">STATUS:</span> <span className="text-emerald-400 font-bold">[+] SUCCESS</span></div>
                <div><span className="text-slate-500">HOST:</span> LAB-DC01</div>
                <div><span className="text-slate-500">OS:</span> Windows Server 2019</div>
                <div><span className="text-slate-500">BUILD:</span> 17763</div>
                <div><span className="text-slate-500">DOMAIN:</span> LAB.LOCAL</div>
                <div><span className="text-slate-500">DIALECT:</span> SMB 3.1.1</div>
                <div><span className="text-slate-500">SIGNING:</span> <span className="text-amber-300 font-semibold">Required</span></div>
                <div><span className="text-slate-500">LATENCY:</span> 0.0018s</div>
              </div>
            </div>

            <div className="text-slate-400 text-xs pl-2 border-l-2 border-emerald-500/40">
              ✓ NTLMSSP TargetInfo AV_PAIR metadata parsed safely without authentication.
            </div>
          </div>
        ) : (
          <div className="space-y-3 animate-fadeIn">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold">
              <span className="text-slate-500 select-none">$</span>
              <span>crackmapexec+ --nmap scan.txt</span>
            </div>

            <div className="p-3.5 rounded-lg bg-dark-900/90 border border-slate-800/80 space-y-2 font-mono text-[12px] sm:text-xs">
              <div className="text-teal-300 font-bold border-b border-slate-800 pb-1">
                ╭── Target Intelligence: LAB-DC01 (10.10.10.10) ──╮
              </div>
              <div className="space-y-1 text-slate-300">
                <div>88/tcp   <span className="text-amber-400">KERBEROS</span>  Microsoft Windows Kerberos</div>
                <div>389/tcp  <span className="text-emerald-400">LDAP</span>      Active Directory LDAP <span className="text-emerald-400">✓ Native Driver</span></div>
                <div>445/tcp  <span className="text-emerald-400">SMB</span>       Windows Server 2019 <span className="text-emerald-400">✓ Native Driver</span></div>
                <div>5985/tcp <span className="text-emerald-400">WINRM</span>     Microsoft HTTPAPI 2.0 <span className="text-emerald-400">✓ Native Driver</span></div>
              </div>
              <div className="pt-2 text-amber-300 font-semibold border-t border-slate-800">
                Plan: LDAP -&gt; inspect, SMB -&gt; inspect, WinRM -&gt; inspect. Continue? [y/N]
              </div>
            </div>

            <div className="text-slate-400 text-xs pl-2 border-l-2 border-cyan-500/40">
              ✓ Nmap Intelligence maps open ports to native protocol drivers with execution safety confirmation.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
