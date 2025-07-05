import streamlit as st
import pandas as pd
import numpy as np

# ページ設定
st.set_page_config(
    page_title="コンクリート集水桝計算ツール",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# メインヘッダー
st.markdown("""
<div class="main-header">
    <h1>🏗️ コンクリート集水桝 重量・体積量計算ツール</h1>
    <p>簡単・正確・美しい計算ツール</p>
</div>
""", unsafe_allow_html=True)

# サイドバーで基本寸法入力
with st.sidebar:
    st.markdown("### 📏 基本寸法設定")
    
    # 寸法入力
    outer_length = st.number_input(
        "外形縦寸法 (mm)", 
        min_value=1, 
        value=1000, 
        help="奥行き方向の外寸"
    )
    
    outer_width = st.number_input(
        "外形横寸法 (mm)", 
        min_value=1, 
        value=1000, 
        help="左右方向の外寸"
    )
    
    outer_height = st.number_input(
        "外形高さ寸法 (mm)", 
        min_value=1, 
        value=1450, 
        help="上下方向の外寸"
    )
    
    wall_thickness = st.number_input(
        "壁厚 (mm)", 
        min_value=1, 
        value=150, 
        help="コンクリートの厚み"
    )
    
    # 単位体積重量
    unit_weight = st.number_input(
        "コンクリート単位体積重量 (t/m³)", 
        min_value=1.0, 
        max_value=3.0, 
        value=2.35, 
        step=0.01,
        help="通常は2.35 t/m³"
    )
    
    # 寸法イメージ
    st.markdown("### 📊 寸法イメージ")
    st.markdown("""
    ```
    +---------------------------+
    |                           |
    |        ↑高さ              |
    |        |                  |
    |   +----+-----+            |
    |   |          | ←壁厚      |
    |   |          |            |
    |   +----------+            |
    +---------------------------+
    ←------幅------→
    ```
    """)

# メイン画面
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔧 開口部設定")
    
    # 開口部の動的追加
    if 'openings' not in st.session_state:
        st.session_state.openings = []
    
    # 新しい開口部を追加
    with st.expander("➕ 開口部を追加", expanded=True):
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            new_width = st.number_input("幅 (mm)", min_value=1, key="new_width")
        with col_b:
            new_height = st.number_input("高さ (mm)", min_value=1, key="new_height")
        with col_c:
            new_count = st.number_input("個数", min_value=1, value=1, key="new_count")
        with col_d:
            if st.button("追加", key="add_button", use_container_width=True):
                st.session_state.openings.append((new_width, new_height, new_count))
                st.success(f"✅ 開口部を追加: {new_width}×{new_height}mm × {new_count}箇所")
                st.rerun()
    
    # 現在の開口部一覧
    if st.session_state.openings:
        st.markdown("### 📋 現在の開口部一覧")
        
        openings_data = []
        for i, (width, height, count) in enumerate(st.session_state.openings):
            volume = (width * height * wall_thickness * count) / (1000**3)
            openings_data.append({
                "番号": i + 1,
                "幅 (mm)": width,
                "高さ (mm)": height,
                "個数": count,
                "体積 (m³)": f"{volume:.3f}"
            })
        
        df = pd.DataFrame(openings_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 削除機能
        col_del1, col_del2 = st.columns([1, 3])
        with col_del1:
            delete_index = st.number_input("削除する番号", min_value=1, max_value=len(st.session_state.openings), key="delete_index")
        with col_del2:
            if st.button("🗑️ 削除", key="delete_button", use_container_width=True):
                if 1 <= delete_index <= len(st.session_state.openings):
                    removed = st.session_state.openings.pop(delete_index - 1)
                    st.success(f"✅ 開口部{delete_index}を削除しました")
                    st.rerun()
    else:
        st.markdown("""
        <div class="info-box">
            <p>📝 開口部が設定されていません。上記で追加してください。</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 入力値サマリー")
    
    # 基本寸法の表示
    st.markdown(f"""
    **外形寸法:**
    - 縦: {outer_length} mm
    - 横: {outer_width} mm  
    - 高さ: {outer_height} mm
    - 壁厚: {wall_thickness} mm
    """)
    
    # 内形寸法の計算
    inner_length = outer_length - 2 * wall_thickness
    inner_width = outer_width - 2 * wall_thickness
    inner_height = outer_height - wall_thickness
    
    st.markdown(f"""
    **内形寸法:**
    - 縦: {inner_length} mm
    - 横: {inner_width} mm
    - 高さ: {inner_height} mm
    """)
    
    # 開口部数
    st.markdown(f"**開口部数:** {len(st.session_state.openings)} 種類")

# 計算ボタン
st.markdown("---")
col_calc1, col_calc2, col_calc3 = st.columns([1, 2, 1])

with col_calc2:
    if st.button("🚀 計算実行", type="primary", use_container_width=True):
        
        # 入力値の妥当性チェック
        if wall_thickness >= min(outer_length, outer_width) / 2:
            st.markdown("""
            <div class="error-box">
                <h4>❌ エラー</h4>
                <p>壁厚が大きすぎます。外形寸法の半分未満にしてください。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 計算実行
            with st.spinner("🔄 計算中..."):
                
                # 1. 外形の体積
                outer_volume = outer_length * outer_width * outer_height
                outer_volume_m3 = outer_volume / (1000**3)
                
                # 2. 内形の体積
                inner_volume = inner_length * inner_width * inner_height
                inner_volume_m3 = inner_volume / (1000**3)
                
                # 3. 開口部の体積
                total_opening_volume = 0
                for width, height, count in st.session_state.openings:
                    opening_volume = width * height * wall_thickness * count
                    total_opening_volume += opening_volume / (1000**3)
                
                # 4. コンクリート体積
                concrete_volume = outer_volume_m3 - inner_volume_m3 - total_opening_volume
                
                # 5. コンクリート重量
                concrete_weight = concrete_volume * unit_weight
                
                # 結果表示
                st.markdown("""
                <div class="success-box">
                    <h4>✅ 計算が完了しました！</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # 結果をカード形式で表示
                col_result1, col_result2, col_result3 = st.columns(3)
                
                with col_result1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📦 コンクリート体積</h3>
                        <h2>{concrete_volume:.3f} m³</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_result2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>⚖️ コンクリート重量</h3>
                        <h2>{concrete_weight:.3f} t</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_result3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📊 単位体積重量</h3>
                        <h2>{unit_weight} t/m³</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 詳細計算過程
                with st.expander("📝 詳細計算過程", expanded=False):
                    st.markdown("### 1. 外形の体積")
                    st.markdown(f"- 外形寸法: {outer_length}mm × {outer_width}mm × {outer_height}mm")
                    st.markdown(f"- 外形体積: {outer_volume_m3:.3f} m³")
                    
                    st.markdown("### 2. 内形の体積")
                    st.markdown(f"- 内形寸法: {inner_length}mm × {inner_width}mm × {inner_height}mm")
                    st.markdown(f"- 内形体積: {inner_volume_m3:.3f} m³")
                    
                    st.markdown("### 3. 開口部の体積")
                    st.markdown(f"- 開口部体積合計: {total_opening_volume:.3f} m³")
                    
                    st.markdown("### 4. コンクリート体積の計算")
                    st.markdown(f"コンクリート体積 = 外形体積 - 内形体積 - 開口部体積")
                    st.markdown(f"コンクリート体積 = {outer_volume_m3:.3f} - {inner_volume_m3:.3f} - {total_opening_volume:.3f}")
                    st.markdown(f"コンクリート体積 = {concrete_volume:.3f} m³")
                    
                    st.markdown("### 5. コンクリート重量の計算")
                    st.markdown(f"コンクリート重量 = コンクリート体積 × 単位体積重量")
                    st.markdown(f"コンクリート重量 = {concrete_volume:.3f} × {unit_weight}")
                    st.markdown(f"コンクリート重量 = {concrete_weight:.3f} t")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🏗️ コンクリート集水桝計算ツール | 開発: AI Assistant</p>
    <p>📱 スマートフォン対応 | 🎨 美しいUI | ⚡ 高速計算</p>
</div>
""", unsafe_allow_html=True) 
