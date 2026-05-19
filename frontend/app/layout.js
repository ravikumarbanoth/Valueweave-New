import "./globals.css";

export const metadata = {
  title: "ValueWeave — Where Ambition Finds Its Team",
  description: "India's collaboration & opportunity discovery platform. Connect with builders, find co-founders, post opportunities.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
