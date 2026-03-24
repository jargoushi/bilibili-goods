import type { ReactNode } from "react";

type CanvasShellProps = {
  title: string;
  description: string;
  children: ReactNode;
};

export function CanvasShell({
  title,
  description,
  children,
}: CanvasShellProps) {
  return (
    // 这个组件不关心“里面到底是什么模板”。
    // 它只负责提供统一的模板预览外壳：标题、说明、1920x1080 画布容器。
    <section className="panel-surface rounded-[32px] p-4">
      <div className="mb-4 flex flex-col gap-3 border-b border-white/8 px-2 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-accent-cyan">
            Live Preview
          </p>
          <h2 className="display-font mt-2 text-2xl font-semibold text-white">
            {title}
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-7 text-ink-1">
            {description}
          </p>
        </div>

        <div className="mono-font inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-ink-1">
          Canvas 1920 × 1080
        </div>
      </div>

      <div className="overflow-hidden rounded-[28px] border border-white/10 bg-black/20 p-3">
        {/* 
          aspect-[16/9] 把容器锁成 16:9 比例；
          template-canvas 开启容器尺寸单位，这样里面可以大量使用 cqw 来等比缩放。
        */}
        <div className="template-canvas aspect-[16/9] w-full overflow-hidden rounded-[22px] border border-white/6 bg-[#06070b]">
          {children}
        </div>
      </div>
    </section>
  );
}
