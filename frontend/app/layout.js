import "./globals.css";
import { Plus_Jakarta_Sans, Inter } from "next/font/google";
import Footer from "@/components/Footer";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-display",
  display: "swap",
});
const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-body",
  display: "swap",
});

export const metadata = {
  metadataBase: new URL("https://valueweave.in"),
  title: "ValueWeave — Where Ambition Finds Its Team",
  description:
    "India's collaboration & opportunity discovery platform. Connect with builders, find co-founders, post opportunities — from tier-2 towns to global ambitions.",
  openGraph: {
    title: "ValueWeave — Where Ambition Finds Its Team",
    description: "India's collaboration & opportunity discovery platform.",
    url: "https://valueweave.in",
    siteName: "ValueWeave",
    locale: "en_IN",
    type: "website",
  },
  twitter: { card: "summary_large_image", title: "ValueWeave", description: "Where Ambition Finds Its Team." },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${jakarta.variable} ${inter.variable}`}>
      <body className="font-body antialiased">
        {children}
        <Footer />
      </body>
    </html>
  );
}
