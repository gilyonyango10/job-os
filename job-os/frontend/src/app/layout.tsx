import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Job OS",
  description: "Capture and track job opportunities before you apply.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-muted/40 font-sans">
        <header className="border-b border-border bg-background">
          <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-sm font-semibold tracking-tight">
              Job OS
            </Link>
            <p className="text-sm text-muted-foreground">Jobs</p>
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
