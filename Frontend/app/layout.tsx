import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { UserNav } from "@/components/auth/UserNav";

const inter = Inter({ 
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter"
});

export const metadata: Metadata = {
  title: "Assinc Manutenções",
  description: "Controle de manutenção preventiva e corretiva (GLPI)"
};

export default function RootLayout({
  children
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="font-sans antialiased">
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
          <header className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white shadow-lg">
            <div className="mx-auto max-w-7xl px-6 py-10">
              <div className="flex items-start justify-between gap-6">
                <Link href="/" className="flex items-center gap-3" aria-label="Ir para a tela principal">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
                  <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                      Assinc Manutenções
                    </h1>
                    <p className="mt-1 text-sm text-blue-100">
                      Controle de manutenção preventiva e corretiva dos dispositivos integrados ao GLPI
                    </p>
                  </div>
                </Link>

                <div className="pt-1">
                  <UserNav />
                </div>
              </div>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-10">{children}</main>
        </div>
      </body>
    </html>
  );
}
