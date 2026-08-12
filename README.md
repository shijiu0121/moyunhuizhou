# 墨蕴徽州 —— 徽文化数字文创智造平台

基于 AIGC 的徽文化数字文创平台。iCAN 2026 创新赛道·智慧文创方向。

## 项目结构

```
mojyun-huizhou/
├── docs/          # 技术方案书、开发日志（原创材料）、数据来源清单
├── backend/       # FastAPI 后端
│   └── app/
│       ├── routes/     # generate / ask / export / tour 四个接口
│       ├── image_gen/  # 可插拔生图服务（local / remote / api）
│       ├── rag/        # 知识库 + 向量库 + RAG 问答
│       └── export/     # 文创合成
└── frontend/      # Vue3 前端
```

## 快速启动

### 后端（FastAPI）
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # 填 DeepSeek 等密钥
uvicorn app.main:app --reload
# 访问 http://localhost:8000/docs
```

### 前端（Vue3）
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

## 详细文档
- 技术方案：`docs/项目技术方案书.md`
- 原创材料：`docs/开发日志.md`
- 数据来源：`docs/数据来源清单.md`
