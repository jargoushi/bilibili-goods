# 04 商品信息抓取与 OCR

## 1. 模块定位

抓取商品详情页图文信息，用 OCR 提取参数，再用 AI 整理为“可直接写脚本”的结构化卖点。

对应代码目录：
- `app/modules/product_info/detail_crawler.py`
- `app/modules/product_info/ocr_extractor.py`
- `app/modules/product_info/ai_summarizer.py`

## 2. 边界定义

- 负责：详情抓取、图片下载、OCR 识别、卖点提炼。
- 不负责：佣金查询和脚本生成最终编排。

## 3. 输入与输出

- 输入：`platform + product_id + detail_url`
- 输出：
- `title`
- `price`
- `params_json`
- `selling_points[]`
- `scenes[]`

## 4. 数据结构

- `product_details`（建议新增）：
- `product_id`
- `detail_html_path`
- `image_paths`
- `ocr_raw_text`
- `params_json`
- `selling_points_json`

## 5. 核心流程

1. 用 requests 或 playwright 抓取详情页。
2. 下载参数图、卖点图和主图。
3. OCR 提取文本并清洗噪音。
4. 送 AI 网关做字段归一和卖点总结。
5. 入库并生成“脚本填充字段”。

## 6. 接口设计

- `POST /api/product-info/extract`
- 请求：`{"platform":"jd","product_id":"123","detail_url":"..."}`
- 返回：结构化参数和卖点

- `GET /api/product-info/{product_id}`
- 返回最近一次抓取结果

## 7. 异常与重试

- 页面反爬：切换浏览器指纹 + 代理。
- OCR 质量低：保留原文并标记置信度。
- AI 整理失败：返回 OCR 原文供人工编辑。

## 8. 监控指标

- 抓取成功率
- OCR 字段提取完整率
- 卖点提炼可用率（人工抽样）
- 单商品处理耗时

## 9. MVP 验收标准

- 10 个商品中至少 8 个能输出参数表。
- 每个商品输出至少 3 条可读卖点。
- 结果可被脚本生成器直接消费。
