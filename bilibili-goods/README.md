# bilibili-goods

`B站好物工业化生产操作台（人机协同版）`项目骨架。

## 目录

- `app/` FastAPI 后端和业务模块
- `frontend/` Streamlit 可视化页面
- `data/` 数据库、模板、知识库、输出目录
- `docs/业务导航.md` 中文业务定位说明（建议先看）

## 中文导航（先看这个）

- 中文业务索引见：`docs/业务导航.md`
- 原则：先按“业务目标”找模块，不按英文名字猜

## 环境要求

- Python 3.11+
- 建议使用虚拟环境（`venv`）

## 快速开始（推荐）

### 1) 创建并激活虚拟环境

PowerShell:

```powershell
cd "D:\py-workspace\my-fullstack-app\bilibili-goods-workspace\bilibili-goods"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
cd "/d/py-workspace/my-fullstack-app/bilibili-goods-workspace/bilibili-goods"
python -m venv .venv
source .venv/Scripts/activate
```

如果 PowerShell 首次激活报执行策略错误，可先执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2) 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3) 统一入口启动（推荐）

```powershell
# 同时启动后端和前端（默认后端开启热更新）
python main.py

# 仅启动后端（默认热更新）
python main.py api

# 仅启动前端
python main.py ui

# 指定端口
python main.py --api-port 8021 api

# 关闭后端热更新
python main.py --api-port 8021 --no-reload api
```

## 单独启动（可选）

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
python -m streamlit run frontend/streamlit_app.py
```

## 验证是否正常

后端启动后访问：

- `http://127.0.0.1:8000/`（根路径）
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/docs`

预期：

- `/health` 返回 `{"status":"ok"}`
- `/api/health` 返回 `{"status":"ok"}`

## 已实现接口（第一阶段）

- `POST /api/collect/run` 同步采集（视频解析 -> 评论提链 -> 佣金 -> 入库）
- `POST /api/collect/run-async` 异步采集任务
- `GET /api/tasks/{task_id}` 任务状态查询
- `GET /api/products` 商品池查询
- `GET /api/videos` 视频列表
- `GET /api/videos/{video_id}/links` 视频评论商品链接
- `POST /api/products/export` 导出商品池 Excel

## 页面说明

- `1_数据采集.py` 已接通采集、异步任务、导出
- `2_商品库.py` 已接通商品查询和导出
- `3~7` 已提供可操作 MVP 逻辑（评分推荐、脚本生成、发布清单、运营分析、知识库）

## 当前 TODO（已标注在代码内）

- 京东/淘宝联盟接口目前为模拟查询，需要替换为真实 API 鉴权调用
- TTS 目前为占位输出，需要接入 ChatTTS/CosyVoice 实际推理
- OCR 目前为规则抽取，需要接入 PaddleOCR
- 部分模块当前为内存存储（脚本库/版本管理），后续可迁移到 SQLite

## 常见问题

### 1) `No module named uvicorn`

说明当前虚拟环境未安装依赖。执行：

```bash
python -m pip install -r requirements.txt
```

### 2) `streamlit` 命令找不到

不要直接用 `streamlit`，改用：

```bash
python -m streamlit run frontend/streamlit_app.py
```

### 3) 浏览器访问返回 404

- 先确认访问的是正确端口，例如 `http://127.0.0.1:8021/health`
- 若 `/health` 正常而根路径异常，重启后端并确认使用的是当前项目代码
- 可直接访问 `http://127.0.0.1:PORT/docs` 查看路由是否已加载

### 4) VS Code 没用到 `.venv`

在 VS Code 执行：

1. `Ctrl + Shift + P`
2. `Python: Select Interpreter`
3. 选择当前项目 `.venv\Scripts\python.exe`

## 当前状态

- 已按架构文档完成目录和模块实现（含详细中文注释）
- 已提供可运行的第一阶段采集闭环和导出能力
- 已提供统一启动入口 `main.py`
- 已提供 Streamlit 主页面和 7 个可操作 MVP 页面
