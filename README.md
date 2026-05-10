# 投资分析工具

贵金属及期货多维度投资分析平台，基于 Streamlit 构建。

## ✨ 功能特性

### 📊 行情总览
- 贵金属实时报价（黄金、白银、铂金）
- K线走势图（日K/周K/月K可切换）
- 自定义期货品种添加/删除
- 成交量展示

### 📈 技术分析
- **技术指标**：MACD、KDJ、RSI、成交量
- **均线系统**：MA5/MA10/MA20/MA60/MA120/MA250
- **缠论分析**：分型识别、笔段划分（基础版）
- **波浪理论**：推动浪/调整浪识别（基础版）
- 信号汇总与多空判断

### 💰 资金面分析（开发中）
- 持仓量分析
- 资金流向
- 多空比例

### 📰 消息面分析（开发中）
- 新闻聚合
- 事件驱动分析
- NLP情感分析

### 🎯 投资预测（开发中）
- 博主观点爬取
- 综合预测评分

## 🚀 安装与运行

### 1. 克隆项目

```bash
cd 投资分析工具
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

## 📁 项目结构

```
投资分析工具/
├── app.py                    # Streamlit主入口
├── requirements.txt          # 依赖列表
├── config.py                 # 配置文件（品种、API参数等）
├── pages/
│   ├── 1_📊_行情总览.py      # 实时行情+K线
│   ├── 2_📈_技术分析.py      # 技术指标+理论分析
│   ├── 3_💰_资金面.py        # 资金面分析（占位）
│   ├── 4_📰_消息面.py        # 新闻+事件分析（占位）
│   └── 5_🎯_投资预测.py      # 博主观点+预测（占位）
├── services/
│   ├── market_data.py        # 行情数据获取服务
│   ├── technical_analysis.py # 技术指标计算
│   ├── chan_theory.py        # 缠论分析
│   ├── elliott_wave.py       # 波浪理论
│   ├── sentiment.py          # 情感分析（占位）
│   └── blogger_scraper.py    # 博主观点爬取（占位）
├── utils/
│   └── chart_helper.py       # 图表绘制工具
└── README.md                 # 使用说明
```

## ⚙️ 配置说明

### 品种代码映射

在 `config.py` 中配置品种和 yfinance 代码的映射关系：

| 品种 | 代码 |
|------|------|
| 黄金 | GC=F |
| 白银 | SI=F |
| 铂金 | PL=F |
| 原油 | CL=F |
| 天然气 | NG=F |
| 铜 | HG=F |

更多期货代码可在 `config.py` 的 `FUTURES_SYMBOLS` 中添加。

### 技术指标参数

可在 `config.py` 中调整技术指标的默认参数：

- MACD：快线12、慢线26、信号线9
- KDJ：周期9
- RSI：周期14
- 均线：5/10/20/60/120/250

### 环境变量

- `NEWS_API_KEY`：新闻API密钥（消息面模块使用，可选）

## 🖥️ 服务器部署

### 使用 Docker 部署（推荐）

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t investment-tool .
docker run -p 8501:8501 investment-tool
```

### 直接部署

```bash
# 安装依赖
pip install -r requirements.txt

# 后台运行
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

### 使用 systemd 服务

创建 `/etc/systemd/system/investment-tool.service`：

```ini
[Unit]
Description=Investment Analysis Tool
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/投资分析工具
ExecStart=/usr/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable investment-tool
sudo systemctl start investment-tool
```

## ⚠️ 免责声明

本工具仅供学习研究使用，所有分析结果和预测均不构成投资建议。
投资有风险，入市需谨慎。过往表现不代表未来收益，请根据自身情况独立做出投资决策。

## 📝 开发计划

- [x] 行情总览（实时报价 + K线图）
- [x] 技术指标（MACD/KDJ/RSI/成交量）
- [x] 均线系统
- [x] 缠论基础分析
- [x] 波浪理论基础分析
- [ ] 缠论中枢识别与买卖点
- [ ] 波浪理论进阶分析
- [ ] 资金面分析（持仓量/资金流向）
- [ ] 消息面分析（新闻/情感分析）
- [ ] 博主观点爬取与预测评分
- [ ] 服务器部署与监控
