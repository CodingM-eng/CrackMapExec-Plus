'use client';

import React from "react";
import { Language, translations } from "../lib/i18n";
import {
  Binary,
  Layers,
  ShieldCheck,
  Network,
  Cpu,
  Stethoscope,
  Bug,
  Video,
} from "lucide-react";

interface FeatureGridProps {
  lang: Language;
}

export const FeatureGrid: React.FC<FeatureGridProps> = ({ lang }) => {
  const t = translations[lang].features;

  const features = [
    {
      icon: Binary,
      title: t.nmapTitle,
      desc: t.nmapDesc,
      tag: "SIGNATURE FEATURE",
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      icon: Layers,
      title: t.transportTitle,
      desc: t.transportDesc,
      tag: "8-STAGE ENGINE",
      color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    },
    {
      icon: ShieldCheck,
      title: t.smbTitle,
      desc: t.smbDesc,
      tag: "NTLMSSP AV_PAIR",
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
    {
      icon: Network,
      title: t.multiTargetTitle,
      desc: t.multiTargetDesc,
      tag: "CIDR / RANGES",
      color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    },
    {
      icon: Cpu,
      title: t.protocolsTitle,
      desc: t.protocolsDesc,
      tag: "SMB • LDAP • WINRM • SSH",
      color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
    },
    {
      icon: Stethoscope,
      title: t.diagnosticsTitle,
      desc: t.diagnosticsDesc,
      tag: "HEALTH DIAGNOSTICS",
      color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    },
    {
      icon: Bug,
      title: t.bugTrackerTitle,
      desc: t.bugTrackerDesc,
      tag: "SANITIZED LOGS",
      color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
    },
    {
      icon: Video,
      title: t.videoCenterTitle,
      desc: t.videoCenterDesc,
      tag: "DEEP-LINK TIMESTAMPS",
      color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
  ];

  return (
    <section id="features" className="w-full py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
      <div className="text-center space-y-3 max-w-3xl mx-auto">
        <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          {t.sectionTitle}
        </h2>
        <p className="text-sm sm:text-base text-slate-400">
          {t.sectionSubtitle}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((f, i) => {
          const Icon = f.icon;
          return (
            <div
              key={i}
              className="p-6 rounded-2xl bg-dark-900 border border-slate-800 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between space-y-4 group hover:shadow-xl hover:shadow-emerald-950/10"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-xl border ${f.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-dark-950 border border-slate-800 text-slate-400">
                    {f.tag}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
                  {f.title}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {f.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
