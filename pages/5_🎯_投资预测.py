"""
🎯 投资预测页面（占位）
后续实现：博主观点爬取、综合预测评分
"""
import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_SYMBOLS, BLOGGER_SOURCES
from services.blogger_scraper import get_all_blogger_views, calculate_prediction_score

st.set_page_config(
    page_title="投资预测",
    page_icon="🎯",
    layout="wide",
)


def main():
    st.title("🎯 投资预测")
    st.markdown("---")

    # 品种选择
    selected = st.selectbox(
        "选择品种",
        options=list(DEFAULT_SYMBOLS.keys()),
    )

    st.markdown("---")

    # 博主观点来源
    st.subheader("📋 博主/分析师来源")
    st.markdown("以下为规划的数据来源，正逐步接入中：")

    source_data = []
    for name, info in BLOGGER_SOURCES.items():
        source_data.append({
            "博主/分析师": name,
            "平台": info["platform"],
            "链接": info.get("url", "暂无"),
        })
    st.dataframe(
        pd.DataFrame(source_data),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # 博主观点汇总（当前为占位）
    st.subheader("💬 博主观点汇总")
    views_df = get_all_blogger_views()
    st.dataframe(views_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 综合预测评分
    st.subheader("🎯 综合预测评分")
    score = calculate_prediction_score(views_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("综合评分", value=f"{score['score']}/100")
    with col2:
        st.metric("方向判断", value=score["direction"])
    with col3:
        st.metric("置信度", value=score["confidence"])

    st.info("🚧 博主观点爬取功能正在开发中，当前显示为占位数据")

    # 免责声明
    st.markdown("---")
    st.caption("""
    ⚠️ **免责声明**：本页面的博主观点和预测评分仅供参考，不构成投资建议。
    投资有风险，入市需谨慎。请根据自身情况独立做出投资决策。
    """)


main()
