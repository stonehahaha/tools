# Private Tools

这个仓库包含一个 `Vue 3 + Vite` 前端工具站，以及一个用于 PDF 团队行程整理的 `FastAPI` 后端。

## 工具列表

### 旅客信息整理

- 专门针对复杂的旅客订单信息进行结构化提取。
- 自动识别 **姓名** 与 **乘客号**。
- **Excel 兼容**：输出采用制表符（Tab）分隔，支持直接粘贴至 Excel 单元格。
- **智能容错**：支持带有空行、杂乱格式的原始数据输入。

### PDF 行程整理

- 上传人员表和 PDF。
- 服务端按团队拆分行程单。
- 返回一个 `zip`，其中包含团队 PDF 和 `match_report.csv`。

## 本地开发

### 前端

```bash
npm install
npm run dev
```

### 后端

```bash
py -3.12 -m pip install -r server/requirements.txt
py -3.12 -m uvicorn server.app:app --host 127.0.0.1 --port 8001
```

前端开发代理会把 `/api` 请求转发到 `http://127.0.0.1:8001`。

## 使用流程

1. 在输入框中粘贴从厦航官网复制的旅客信息。
2. 点击“提取旅客信息”。
3. 将输出结果直接粘贴到 Excel 或其他文档中。

## 验证命令

```bash
py -3.12 -m pytest server/tests -v
npm run test
npm run type-check
npm run build
```
