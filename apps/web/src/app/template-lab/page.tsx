import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, CheckCircle2, LayoutTemplate, Sparkles } from "lucide-react";
import { CanvasShell } from "@/components/templates/canvas-shell";
import { BudgetCoverScene } from "@/components/templates/budget-cover-scene";
import { ProductDetailScene } from "@/components/templates/product-detail-scene";
import {
  budgetCoverSample,
  productDetailSample,
  templateRegistry,
} from "@/lib/templates/registry";

// 这个页面的标题和描述只作用于 /template-lab 这一路由。
export const metadata: Metadata = {
  title: "Template Lab",
  description:
    "Template previews and schema notes for the Bilibili goods operations console.",
};

export default function TemplateLabPage() {
  // 这里先筛出已实现模板，方便下方展示“当前可用模板”。
  const readyTemplates = templateRegistry.filter(
    (template) => template.status === "ready",
  );

  return (
    // 这个页面的职责不是“生产最终视频图”，而是给你看模板现状、字段结构和预览效果。
    <main className="page-grid flex-1">
      <div className="relative mx-auto w-full max-w-[1560px] px-6 pb-16 pt-8 lg:px-10">
        {/* 页头：介绍当前实验区用途，并提供返回首页入口。 */}
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/8 pb-7">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.28em] text-ink-1">
              <LayoutTemplate className="size-3.5 text-accent-cyan" />
              Template Lab
            </div>
            <h1 className="display-font mt-5 text-4xl font-semibold text-white sm:text-5xl">
              模板实验区
            </h1>
            <p className="mt-4 max-w-3xl text-base leading-8 text-ink-1 sm:text-lg">
              这里专门承接你的视频画面模板。当前已经实现 2 套可运行模板，
              并且把 6 套模板类型全部登记进注册表，后续直接继续往这里扩。
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-ink-1 transition hover:border-white/20 hover:text-white"
            >
              <ArrowLeft className="size-4" />
              返回控制台
            </Link>
          </div>
        </div>

        {/* 第一块：左边是模板注册表，右边是两个可运行模板预览。 */}
        <section className="mt-8 grid gap-6 xl:grid-cols-[0.86fr_1.14fr]">
          <div className="panel-surface rounded-[32px] p-6 sm:p-7">
            <div className="flex items-center gap-3">
              <Sparkles className="size-4 text-accent-pink" />
              <p className="text-xs uppercase tracking-[0.28em] text-accent-pink">
                Registry Snapshot
              </p>
            </div>
            <h2 className="display-font mt-4 text-3xl font-semibold text-white">
              模板注册表
            </h2>
            <p className="mt-4 text-sm leading-7 text-ink-1">
              这层是后续模板系统的核心。每个模板都应该有固定的 id、
              字段清单、状态和样例数据，而不是随手堆一个孤立页面。
            </p>

            <div className="mt-6 grid gap-3">
              {templateRegistry.map((template) => (
                <div
                  key={template.id}
                  className="rounded-[24px] border border-white/8 bg-black/20 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {template.name}
                      </h3>
                      <p className="mt-1 text-xs uppercase tracking-[0.22em] text-ink-2">
                        {template.id}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-medium ${
                        template.status === "ready"
                          ? "bg-accent-cyan text-black"
                          : "bg-white/10 text-ink-1"
                      }`}
                    >
                      {template.status === "ready" ? "已实现" : "待实现"}
                    </span>
                  </div>

                  <p className="mt-3 text-sm leading-6 text-ink-1">
                    {template.summary}
                  </p>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {template.jsonFields.map((field) => (
                      <span
                        key={field}
                        className="mono-font rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] text-ink-1"
                      >
                        {field}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            {/* 预算封面页预览。 */}
            <CanvasShell
              title="预算段封面页"
              description="这一页对应你视频里 1000 元以内、1000-2000、2000-3000 这类预算分段封面。后续只换 JSON 数据，不换结构。"
            >
              <BudgetCoverScene data={budgetCoverSample} />
            </CanvasShell>

            {/* 商品详情页预览。 */}
            <CanvasShell
              title="商品详情点评页"
              description="这一页用于单品拆解。当前先用结构化占位内容替代真实图片，等你接入素材后就能直接量产。"
            >
              <ProductDetailScene data={productDetailSample} />
            </CanvasShell>
          </div>
        </section>

        {/* 第二块：告诉你现在已经具备什么能力，以及下一个最短闭环是什么。 */}
        <section className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="panel-surface rounded-[32px] p-6 sm:p-7">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="size-4 text-accent-cyan" />
              <p className="text-xs uppercase tracking-[0.28em] text-accent-cyan">
                Ready Now
              </p>
            </div>
            <h2 className="display-font mt-4 text-3xl font-semibold text-white">
              当前已经能做什么
            </h2>

            <ul className="mt-5 space-y-3 text-sm leading-7 text-ink-1">
              {[
                "进入模板实验区查看 1920×1080 预览容器和两套样例模板",
                "统一管理模板 id、状态、字段列表与样例数据",
                "把模板拆成可复用组件，而不是一张图一个 HTML 文件",
                "为后续接图片下载、批量渲染和本地 JSON 导入留出结构",
              ].map((item) => (
                <li key={item} className="flex gap-3">
                  <span className="mt-2 size-1.5 rounded-full bg-accent-pink" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="panel-surface rounded-[32px] p-6 sm:p-7">
            <div className="flex items-center gap-3">
              <Sparkles className="size-4 text-accent-gold" />
              <p className="text-xs uppercase tracking-[0.28em] text-accent-gold">
                Next Step
              </p>
            </div>
            <h2 className="display-font mt-4 text-3xl font-semibold text-white">
              后续最短闭环
            </h2>
            <p className="mt-4 text-sm leading-7 text-ink-1">
              下一步最值得做的是把“读取本地 JSON，选择模板，渲染画面，再下载
              1920×1080 图片”这一整条链路打通。这个闭环一旦跑通，
              你就可以开始围绕模板、素材和脚本做真正的工业化生产。
            </p>

            <div className="mt-5 rounded-[24px] border border-white/8 bg-black/20 p-4">
              <p className="mono-font text-xs uppercase tracking-[0.22em] text-ink-2">
                ready templates
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {readyTemplates.map((template) => (
                  <span
                    key={template.id}
                    className="rounded-full border border-accent-cyan/30 bg-accent-cyan/12 px-3 py-1 text-sm text-accent-cyan"
                  >
                    {template.id}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
