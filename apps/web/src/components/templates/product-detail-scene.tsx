import type { ProductDetailSceneData } from "@/lib/templates/types";

// 不同 accent 对应不同的边框、背景和文字颜色。
// 后续如果你新增颜色风格，优先在这里补映射，而不是去 JSX 里硬改。
const accentStyles = {
  pink: {
    border: "border-accent-pink/40",
    bg: "bg-accent-pink/10",
    text: "text-accent-pink",
  },
  cyan: {
    border: "border-accent-cyan/40",
    bg: "bg-accent-cyan/10",
    text: "text-accent-cyan",
  },
  gold: {
    border: "border-accent-gold/40",
    bg: "bg-accent-gold/10",
    text: "text-accent-gold",
  },
  lime: {
    border: "border-accent-lime/40",
    bg: "bg-accent-lime/10",
    text: "text-accent-lime",
  },
} as const;

type ProductDetailSceneProps = {
  data: ProductDetailSceneData;
};

export function ProductDetailScene({ data }: ProductDetailSceneProps) {
  return (
    // 商品详情模板：
    // 这是当前最重要的结构化模板之一，未来大概率会接真实商品图、价格矩阵和 AI 生成的点评文案。
    <div className="template-grid relative h-full w-full overflow-hidden bg-[#07080d] px-[2cqw] py-[1.8cqw] text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,114,191,0.14),transparent_24%),radial-gradient(circle_at_bottom_right,rgba(53,231,255,0.1),transparent_30%)]" />

      <div className="relative flex h-full flex-col">
        {/* 顶栏：创作者信息、当前章节标题、页码。 */}
        <div className="flex items-center justify-between gap-[1.4cqw]">
          <div className="flex items-center gap-[1.2cqw]">
            <div className="flex h-[4.6cqw] w-[4.6cqw] items-center justify-center rounded-full border-[0.16cqw] border-white bg-[radial-gradient(circle_at_top,#ffdff0_0%,#f2b9df_48%,#af76ff_100%)]">
              <span className="display-font text-[1.3cqw] font-black text-black">
                {data.creatorBadge}
              </span>
            </div>
            <div>
              <p className="display-font text-[1.05cqw] font-semibold tracking-[0.2em] text-white">
                {data.creator}
              </p>
              <p className="text-[0.88cqw] uppercase tracking-[0.22em] text-ink-2">
                Product Detail Review
              </p>
            </div>
          </div>

          <div className="flex min-w-[32cqw] items-center justify-center rounded-full border-[0.12cqw] border-white/18 bg-[#f4b7e0] px-[2.4cqw] py-[0.7cqw]">
            <span className="display-font text-[1.6cqw] font-black text-black">
              {data.headerTitle}
            </span>
          </div>

          <div className="flex h-[4.8cqw] min-w-[6.8cqw] items-center justify-center rounded-[1.3cqw] border-[0.14cqw] border-white bg-[#f4b7e0] px-[1.4cqw]">
            <span className="mono-font text-[2.1cqw] font-black text-black">
              {data.pageIndex}
            </span>
          </div>
        </div>

        {/* 主体分成左右两栏：左边偏视觉和参数，右边偏配置和点评。 */}
        <div className="mt-[1.6cqw] grid flex-1 grid-cols-[1.08fr_0.92fr] gap-[1.4cqw]">
          <section className="rounded-[1.8cqw] border-[0.14cqw] border-white/14 bg-black/35 p-[1.2cqw] shadow-[0_2cqw_4cqw_rgba(0,0,0,0.25)]">
            <div className="flex items-center justify-between">
              <h2 className="display-font text-[2cqw] font-black text-[#ff8bd0]">
                {data.productName}
              </h2>
              <span className="rounded-full border-[0.08cqw] border-white/10 bg-white/5 px-[0.9cqw] py-[0.35cqw] text-[0.72cqw] uppercase tracking-[0.24em] text-ink-2">
                Visual Stack
              </span>
            </div>

            <div className="mt-[1cqw] grid h-[23.2cqw] grid-cols-2 gap-[0.9cqw]">
              {data.visuals.map((visual) => {
                // 根据当前 visual.accent 取对应的颜色方案。
                const accent = accentStyles[visual.accent];

                return (
                  <div
                    key={visual.title}
                    className={`flex flex-col rounded-[1.2cqw] border-[0.1cqw] ${accent.border} ${accent.bg} p-[1cqw]`}
                  >
                    <p className={`text-[0.72cqw] uppercase tracking-[0.22em] ${accent.text}`}>
                      {visual.eyebrow}
                    </p>
                    <h3 className="mt-[0.7cqw] display-font text-[1.24cqw] font-semibold text-white">
                      {visual.title}
                    </h3>
                    {/* 
                      这里目前是占位块。
                      后续接真实图片时，通常把这个 div 换成 <img> 或 next/image 即可。
                    */}
                    <div className="mt-[0.9cqw] flex-1 rounded-[1cqw] border-[0.08cqw] border-dashed border-white/12 bg-[linear-gradient(145deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02))]" />
                    <p className="mt-[0.8cqw] text-[0.8cqw] leading-[1.65] text-ink-1">
                      {visual.caption}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* 商品概述。适合放一句强总结或者 AI 生成的提炼描述。 */}
            <div className="mt-[1.1cqw] rounded-[1.3cqw] border-[0.08cqw] border-white/10 bg-white/[0.03] p-[1cqw]">
              <p className="text-[0.78cqw] uppercase tracking-[0.24em] text-ink-2">
                Summary
              </p>
              <p className="mt-[0.55cqw] text-[0.92cqw] leading-[1.75] text-ink-1">
                {data.summary}
              </p>
            </div>

            {/* 底部参数卡。这里适合放范围、噪音、承重等短字段。 */}
            <div className="mt-[1cqw] grid grid-cols-3 gap-[0.8cqw]">
              {data.metrics.map((metric) => (
                <div
                  key={metric.label}
                  className="rounded-[1.1cqw] border-[0.08cqw] border-white/10 bg-white/[0.04] px-[1cqw] py-[0.9cqw]"
                >
                  <p className="text-[0.72cqw] uppercase tracking-[0.22em] text-ink-2">
                    {metric.label}
                  </p>
                  <p className="mono-font mt-[0.45cqw] text-[1.3cqw] font-semibold text-white">
                    {metric.value}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="flex flex-col gap-[1.1cqw]">
            {/* 右上：配置价格矩阵。 */}
            <div className="rounded-[1.8cqw] border-[0.14cqw] border-white/14 bg-black/35 p-[1.2cqw]">
              <div className="flex items-center justify-between">
                <h3 className="display-font text-[1.8cqw] font-black text-[#ff8bd0]">
                  可选配置
                </h3>
                <span className="rounded-full border-[0.08cqw] border-white/10 bg-white/5 px-[0.8cqw] py-[0.28cqw] text-[0.66cqw] uppercase tracking-[0.2em] text-ink-2">
                  Pricing Matrix
                </span>
              </div>

              <ul className="mt-[1cqw] space-y-[0.7cqw]">
                {data.configurations.map((item) => (
                  <li
                    key={item}
                    className="rounded-[1cqw] border-[0.08cqw] border-white/10 bg-white/[0.04] px-[1cqw] py-[0.8cqw] text-[0.96cqw] leading-[1.65] text-white"
                  >
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* 右下：关键配置、推荐理由等长文本点评。 */}
            <div className="flex-1 rounded-[1.8cqw] border-[0.14cqw] border-white/14 bg-black/35 p-[1.2cqw]">
              <div className="flex items-center justify-between">
                <h3 className="display-font text-[1.8cqw] font-black text-[#35e7ff]">
                  点评摘要
                </h3>
                <span className="rounded-full border-[0.08cqw] border-white/10 bg-white/5 px-[0.8cqw] py-[0.28cqw] text-[0.66cqw] uppercase tracking-[0.2em] text-ink-2">
                  Review Notes
                </span>
              </div>

              <div className="mt-[1cqw] space-y-[0.85cqw]">
                {data.highlights.map((highlight, index) => (
                  <div
                    key={`${highlight.label}-${index}`}
                    className="rounded-[1.05cqw] border-[0.08cqw] border-white/10 bg-white/[0.04] px-[1cqw] py-[0.95cqw]"
                  >
                    <p className="display-font text-[1.08cqw] font-semibold text-[#ff8bd0]">
                      {highlight.label}
                    </p>
                    <p className="mt-[0.35cqw] text-[0.95cqw] leading-[1.75] text-ink-1">
                      {highlight.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
