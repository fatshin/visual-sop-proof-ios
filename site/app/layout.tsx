import "./globals.css";

export const metadata = {
  title: "Oracle Council — 記憶を読み、次の一歩を選ぶ",
  description:
    "ObsidianとChatGPTから自分で選んだ記憶を、易・タロット・占星術など10の象徴体系で読み直すローカルファーストの内省ツールです。",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    title: "Oracle Council",
    description: "未来を占う前に、自分の記憶を読む。",
    type: "website",
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "Oracle Council — 未来を占う前に、自分の記憶を読む。",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Oracle Council",
    description: "未来を占う前に、自分の記憶を読む。",
    images: ["/og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
