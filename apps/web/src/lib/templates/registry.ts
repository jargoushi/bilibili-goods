import {
  budgetCoverSceneSchema,
  productDetailSceneSchema,
  type BudgetCoverSceneData,
  type ProductDetailSceneData,
  type TemplateDefinition,
} from "@/lib/templates/types";

// 模板注册表：
// 这里不是具体页面渲染，而是维护“系统里有哪些模板、模板属于哪一类、现在是否已经实现”。
export const templateRegistry: TemplateDefinition[] = [
  {
    id: "pastel-hero",
    name: "浅色角色开场页",
    family: "opening",
    status: "planned",
    summary: "用于视频开场、结尾或单句强调的大标题页。",
    jsonFields: ["creator", "mascotImage", "title", "subtitle", "decorations"],
  },
  {
    id: "pastel-showcase",
    name: "浅色展示说明页",
    family: "showcase",
    status: "planned",
    summary: "左侧角色 + 右侧内容区，适合放商品卡、品类对比和卖点说明。",
    jsonFields: ["creator", "mascotImage", "headline", "cards", "caption"],
  },
  {
    id: "photo-highlight",
    name: "实拍高光页",
    family: "photo",
    status: "planned",
    summary: "大图展示某个真实操作瞬间，适合承接实拍素材和视频截帧。",
    jsonFields: ["creator", "photo", "headline", "caption", "overlay"],
  },
  {
    id: "budget-cover",
    name: "预算段封面页",
    family: "section",
    status: "ready",
    summary: "预算切页模板，负责把视频内容按价格段切成多个 part。",
    jsonFields: ["creator", "badge", "budget", "title", "kicker", "note"],
  },
  {
    id: "product-grid",
    name: "四列商品总览页",
    family: "listing",
    status: "planned",
    summary: "四列卡片总览，用于同预算区间的商品速览和初筛。",
    jsonFields: ["creator", "headerTitle", "part", "items[]"],
  },
  {
    id: "product-detail",
    name: "商品详情点评页",
    family: "review",
    status: "ready",
    summary: "单个商品的结构化点评页，适合配置、参数和推荐理由并排展示。",
    jsonFields: [
      "creator",
      "creatorBadge",
      "headerTitle",
      "pageIndex",
      "productName",
      "summary",
      "visuals[]",
      "metrics[]",
      "configurations[]",
      "highlights[]",
    ],
  },
];

// 预算封面模板的样例数据。
// 模板实验区会直接拿它来渲染预览，后续也可以替换成真实 JSON。
export const budgetCoverSample: BudgetCoverSceneData = budgetCoverSceneSchema.parse({
  template: "budget-cover",
  creator: "星源爱 · bilibili",
  badge: "XY",
  budget: "1000元以内",
  title: "升降桌推荐",
  kicker: "预算段封面 / Budget Cover",
  note: "用于承接每个预算区间的开场，后续只需要替换预算文案和副标题即可复用。",
});

// 商品详情模板的样例数据。
// 这里用 parse 的原因是：样例数据本身也会经过 schema 校验，避免“样例都写错”的情况。
export const productDetailSample: ProductDetailSceneData =
  productDetailSceneSchema.parse({
    template: "product-detail",
    creator: "星源爱",
    creatorBadge: "XY",
    headerTitle: "2025年双12 · 升降桌推荐 · 1000元以内",
    pageIndex: "01",
    productName: "乐歌 E2",
    summary: "这是一个为 JSON 驱动渲染准备的结构化详情模板。后续接入真实商品图、价格和卖点后，可以直接量产点评页。",
    visuals: [
      {
        eyebrow: "主视图",
        title: "核心桌面视角",
        caption: "适合替换为主商品图、Broll 截帧或经过裁切的详情页素材。",
        accent: "pink",
      },
      {
        eyebrow: "操控细节",
        title: "控制面板",
        caption: "这里建议放特写图，强化高度记忆、数显和按键逻辑。",
        accent: "cyan",
      },
      {
        eyebrow: "桌面卖点",
        title: "板材与稳定性",
        caption: "可用来补充承重、桌板厚度、桌腿结构等信息。",
        accent: "gold",
      },
      {
        eyebrow: "使用情境",
        title: "家庭或宿舍场景",
        caption: "承接脚本里的典型用户场景，帮助人和货建立关系。",
        accent: "lime",
      },
    ],
    metrics: [
      {
        label: "升降范围",
        value: "72-116cm",
      },
      {
        label: "噪音水平",
        value: "49dB",
      },
      {
        label: "适配人群",
        value: "入门首购",
      },
    ],
    configurations: [
      "单电机 1.0m*0.6m 参考价：891",
      "单电机 1.2m*0.6m 参考价：934",
      "单电机 1.4m*0.7m 参考价：1019",
      "单电机 1.6m*0.8m 参考价：1104",
    ],
    highlights: [
      {
        label: "关键配置",
        content:
          "单电机结构，桌面尺寸 1.0-1.6 米可选，4 档高度记忆，适合预算有限但需要基础升降体验的用户。",
      },
      {
        label: "推荐理由",
        content:
          "它不是“花哨型”产品，但很适合作为入门模板示例，因为字段简单、结构稳定、后续可批量替换。",
      },
    ],
  });
