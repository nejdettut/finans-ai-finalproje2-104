import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Config
st.set_page_config(
    page_title="AI Finans Asistanı",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    .category-card {
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00D1FF;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header
st.title("💰 AI Destekli Kişisel Finans Danışmanı")
st.markdown("Harcamalarınızı doğal dille yazın, AI sizin için stratejik analiz yapsın.")

# User Input Section
col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area(
        "Harcama Metni",
        placeholder="Örn: Marketten 500 TL alışveriş yaptım. Dün 150 TL'ye sinemaya gittim. 2000 TL kira ödedim.",
        height=200
    )
    
    if st.button("Stratejik Analiz Başlat ✨"):
        if user_input:
            with st.spinner("Llama 3.3 analiz ediyor..."):
                try:
                    response = requests.post(
                        "http://127.0.0.1:8000/analyze",
                        json={"text": user_input, "provider": "groq"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.analysis_data = data
                        st.success("Analiz başarıyla tamamlandı!")
                    else:
                        st.error(f"Hata: {response.text}")
                except Exception as e:
                    st.error(f"Bağlantı hatası: {e}")
        else:
            st.warning("Lütfen analiz edilecek bir metin girin.")

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
