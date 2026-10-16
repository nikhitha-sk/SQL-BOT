import { Inter, JetBrains_Mono } from "next/font/google";
import Header from "@/components/Header";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

export const metadata = {
  title: "AskSQL — Business Data Assistant",
  description: "Ask questions in plain English. Get SQL, a chart and a table back.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body className="flex min-h-screen flex-col font-sans">
        <Header />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-slate-200 bg-white">
          <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-6 py-5 text-xs text-ink-500 sm:flex-row">
            <span>© {new Date().getFullYear()} AskSQL · SQL Chatbot for Business Data</span>
            <span>Read-only queries · SELECT only · 1,000 row limit · 10 s timeout</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
