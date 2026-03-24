import type { Metadata } from "next";
import {
  Bricolage_Grotesque,
  JetBrains_Mono,
  Noto_Sans_SC,
} from "next/font/google";
import "./globals.css";

// 这里统一注册全站字体。
// 后面如果你想整体换风格，优先改这里，而不是到每个组件里逐个替换。
const displayFont = Bricolage_Grotesque({
  subsets: ["latin"],
  variable: "--font-display",
});

const bodyFont = Noto_Sans_SC({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "700", "900"],
});

const monoFont = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

// Next.js 的 metadata 会自动写入页面的 <title> 和 meta description。
// 这是全局默认值，单个页面也可以自己覆盖。
export const metadata: Metadata = {
  title: {
    default: "Bilibili Goods Ops Console",
    template: "%s | Bilibili Goods Ops Console",
  },
  description:
    "A human-in-the-loop operations console for Bilibili product-content workflows, built with Next.js and Tailwind CSS.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      // 这里把字体变量挂到 html 上，下面所有页面都能直接使用。
      className={`${displayFont.variable} ${bodyFont.variable} ${monoFont.variable} h-full antialiased`}
    >
      {/* body 只负责提供全站的基础容器，真正的页面结构在各自 page.tsx 中实现。 */}
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
