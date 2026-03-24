import Link from "next/link";
import { ArrowRight, type LucideIcon } from "lucide-react";

type ModuleCardProps = {
  eyebrow: string;
  title: string;
  description: string;
  bullets: string[];
  icon: LucideIcon;
  href?: string;
};

export function ModuleCard({
  eyebrow,
  title,
  description,
  bullets,
  icon: Icon,
  href,
}: ModuleCardProps) {
  return (
    // 这是首页中部那种“大模块卡片”。
    // 它是纯展示组件，本身不管业务数据，只负责把传进来的内容排版出来。
    <article className="panel-surface flex h-full flex-col rounded-[30px] p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-ink-2">
            {eyebrow}
          </p>
          <h3 className="display-font mt-3 text-2xl font-semibold text-white">
            {title}
          </h3>
        </div>
        <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
          <Icon className="size-5 text-accent-cyan" />
        </div>
      </div>

      <p className="mt-4 text-sm leading-7 text-ink-1">{description}</p>

      <ul className="mt-5 space-y-3 text-sm text-ink-1">
        {bullets.map((bullet) => (
          <li key={bullet} className="flex gap-3">
            {/* 左边这个小圆点只是视觉装饰，不影响任何业务逻辑。 */}
            <span className="mt-1.5 size-1.5 rounded-full bg-accent-pink" />
            <span className="leading-6">{bullet}</span>
          </li>
        ))}
      </ul>

      <div className="mt-auto pt-6">
        {/* 
          有 href 时显示可点击入口；
          没有 href 时只显示“后续接入”，表示这个模块目前只是规划状态。
        */}
        {href ? (
          <Link
            href={href}
            className="inline-flex items-center gap-2 text-sm font-medium text-accent-cyan transition hover:text-white"
          >
            打开模块
            <ArrowRight className="size-4" />
          </Link>
        ) : (
          <span className="inline-flex items-center gap-2 text-sm text-ink-2">
            结构已预留，后续接入
          </span>
        )}
      </div>
    </article>
  );
}
