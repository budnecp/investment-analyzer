"""
📰 消息面分析页面（占位）
后续实现：新闻聚合、事件驱动分析、NLP情感分析
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_SYMBOLS

st.set_page_config(
    page_title="消息面",
    page_icon="📰",
    layout="wide",
)


def main():
    st.title("📰 消息面分析")
    st.markdown("---")

    st.info("🚧 消息面分析模块正在建设中...")

    st.markdown("""
    ### 规划功能

    #### 📰 新闻聚合
    - 贵金属/期货相关新闻自动抓取
    - 多源新闻整合（财经网站、社交媒体）
    - 新闻重要性评级

    #### ⚡ 事件驱动分析
    - 重大经济事件日历（FOMC、非农等）
    - 事件对市场的影响评估
    - 历史事件回测

    #### 🤖 NLP情感分析
    - 新闻文本情感分析（利好/利空/中性）
    - 市场情绪指数
    - 情感趋势变化图

    ---

    > 📌 数据来源规划：新闻API、社交媒体、经济日历API
    """)

    # 品种选择占位
    st.subheader("选择品种")
    selected = st.selectbox(
        "品种",
        options=list(DEFAULT_SYMBOLS.keys()),
        disabled=True,
    )

    st.caption("该功能需要接入新闻API和NLP模型，正在规划中")


main()
