import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CrackMapExec+ — Modern Network Security Intelligence & Enumeration Framework",
  description:
    "CrackMapExec+ is a modern network security intelligence and enumeration framework engineered for authorized labs, CTFs, TryHackMe, Hack The Box, academic research, and educational seminars.",
  keywords: [
    "CrackMapExec+",
    "cme+",
    "Network Security",
    "Active Directory",
    "SMB",
    "LDAP",
    "WinRM",
    "SSH",
    "Nmap Intelligence",
    "CTF",
    "Cybersecurity Education",
  ],
  authors: [{ name: "CodingM-eng / CrackMapExec+ Team" }],
  openGraph: {
    title: "CrackMapExec+ — Next-Gen Security Intelligence Framework",
    description:
      "Modern network security intelligence for authorized labs, CTFs, and security research.",
    url: "https://github.com/CodingM-eng/CrackMapExec-Plus",
    siteName: "CrackMapExec+",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "CrackMapExec+",
    description:
      "Modern network security intelligence for authorized labs, CTFs, and security research.",
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className="bg-dark-950 text-slate-100 font-sans antialiased selection:bg-emerald-500/30 selection:text-emerald-200 min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  );
}
