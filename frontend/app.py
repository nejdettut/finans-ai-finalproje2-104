import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from groq import Groq
from dotenv import load_dotenv

# --- BACKEND LOGIC INTEGRATION ---
# Instead of calling an external API, we use the logic directly for Streamlit Cloud
load_dotenv()

SYSTEM_PROMPT = """
Sen kıdemli bir finans danışmanı ve yapay zeka asistanısın. Kullanıcının harcamalarını analiz ederek sadece veri sunmakla kalmaz, aynı zamanda derinlemesine finansal stratejiler geliştirirsin.

Görevlerin:
1. Harcamaları kalem kalem ayır ve kategorize et.
2. Her kategori için harcama yoğunluğunu değerlendir.
3. Tasarruf önerilerini şu kategorilerde detaylandır: 'Kısa Vadeli Aksiyonlar', 'Yaşam Tarzı Değişiklikleri', 'Yatırım Fırsatları'.
4. Her öneri için bir açıklama ve tahmini tasarruf potansiyeli (TL bazında) belirt.

Yanıtını şu JSON formatında dön:
{
    "status": "success",
    "analysis": {
        "items": [
            {"item": "ürün", "amount": 0.0, "category": "Kategori", "date": "2026-03-06"}
        ],
        "total_amount": 0.0,
        "summary": "Analiz özeti.",
        "detailed_recommendations": [
            {"title": "Başlık", "description": "Detay", "type": "Tür", "impact": "Yüksek", "estimated_saving": "100 TL"}
        ],
        "spending_risk": "Düşük"
    }
}
"""

def analyze_with_groq(text):
    client = Groq(api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"))
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

# --- UI CONFIG ---
st.set_page_config(page_title="AI Finans Danışmanı", page_icon="💰", layout="wide")

# (Custom CSS remains the same...)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #FF4B4B; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 AI Destekli Kişisel Finans Danışmanı")

col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area("Harcama Metni", placeholder="Örn: Market 500 TL, Kira 2000 TL...", height=150)
    if st.button("Stratejik Analiz Başlat ✨"):
        if user_input:
            with st.spinner("Llama 3.3 analiz ediyor..."):
                try:
                    # DIRECT CALL INSTEAD OF API
                    data = analyze_with_groq(user_input)
                    st.session_state.analysis_data = data
                    st.success("Analiz tamamlandı!")
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")

with col2:
    st.markdown("### 📊 Finansal Sağlık")
    if 'analysis_data' in st.session_state:
        analysis = st.session_state.analysis_data.get('analysis', {})
        total = float(analysis.get('total_amount', 0))
        risk = analysis.get('spending_risk', 'Bilinmiyor')
        
        st.metric("Toplam Harcama", f"{total:,.2f} TL")
        risk_color = "🟢" if risk == "Düşük" else "🟡" if risk == "Orta" else "🔴"
        st.markdown(f"#### Harcama Riski: {risk_color} {risk}")
    else:
        st.info("Analiz yaptıktan sonra özet burada görünecektir.")

# Analysis Results
if 'analysis_data' in st.session_state:
    st.markdown("---")
    analysis = st.session_state.analysis_data.get('analysis', {})
    items = analysis.get('items', [])
    
    if items:
        df = pd.DataFrame(items)
        # Ensure amount is numeric to avoid empty charts
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        
        tab1, tab2, tab3 = st.tabs(["📋 Harcama Detayları", "📊 Görselleştirme", "💡 Stratejik Öneriler"])
        
        with tab1:
            st.dataframe(df, use_container_width=True)
            
        with tab2:
            c1, c2 = st.columns(2)
            
            with c1:
                fig_pie = px.pie(df, values='amount', names='category', title='Kategori Dağılımı',
                                color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with c2:
                # Ensure data is ready for grouping
                df_grouped = df.groupby('category')['amount'].sum().reset_index()
                df_grouped = df_grouped.sort_values(by='amount', ascending=False)
                
                # Standard Vertical Bar Chart - Clean and Reliable
                fig_bar = px.bar(
                    df_grouped, 
                    x='category', 
                    y='amount',
                    title='Kategori Bazlı Toplam Harcama',
                    color='category', # Standard coloring
                    color_discrete_sequence=px.colors.qualitative.Pastel, # Same palette as Pie
                    text_auto='.2f', 
                    labels={'amount': 'Toplam Tutar (TL)', 'category': 'Kategori'},
                    height=450
                )
                
                fig_bar.update_layout(
                    showlegend=False,
                    xaxis={'categoryorder':'total descending'},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    margin=dict(t=50, l=10, r=10, b=50)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
        with tab3:
            st.markdown("### 🏹 Akıllı Finansal Stratejiler")
            detailed_recs = analysis.get('detailed_recommendations', [])
            
            summary = analysis.get('summary', "")
            if summary:
                st.info(f"📍 **Genel Analiz:** {summary}")
            
            for rec in detailed_recs:
                with st.expander(f"📌 {rec.get('title')} ({rec.get('impact')} Etki)"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(rec.get('description'))
                        st.caption(f"Kategori: {rec.get('type')}")
                    with c2:
                        st.metric("Potansiyel Tasarruf", rec.get('estimated_saving', "N/A"))

else:
    # Showcase empty state with instructions
    st.markdown("---")
    st.markdown("### 🚀 Nasıl Kullanılır?")
    cols = st.columns(3)
    cols[0].markdown("**1. Harcamalarını Yaz**\nFişlerini veya günlük harcamalarını buraya olduğu gibi yapıştır.")
    cols[1].markdown("**2. AI Analiz Etsin**\nLLM harcamalarını tek tek ayırsın, kategorize etsin.")
    cols[2].markdown("**3. Tasarruf Et**\nHarcama alışkanlıklarını gör ve AI'dan öneriler al.")
