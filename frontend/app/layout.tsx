import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Property Recommender",
  description: "A Berlin short-stay recommender with hybrid retrieval and explainable ranking.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
