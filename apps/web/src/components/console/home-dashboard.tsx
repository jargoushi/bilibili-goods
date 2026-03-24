import Link from "next/link";
import {
  Boxes,
  BrainCircuit,
  Clapperboard,
  DatabaseZap,
  LayoutTemplate,
  Rocket,
  Send,
  Sparkles,
  Workflow,
} from "lucide-react";
import { MetricCard } from "@/components/console/metric-card";
import { ModuleCard } from "@/components/console/module-card";
import { templateRegistry } from "@/lib/templates/registry";

// 这组数据驱动首页最上面的三张指标卡。
// 后续如果你想把“模板进度”改成真实接口数据，可以先从这里下手。
const metrics = [
  {
    label: "前端基座",
    value: "Next.js 16",
    hint: "App Router + Tailwind CSS v4，后续可继续挂模板、工作流和数据面板。",
  },
  {
    label: "模板进度",
    value: "2 / 6",
    hint: "已落地预算段封面页和商品详情点评页，其余模板已进入注册表。",
  },
  {
    label: "协作模式",
    value: "Human + AI",
    hint: "统一用 JSON 驱动模板、脚本和后续批量导出链路。",
  },
];

// 这组数据驱动首页的“模块分区”卡片。
// 当前先写成静态配置，等你后面接 API 或配置中心时，这里可以很自然地替换。
const modules = [
  {
    eyebrow: "Data Intake",
    title: "数据采集与结构化",
    description:
      "负责承接对标视频、评论区商品、详情页 OCR 与佣金数据，形成统一的商品数据底座。",
    bullets: [
      "视频解析、商品提取、价格与佣金归档到同一条业务链路",
      "给后续脚本、模板和运营模块提供单一事实来源",
      "适合先接 FastAPI 或 Python worker，前端只消费结果和任务状态",
    ],
    icon: DatabaseZap,
  },
  {
    eyebrow: "Content Studio",
    title: "内容生产工作台",
    description:
      "围绕脚本、TTS、镜头组织和模板渲染展开，目标是把视频生产过程拆成可组合的小工位。",
    bullets: [
      "脚本草稿、卖点重写、镜头清单和素材包在同一界面协同",
      "模板页直接读取 JSON，方便批量出图和追溯版本",
      "后面可以扩展批量渲染队列、历史版本和审核流",
    ],
    icon: Clapperboard,
  },
  {
    eyebrow: "Template Lab",
    title: "模板实验区",
    description:
      "当前已经落地模板注册表和两套可运行预览，后续可以扩成完整的模板市场与渲染控制台。",
    bullets: [
      "统一定义模板 id、字段、状态和样例数据",
      "所有模板都可以共用同一套 1920×1080 预览容器",
      "后续接截图导出、下载按钮和批量渲染时不需要改架构",
    ],
    icon: LayoutTemplate,
    href: "/template-lab",
  },
  {
    eyebrow: "Ops Loop",
    title: "发布与运营闭环",
    description:
      "从蓝链文本、发布清单、评论建议到收益追踪，最终都可以纳入同一套操作台。",
    bullets: [
      "面向“发布后继续运营”的真实工作流，而不是只做一次性页面",
      "评论监控、蓝链预设和收益看板可以拆成独立模块持续扩展",
      "人机协同保留人工判断位，避免全自动内容工厂的失真问题",
    ],
    icon: Send,
  },
];

// 首页右下角“工作流骨架”步骤说明。
const workflowSteps = [
  "采集层统一沉淀原始视频、商品、评论和价格数据",
  "内容层组织脚本、模板、字幕、TTS 和素材清单",
  "发布层输出封面、蓝链、清单与批量导出结果",
  "运营层回收评论、播放与收益，反哺下轮选题和模板",
];

export function HomeDashboard() {
  // 这里根据注册表动态统计已实现模板数量。
  // 好处是：后面 registry 里新增 ready 模板时，首页数字会自动更新。
  const readyCount = templateRegistry.filter(
    (template) => template.status === "ready",
  ).length;

  return (
    // page-grid 是全页背景容器，负责铺大背景和弱化网格。
    <main className="page-grid flex-1">
      <div className="relative mx-auto w-full max-w-[1440px] px-6 pb-16 pt-8 lg:px-10">
        {/* 顶部头图区域：介绍平台定位 + 快速入口按钮。 */}
        <header className="flex flex-col gap-6 border-b border-white/8 pb-8 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.3em] text-ink-1">
              <Sparkles className="size-3.5 text-accent-pink" />
              Human-in-the-loop Console
            </div>
            <h1 className="display-font mt-5 text-4xl font-semibold leading-tight text-white sm:text-5xl">
              B站好物工业化生产操作台
            </h1>
            <p className="mt-4 max-w-3xl text-base leading-8 text-ink-1 sm:text-lg">
              这是一个面向内容工业化生产的人机协同前端基座。它不是单页模板仓库，
              而是为了长期承载选品、脚本、模板、发布和运营环节的操作台。
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/template-lab"
              className="inline-flex items-center gap-2 rounded-full bg-accent-cyan px-5 py-3 text-sm font-semibold text-black transition hover:bg-white"
            >
              打开模板实验区
              <Rocket className="size-4" />
            </Link>
            <a
              href="#modules"
              className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-5 py-3 text-sm text-ink-1 transition hover:border-white/20 hover:text-white"
            >
              查看模块规划
              <Workflow className="size-4" />
            </a>
          </div>
        </header>

        {/* 第一屏：左边讲当前阶段目标，右边讲设计原则。 */}
        <section className="mt-10 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="panel-surface rounded-[36px] p-7 sm:p-9">
            <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
              <div>
                <p className="text-xs uppercase tracking-[0.32em] text-accent-cyan">
                  Ops Vision
                </p>
                <h2 className="display-font mt-4 text-3xl font-semibold text-white sm:text-4xl">
                  以模板驱动的内容生产主线
                </h2>
                <p className="mt-5 max-w-2xl text-base leading-8 text-ink-1">
                  当前版本先把最关键的前端骨架搭起来：控制台首页、
                  模板注册表、模板实验区，以及与 1920×1080 视频画面相匹配的预览容器。
                  这样后面无论接脚本编辑器、批量导出还是任务队列，都不需要再推翻。
                </p>
              </div>

              <div className="rounded-[28px] border border-white/8 bg-black/20 p-5">
                <p className="text-sm uppercase tracking-[0.24em] text-ink-2">
                  当前落地点
                </p>
                <div className="mt-4 space-y-3">
                  {[
                    "首页已经改为操作台入口，而不是默认脚手架首页",
                    "模板层建立了 registry，可统一维护模板 id 和字段",
                    "已落地预算封面页与商品详情页两个可运行样例",
                    "后面接 JSON 渲染、下载图片和批量出图时结构仍可复用",
                  ].map((item) => (
                    <div
                      key={item}
                      className="flex gap-3 rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3"
                    >
                      <Boxes className="mt-0.5 size-4 shrink-0 text-accent-pink" />
                      <p className="text-sm leading-6 text-ink-1">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {metrics.map((metric) => (
                <MetricCard key={metric.label} {...metric} />
              ))}
            </div>
          </div>

          <div className="panel-surface rounded-[36px] p-7 sm:p-8">
            <p className="text-xs uppercase tracking-[0.32em] text-accent-pink">
              Operating Principles
            </p>
            <h2 className="display-font mt-4 text-3xl font-semibold text-white">
              前端不是花架子，而是业务中枢
            </h2>

            <div className="mt-6 space-y-4">
              {[
                {
                  title: "模块化",
                  copy: "页面按业务工位拆开，而不是写成一个大而乱的神页。",
                },
                {
                  title: "JSON 优先",
                  copy: "模板先吃结构化数据，后续才能稳定做批量渲染和版本管理。",
                },
                {
                  title: "人机协同",
                  copy: "AI 负责提效，关键判断和风格修正依然保留人工控制位。",
                },
                {
                  title: "渐进扩展",
                  copy: "先把模板工作台跑通，再接任务队列、导出、权限与多端联动。",
                },
              ].map((item) => (
                <div
                  key={item.title}
                  className="rounded-[26px] border border-white/8 bg-black/25 px-5 py-5"
                >
                  <div className="flex items-center gap-3">
                    <BrainCircuit className="size-4 text-accent-cyan" />
                    <h3 className="text-lg font-semibold text-white">
                      {item.title}
                    </h3>
                  </div>
                  <p className="mt-3 text-sm leading-7 text-ink-1">{item.copy}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 中间区域：业务模块划分。 */}
        <section id="modules" className="mt-12">
          <div className="mb-6 flex items-end justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-accent-gold">
                Console Modules
              </p>
              <h2 className="display-font mt-3 text-3xl font-semibold text-white">
                操作台模块分区
              </h2>
            </div>
            <p className="max-w-xl text-sm leading-7 text-ink-2">
              现在先把承重最大的模块骨架铺好。你后面扩任何功能，都应该落到这些工位里，而不是继续堆孤立页面。
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {modules.map((module) => (
              <ModuleCard key={module.title} {...module} />
            ))}
          </div>
        </section>

        {/* 底部区域：模板系统状态 + 整体工作流说明。 */}
        <section className="mt-12 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
          <div className="panel-surface rounded-[36px] p-7 sm:p-8">
            <p className="text-xs uppercase tracking-[0.32em] text-accent-cyan">
              Template Registry
            </p>
            <h2 className="display-font mt-4 text-3xl font-semibold text-white">
              模板系统已经进入可扩展状态
            </h2>
            <p className="mt-4 max-w-2xl text-base leading-8 text-ink-1">
              你之前提到希望保留多套模板并自由组合，这一版已经按这个方向起结构：
              用统一注册表维护 6 个模板类型，其中 {readyCount} 个已经具备可运行预览。
            </p>

            <div className="mt-6 grid gap-3">
              {templateRegistry.map((template) => (
                <div
                  key={template.id}
                  className="flex items-start justify-between gap-4 rounded-[24px] border border-white/8 bg-black/20 px-5 py-4"
                >
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-white">
                        {template.name}
                      </h3>
                      <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[11px] uppercase tracking-[0.25em] text-ink-2">
                        {template.family}
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-ink-1">
                      {template.summary}
                    </p>
                  </div>

                  <span
                    className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${
                      template.status === "ready"
                        ? "bg-accent-cyan text-black"
                        : "bg-white/10 text-ink-1"
                    }`}
                  >
                    {template.status === "ready" ? "已实现" : "待实现"}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="panel-surface rounded-[36px] p-7 sm:p-8">
            <p className="text-xs uppercase tracking-[0.32em] text-accent-pink">
              Workflow Backbone
            </p>
            <h2 className="display-font mt-4 text-3xl font-semibold text-white">
              整体工作流骨架
            </h2>

            <div className="mt-6 space-y-4">
              {workflowSteps.map((step, index) => (
                <div
                  key={step}
                  className="flex gap-4 rounded-[24px] border border-white/8 bg-black/20 px-5 py-4"
                >
                  <div className="mono-font flex size-10 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/5 text-sm text-accent-cyan">
                    0{index + 1}
                  </div>
                  <p className="pt-1 text-sm leading-7 text-ink-1">{step}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 rounded-[28px] border border-accent-pink/20 bg-accent-pink/8 p-5">
              <div className="flex items-center gap-3">
                <Sparkles className="size-4 text-accent-pink" />
                <h3 className="text-lg font-semibold text-white">
                  下一步优先事项
                </h3>
              </div>
              <p className="mt-3 text-sm leading-7 text-ink-1">
                把模板实验区继续往前推进到“读取本地 JSON，再渲染 1920×1080，
                导出图片”这一条最短闭环。这个闭环一旦通了，整个平台就真正开始具备工业化产能。
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
