import type { BudgetCoverSceneData } from "@/lib/templates/types";

type BudgetCoverSceneProps = {
  data: BudgetCoverSceneData;
};

export function BudgetCoverScene({ data }: BudgetCoverSceneProps) {
  return (
    // 预算封面模板：
    // 作用是把视频内容按“预算区间”切成章节。
    // 这里大量用了 cqw 单位，原因是它会随预览容器大小自动缩放，适合做固定比例画布。
    <div className="template-grid relative h-full w-full overflow-hidden bg-[#08090d] px-[2.2cqw] py-[2cqw] text-white">
      {/* 装饰背景光效，不承载业务信息。 */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(53,231,255,0.14),transparent_25%),radial-gradient(circle_at_bottom_left,rgba(255,114,191,0.18),transparent_28%)]" />

      <div className="relative flex h-full flex-col">
        {/* 顶部信息：创作者名 + 当前模板的说明性标签。 */}
        <div className="flex items-center justify-between">
          <p className="display-font text-[1.4cqw] font-semibold tracking-[0.18em] text-white">
            {data.creator}
          </p>
          <div className="rounded-full border-[0.08cqw] border-white/10 bg-white/5 px-[1.2cqw] py-[0.5cqw] text-[0.86cqw] uppercase tracking-[0.26em] text-ink-1">
            {data.kicker}
          </div>
        </div>

        {/* 中部主视觉：左边徽章，右边预算标题大卡片。 */}
        <div className="mt-[5.4cqw] flex flex-1 items-center gap-[2.2cqw]">
          <div className="flex h-[15.4cqw] w-[15.4cqw] shrink-0 items-center justify-center rounded-full border-[0.32cqw] border-white bg-[radial-gradient(circle_at_top,#ffd8ee_0%,#f6b2da_42%,#c97bff_100%)] shadow-[0_0_4cqw_rgba(255,114,191,0.2)]">
            <span className="display-font text-[4.1cqw] font-black text-black">
              {data.badge}
            </span>
          </div>

          <div className="flex flex-1 flex-col rounded-[2.6cqw] border-[0.16cqw] border-white/20 bg-[#f6b5de] px-[3.2cqw] py-[2.8cqw] text-black shadow-[0_0_4cqw_rgba(255,114,191,0.2)]">
            <span className="display-font outline-dark text-[4.7cqw] font-black text-[#35e7ff]">
              {data.budget}
            </span>
            <span className="display-font outline-dark mt-[0.8cqw] text-[5.6cqw] font-black leading-none text-[#ff7ac7]">
              {data.title}
            </span>
            <p className="mt-[1.6cqw] max-w-[48cqw] text-[1.2cqw] leading-[1.8] text-black/70">
              {data.note}
            </p>
          </div>
        </div>

        {/* 底部辅助说明：告诉使用者这个模板用途是什么。 */}
        <div className="mt-auto flex items-center justify-between pt-[2.8cqw]">
          <p className="text-[1.24cqw] text-ink-1">
            Built for section breaks, part covers, and strong budget-band transitions.
          </p>
          <div className="rounded-full border-[0.08cqw] border-accent-cyan/35 bg-accent-cyan/12 px-[1.2cqw] py-[0.5cqw] text-[0.92cqw] text-accent-cyan">
            JSON-ready
          </div>
        </div>
      </div>
    </div>
  );
}
