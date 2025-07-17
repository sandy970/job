import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Job Dashboard - AI-Enhanced Job Search",
  description: "Real-time job application dashboard with AI-powered matching and insights",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <div className="min-h-screen bg-gray-50">
            <header className="bg-white shadow-sm border-b">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                  <div className="flex items-center">
                    <h1 className="text-2xl font-bold text-gray-900">
                      Job Dashboard
                    </h1>
                    <span className="ml-2 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      AI-Powered
                    </span>
                  </div>
                  <nav className="flex space-x-8">
                    <a href="#jobs" className="text-gray-500 hover:text-gray-700">
                      Jobs
                    </a>
                    <a href="#preferences" className="text-gray-500 hover:text-gray-700">
                      Preferences
                    </a>
                    <a href="#analytics" className="text-gray-500 hover:text-gray-700">
                      Analytics
                    </a>
                  </nav>
                </div>
              </div>
            </header>
            <main>{children}</main>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
