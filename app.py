"""
投资分析工具 - Streamlit 主入口
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, LAYOUT, PAGE_CONFIG

# 页面配置
st.set_page_config(**PAGE_CONFIG)

# 侧边栏
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=80)
    st.title(APP_TITLE)
    st.markdown("---")
    st.markdown("""
    ### 📌 功能导航

    - 📊 **行情总览** — 实时报价 & K线图
    - 📈 **技术分析** — 技术指标 & 理论分析
    - 💰 **资金面** — 持仓量 & 资金流向
    - 📰 **消息面** — 新闻 & 事件分析
    - 🎯 **投资预测** — 博主观点 & 预测

    ---
    """)

    st.markdown("""
    ### ℹ️ 关于

    本工具为贵金属及期货投资分析平台，
    提供多维度价格预测能力。

    **数据源：** yfinance（延迟约15分钟）

    **技术栈：** Streamlit + Plotly + pandas-ta

    ---
    """)

    st.caption("v0.1.0 | 仅供学习参考，不构成投资建议")

# 主页内容
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("---")

# 欢迎区域
st.markdown("""
### 👋 欢迎使用投资分析工具

本工具提供贵金属及期货品种的多维度分析能力，帮助你做出更明智的投资决策。
""")

# 功能概览
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
        <h2>📊</h2>
        <h4>行情总览</h4>
        <p>实时报价<br/>K线走势</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 10px; color: white;'>
        <h2>📈</h2>
        <h4>技术分析</h4>
        <p>MACD/KDJ/RSI<br/>缠论/波浪</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px; color: white;'>
        <h2>💰</h2>
        <h4>资金面</h4>
        <p>持仓分析<br/>资金流向</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 10px; color: white;'>
        <h2>📰</h2>
        <h4>消息面</h4>
        <p>新闻聚合<br/>情感分析</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); border-radius: 10px; color: white;'>
        <h2>🎯</h2>
        <h4>投资预测</h4>
        <p>博主观点<br/>综合评分</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 快速入口
st.subheader("🚀 快速开始")
st.markdown("""
请从左侧导航栏选择功能模块，或点击上方对应卡片进入：

1. **行情总览** → 查看贵金属实时报价和K线走势图
2. **技术分析** → 使用MACD、KDJ、RSI等指标，或缠论/波浪理论进行分析
3. **资金面** → 查看持仓量、资金流向等数据（开发中）
4. **消息面** → 浏览新闻和情感分析（开发中）
5. **投资预测** → 汇集博主观点，综合预测评分（开发中）
""")

# 免责声明
st.markdown("---")
st.caption("""
⚠️ **免责声明**：本工具仅供学习研究使用，所有分析结果和预测均不构成投资建议。
投资有风险，入市需谨慎。过往表现不代表未来收益，请根据自身情况独立做出投资决策。
""")
