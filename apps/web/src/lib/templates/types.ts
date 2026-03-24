import { z } from "zod";

// 所有模板 id 都在这里统一登记。
// 好处是：后续新增模板时，类型系统会提醒你哪些地方还没接上。
export const templateIds = [
  "pastel-hero",
  "pastel-showcase",
  "photo-highlight",
  "budget-cover",
  "product-grid",
  "product-detail",
] as const;

export type TemplateId = (typeof templateIds)[number];
export type TemplateStatus = "ready" | "planned";

// 这是“模板注册表”里每一条记录的通用结构。
// 它不描述具体画面数据，只描述模板本身的信息。
export type TemplateDefinition = {
  id: TemplateId;
  name: string;
  family: string;
  status: TemplateStatus;
  summary: string;
  jsonFields: string[];
};

// 预算封面模板的数据结构。
// 以后如果 JSON 里少字段或字段类型不对，zod 会在开发时及时报错。
export const budgetCoverSceneSchema = z.object({
  template: z.literal("budget-cover"),
  creator: z.string(),
  badge: z.string(),
  budget: z.string(),
  title: z.string(),
  kicker: z.string(),
  note: z.string(),
});

export type BudgetCoverSceneData = z.infer<typeof budgetCoverSceneSchema>;

// 商品详情页里，每一张“小视觉卡片”的字段定义。
export const productVisualSchema = z.object({
  eyebrow: z.string(),
  title: z.string(),
  caption: z.string(),
  accent: z.enum(["pink", "cyan", "gold", "lime"]),
});

// 商品详情页里底部参数卡片的数据结构。
export const productMetricSchema = z.object({
  label: z.string(),
  value: z.string(),
});

// 商品详情页右下角的点评段落结构。
export const highlightBlockSchema = z.object({
  label: z.string(),
  content: z.string(),
});

// 商品详情页整体的数据结构。
// 它比预算封面复杂很多，所以更适合先通过 schema 把边界固定住。
export const productDetailSceneSchema = z.object({
  template: z.literal("product-detail"),
  creator: z.string(),
  creatorBadge: z.string(),
  headerTitle: z.string(),
  pageIndex: z.string(),
  productName: z.string(),
  summary: z.string(),
  visuals: z.array(productVisualSchema).min(3).max(4),
  metrics: z.array(productMetricSchema).min(2).max(3),
  configurations: z.array(z.string()).min(1),
  highlights: z.array(highlightBlockSchema).min(2).max(4),
});

export type ProductDetailSceneData = z.infer<typeof productDetailSceneSchema>;

// 当前已经真正落地的模板 id。
// 后续做“只显示已完成模板”时，可以直接用这组数据。
export const readyTemplateIds = ["budget-cover", "product-detail"] as const;
export type ReadyTemplateId = (typeof readyTemplateIds)[number];
