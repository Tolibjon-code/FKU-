import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta
import calendar
from io import BytesIO
import base64
import json
import time

# Аввал ёшини хисоблаш функциясини аниқлаш
def calculate_age(birth_date):
    today = date.today()
    years = today.year - birth_date.year
    months = today.month - birth_date.month
    days = today.day - birth_date.day
    
    if days < 0:
        months -= 1
        days += 30
    
    if months < 0:
        years -= 1
        months += 12
    
    return years, months, days

st.set_page_config(
    page_title="ФКУ Болалар учун Озукавий Аралашмалар Схемаси",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стиллар
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #60A5FA;
    }
    .info-card {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #3B82F6;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .warning-card {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #F59E0B;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .success-card {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #10B981;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #E5E7EB;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        border-color: #3B82F6;
    }
    .metric-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #3B82F6;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    }
    .stButton>button {
        background: linear-gradient(90deg, #3B82F6, #2563EB);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.2);
    }
    .schedule-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .morning-badge { background: #FEF3C7; color: #92400E; }
    .day-badge { background: #D1FAE5; color: #065F46; }
    .evening-badge { background: #E0E7FF; color: #3730A3; }
    .night-badge { background: #FCE7F3; color: #9D174D; }
</style>
""", unsafe_allow_html=True)

# Sidebar - Асосий маълумотлар
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966321.png", width=100)
    st.markdown("### 👤 Бола маълумотлари")
    
    child_name = st.text_input("**Боланинг исми**", "Али")
    
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("**Туғилган сана**", date(2023, 1, 1))
    with col2:
        weight = st.number_input("**Огирлик (кг)**", min_value=1.0, max_value=50.0, value=12.5, step=0.1)
    
    height = st.number_input("**Бўй (см)**", min_value=30.0, max_value=200.0, value=85.0, step=0.1)
    
    # Бола ёшини хисоблаш
    age_years, age_months, age_days = calculate_age(birth_date)
    
    # Фенилаланин даражаси
    st.markdown("---")
    st.markdown("### 🩸 Фенилаланин даражаси")
    phe_level = st.number_input("**Қондаги ФА даражаси (мкмоль/л)**", 
                                min_value=0.0, max_value=2000.0, value=240.0, step=10.0)
    
    # Мақсад даража
    target_phe = st.slider("**Мақсад даража (мкмоль/л)**", 120.0, 360.0, 240.0, step=20.0)
    
    # Озука маҳсулотлари заҳираси
    st.markdown("---")
    st.markdown("### 📦 Озукавий аралашма заҳираси")
    
    product_stock = {}
    products_list = ["Афенилак", "Нутриген-70", "ФКУ-0", "ФКУ-1", "ФКУ-2", "ФКУ-3", "PKU Sphere", "Фенил-Фри"]
    
    for product in products_list:
        product_stock[product] = st.number_input(f"{product} (пакет)", 
                                                 min_value=0, max_value=100, value=10, key=f"stock_{product}")
    
    st.markdown("---")
    st.markdown("#### 📊 Статистика")
    
    # ФА даражаси кўрсаткичи
    phe_status = ""
    if phe_level > target_phe:
        phe_status = "⬆️ Юқори"
    elif phe_level < target_phe * 0.8:
        phe_status = "⬇️ Паст"
    else:
        phe_status = "✅ Норма"
    
    st.metric("ФА даражаси", f"{phe_level} мкмоль/л", phe_status)
    
    # BMI хисоблаш
    bmi = weight / ((height/100) ** 2)
    
    bmi_status = ""
    if age_years > 2:
        if bmi > 18:
            bmi_status = "⬆️ Ортиқча"
        elif bmi < 14:
            bmi_status = "⬇️ Кам"
        else:
            bmi_status = "✅ Норма"
    else:
        bmi_status = "👶 Болача"
    
    st.metric("БМИ (BMI)", f"{bmi:.1f}", bmi_status)

# Озукавий аралашмалар базаси
products_db = {
    "Афенилак": {
        "description": "0-12 ойлиқ болалар учун",
        "protein_per_100g": 15,
        "phe_content": 0,
        "age_range": "0-12 ой",
        "daily_dose_per_kg": 3.0,
        "calories_per_100g": 480,
        "preparation": "30г аралашма + 180мл иссиқ сув (60°C) аралаштиринг, совитинг ва ичинг",
        "storage": "Хўл жойда сақланмасин, ёпиқ идишда сақлансин",
        "price_per_kg": 85000,
        "color": "#3B82F6"
    },
    "Нутриген-70": {
        "description": "1-10 йиллик болалар учун",
        "protein_per_100g": 70,
        "phe_content": 0,
        "age_range": "1-10 йил",
        "daily_dose_per_kg": 1.5,
        "calories_per_100g": 380,
        "preparation": "50г аралашма + 200мл сув ёки сут, ёхши аралаштиринг",
        "storage": "Қуруқ жойда сақлансин, очилгандан кейин 3 ҳафта ичида ишлатинг",
        "price_per_kg": 125000,
        "color": "#10B981"
    },
    "ФКУ-0": {
        "description": "0-6 ойлиқ болалар учун",
        "protein_per_100g": 12,
        "phe_content": 0,
        "age_range": "0-6 ой",
        "daily_dose_per_kg": 3.5,
        "calories_per_100g": 510,
        "preparation": "35г аралашма + 150мл иссиқ сув, хомилга мос температурагача совитинг",
        "storage": "Ўртача ҳароратда сақланг",
        "price_per_kg": 78000,
        "color": "#8B5CF6"
    },
    "ФКУ-1": {
        "description": "6-12 ойлиқ болалар учун",
        "protein_per_100g": 18,
        "phe_content": 0,
        "age_range": "6-12 ой",
        "daily_dose_per_kg": 2.5,
        "calories_per_100g": 450,
        "preparation": "40г аралашма + 180мл сув, миксерида аралаштиринг",
        "storage": "Тўғридан-тўғри қуёш нуридан сақланг",
        "price_per_kg": 82000,
        "color": "#F59E0B"
    },
    "ФКУ-2": {
        "description": "1-3 йиллик болалар учун",
        "protein_per_100g": 25,
        "phe_content": 0,
        "age_range": "1-3 йил",
        "daily_dose_per_kg": 2.0,
        "calories_per_100g": 420,
        "preparation": "Сув ёки сутга аралаштиринг, диққат билан қориштиринг",
        "storage": "Муҳрланган ҳолатда сақлансин",
        "price_per_kg": 92000,
        "color": "#EF4444"
    },
    "ФКУ-3": {
        "description": "3-10 йиллик болалар учун",
        "protein_per_100g": 40,
        "phe_content": 0,
        "age_range": "3-10 йил",
        "daily_dose_per_kg": 1.5,
        "calories_per_100g": 390,
        "preparation": "Исталган суюқлик билан аралаштириш мумкин",
        "storage": "15-25°C да сақлансин",
        "price_per_kg": 105000,
        "color": "#EC4899"
    },
    "PKU Sphere": {
        "description": "Улгʻайган болалар ва ўсмирлар учун",
        "protein_per_100g": 60,
        "phe_content": 0,
        "age_range": "10+ йил",
        "daily_dose_per_kg": 1.0,
        "calories_per_100g": 350,
        "preparation": "Сув, шарбат ёки йўғурт билан аралаштириш мумкин",
        "storage": "Салқин жойда сақлансин",
        "price_per_kg": 145000,
        "color": "#06B6D4"
    },
    "Фенил-Фри": {
        "description": "Ҳар қандай ёшдаги ФКУ касаллиги борлар учун",
        "protein_per_100g": 80,
        "phe_content": 0,
        "age_range": "Барча ёш",
        "daily_dose_per_kg": 0.8,
        "calories_per_100g": 320,
        "preparation": "Исталган таомга қўшиш мумкин",
        "storage": "Очилгандан сўнг тезда ишлатинг",
        "price_per_kg": 165000,
        "color": "#6366F1"
    }
}

# Асосий сарлавҳа
st.markdown('<h1 class="main-header">🍼 Фенилкетонурия (ФКУ) Болалар учун Озукавий Аралашмалар Тизими</h1>', unsafe_allow_html=True)

# Асосий контейнер
main_container = st.container()

with main_container:
    # Инфо карточкаси
    st.markdown(f"""
    <div class="info-card">
        <h3>👋 Ассалому алайкум, {child_name} учун ФКУ озукавий аралашмалар схемаси!</h3>
        <p><strong>👶 Бола маълумотлари:</strong> {age_years} йил {age_months} ой | {weight} кг | {height} см</p>
        <p><strong>🎯 Мақсад:</strong> Қондаги фенилаланин даражасини {target_phe} мкмоль/л да сақлаш</p>
        <p><strong>📊 Жорий ФА даражаси:</strong> {phe_level} мкмоль/л ({'Юқори' if phe_level > target_phe else 'Паст' if phe_level < target_phe * 0.8 else 'Нормада'})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Таблар
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Схема", "🍼 Тайёрлаш", "📅 Жадвал", "📊 Хисобот", "🛒 Заҳира", "ℹ️ Маълумот"])
    
    # 1-таб: Асосий схема
    with tab1:
        st.markdown('<h2 class="section-header">🎯 Озукавий Аралашма Схемаси</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Тавсия этилган аралашмалар
            def get_recommended_products(age_months, age_years):
                recommended = []
                age_in_months = age_years * 12 + age_months
                
                if age_in_months <= 6:
                    recommended.extend(["ФКУ-0", "Афенилак"])
                elif age_in_months <= 12:
                    recommended.extend(["ФКУ-1", "Афенилак"])
                elif age_in_months <= 36:
                    recommended.extend(["ФКУ-2", "Нутриген-70"])
                elif age_in_months <= 120:
                    recommended.extend(["ФКУ-3", "Нутриген-70"])
                else:
                    recommended.extend(["PKU Sphere", "Фенил-Фри"])
                
                return recommended
            
            recommended = get_recommended_products(age_months, age_years)
            
            st.markdown("### 💡 Тавсия этилган аралашмалар:")
            for i, product in enumerate(recommended):
                prod_info = products_db[product]
                st.markdown(f"""
                <div class="product-card">
                    <h4>#{i+1} {product} <span style="color: {prod_info['color']}; font-size: 0.9rem;">● {prod_info['age_range']}</span></h4>
                    <p>{prod_info['description']}</p>
                    <p><strong>Оқсил:</strong> {prod_info['protein_per_100g']}г/100г | 
                    <strong>Доза:</strong> {prod_info['daily_dose_per_kg']}г/кг | 
                    <strong>Калория:</strong> {prod_info['calories_per_100g']}ккал/100г</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Аралашма танлаш
            selected_product = st.selectbox(
                "Аралашмани танланг:",
                options=list(products_db.keys()),
                index=list(products_db.keys()).index(recommended[0]) if recommended else 0,
                key="product_select"
            )
            
            if selected_product:
                prod_info = products_db[selected_product]
                
                # Кунлик доза хисоблаш
                daily_dose = weight * prod_info['daily_dose_per_kg']
                daily_protein = daily_dose * prod_info['protein_per_100g'] / 100
                daily_calories = daily_dose * prod_info['calories_per_100g'] / 100
                
                st.markdown("### 📈 Кунлик схема:")
                st.markdown(f'<div class="metric-box">', unsafe_allow_html=True)
                st.metric("Кунлик миқдор", f"{daily_dose:.1f} г")
                st.metric("Оқсил миқдори", f"{daily_protein:.1f} г")
                st.metric("Калория миқдори", f"{daily_calories:.0f} ккал")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Доза сони
                if 'doses_per_day' not in st.session_state:
                    st.session_state.doses_per_day = 5
                
                st.session_state.doses_per_day = st.slider(
                    "Кунда неча марта олиши керак?", 
                    3, 8, st.session_state.doses_per_day, 
                    key="doses_slider"
                )
                
                # Нарх хисоби
                monthly_cost = (daily_dose * 30 * prod_info['price_per_kg'] / 1000)
                st.info(f"💵 **Ойлик харажат:** {monthly_cost:,.0f} сўм")
    
    # 2-таб: Тайёрлаш усули
    with tab2:
        st.markdown('<h2 class="section-header">🍼 Озукавий Аралашмани Тайёрлаш</h2>', unsafe_allow_html=True)
        
        if 'selected_product' in locals() and selected_product:
            prod_info = products_db[selected_product]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Тайёрлаш тартиби:")
                st.markdown(f"""
                <div class="info-card">
                    <h4>{selected_product} тайёрлаш усули:</h4>
                    <p>{prod_info['preparation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Тайёрлаш қадамлари
                steps = [
                    "Идиш ва қошиқни тозаланг",
                    "Керакли миқдорда аралашмани ўлчаб олинг",
                    "Иссиқ сув қўшинг (60-70°C)",
                    "Диққат билан аралаштиринг",
                    "Бола ичиши учун мос температурагача совитинг",
                    "Тайёрланган аралашмани 2 соат ичида ичинг"
                ]
                
                for i, step in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {step}")
                
                # Сув миқдори
                water_ratio = st.slider("Сув/Аралашма нисбати (мл/г)", 3.0, 10.0, 5.0, 0.5)
                if 'daily_dose' in locals():
                    water_needed = daily_dose * water_ratio
                    st.success(f"💧 **Кунлик сув эхтиёжи:** {water_needed:.0f} мл")
            
            with col2:
                st.markdown("### ⚠️ Сақлаш ва диққат талаблари:")
                st.markdown(f"""
                <div class="warning-card">
                    <h4>Сақлаш шартлари:</h4>
                    <p>{prod_info['storage']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Огоҳлантиришлар
                warnings = [
                    "Аралашмани шишада тайёрлаб сақланманг",
                    "Қайнатилган сув ишлатмангиз",
                    "Бошқа озуқа билан аралаштирмангиз",
                    "Тайёрланган аралашмани кечки пайтга қолдирмангиз",
                    "Идишни мунтазам тозаланг"
                ]
                
                for warning in warnings:
                    st.markdown(f"⚠️ {warning}")
                
                # Температура мониторинг
                temp = st.slider("Тайёрланган аралашма темпратураси (°C)", 20, 50, 37)
                if temp > 40:
                    st.error("📛 Жуда иссиқ! Совутинг")
                elif temp < 30:
                    st.warning("❄️ Жуда совуқ! Исситинг")
                else:
                    st.success("✅ Мос температурада")
    
    # 3-таб: Жадвал ва график
    with tab3:
        st.markdown('<h2 class="section-header">📅 Кунлик Олиш Жадвали</h2>', unsafe_allow_html=True)
        
        if 'selected_product' in locals() and selected_product:
            prod_info = products_db[selected_product]
            if 'daily_dose' in locals():
                daily_dose = weight * prod_info['daily_dose_per_kg']
                doses_per_day = st.session_state.get('doses_per_day', 5)
                dose_per_serving = daily_dose / doses_per_day
                
                # Вақт жадвали
                time_slots = {
                    "Эрталаб 07:00": "morning-badge",
                    "Нонушта 09:00": "morning-badge", 
                    "Тушликдан олдин 12:00": "day-badge",
                    "Тушлик 14:00": "day-badge",
                    "Пешинди 16:00": "day-badge",
                    "Кечки овқат 19:00": "evening-badge",
                    "Ётгунча 21:00": "night-badge"
                }
                
                time_keys = list(time_slots.keys())
                
                st.markdown("### 🕒 Вақт жадвали:")
                
                schedule_data = []
                for i in range(doses_per_day):
                    time_idx = min(i, len(time_keys)-1)
                    time_name = time_keys[time_idx]
                    badge_class = time_slots[time_name]
                    
                    schedule_data.append({
                        "Вақт": time_name,
                        "Миқдор (г)": f"{dose_per_serving:.1f}",
                        "Оқсил (г)": f"{(dose_per_serving * prod_info['protein_per_100g'] / 100):.1f}",
                        "Калория": f"{(dose_per_serving * prod_info['calories_per_100g'] / 100):.0f}",
                        "Баҳо": badge_class
                    })
                
                # Жадвални кўрсатиш
                schedule_df = pd.DataFrame(schedule_data)
                
                # HTML таблица яратиш
                html_table = "<div style='background: white; padding: 1rem; border-radius: 10px;'>"
                html_table += "<table style='width: 100%; border-collapse: collapse;'>"
                html_table += "<tr style='background: #3B82F6; color: white;'>"
                html_table += "<th style='padding: 10px; text-align: left;'>Вақт</th>"
                html_table += "<th style='padding: 10px; text-align: left;'>Миқдор (г)</th>"
                html_table += "<th style='padding: 10px; text-align: left;'>Оқсил (г)</th>"
                html_table += "<th style='padding: 10px; text-align: left;'>Калория</th>"
                html_table += "</tr>"
                
                for i, row in enumerate(schedule_data):
                    bg_color = "#F8FAFC" if i % 2 == 0 else "#FFFFFF"
                    html_table += f"<tr style='background: {bg_color};'>"
                    html_table += f"<td style='padding: 10px;'>{row['Вақт']}</td>"
                    html_table += f"<td style='padding: 10px;'>{row['Миқдор (г)']}</td>"
                    html_table += f"<td style='padding: 10px;'>{row['Оқсил (г)']}</td>"
                    html_table += f"<td style='padding: 10px;'>{row['Калория']}</td>"
                    html_table += "</tr>"
                
                html_table += "</table></div>"
                st.markdown(html_table, unsafe_allow_html=True)
                
                # График
                col1, col2 = st.columns(2)
                
                with col1:
                    # Оқсил тақсимоти
                    fig1 = go.Figure(data=[
                        go.Pie(
                            labels=[f"Доза {i+1}" for i in range(doses_per_day)],
                            values=[dose_per_serving for _ in range(doses_per_day)],
                            hole=0.4,
                            marker=dict(colors=px.colors.qualitative.Set3)
                        )
                    ])
                    
                    fig1.update_layout(
                        title=f"Кунлик доза тақсимоти",
                        height=400
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Вақт бўйича график
                    times = [d['Вақт'].split()[-1] for d in schedule_data]
                    amounts = [float(d['Миқдор (г)']) for d in schedule_data]
                    
                    fig2 = go.Figure(data=[
                        go.Bar(
                            x=times,
                            y=amounts,
                            marker_color=prod_info['color'],
                            text=[f"{amt}г" for amt in amounts],
                            textposition='auto'
                        )
                    ])
                    
                    fig2.update_layout(
                        title="Вақт бўйича дозалар",
                        xaxis_title="Вақт",
                        yaxis_title="Миқдор (г)",
                        height=400
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Хафталик жадвал
                st.markdown("### 📆 Хафталик мониторинг:")
                week_days = ["Душанба", "Сешанба", "Чоршанба", "Пайшанба", "Жума", "Шанба", "Якшанба"]
                
                week_data = []
                for day in week_days:
                    week_data.append({
                        "Кун": day,
                        "Миқдор (г)": f"{daily_dose:.1f}",
                        "Оқсил (г)": f"{(daily_dose * prod_info['protein_per_100g'] / 100):.1f}",
                        "Ичди": True,
                        "Эслатма": ""
                    })
                
                week_df = pd.DataFrame(week_data)
                edited_week_df = st.data_editor(
                    week_df,
                    column_config={
                        "Ичди": st.column_config.CheckboxColumn(
                            "Ичди",
                            help="Кунлик доза ичилдими?",
                            default=True
                        ),
                        "Эслатма": st.column_config.TextColumn(
                            "Эслатма",
                            help="Қўшимча эслатмалар"
                        )
                    },
                    use_container_width=True
                )
    
    # 4-таб: Хисоботлар
    with tab4:
        st.markdown('<h2 class="section-header">📊 Хисобот ва Таҳлил</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Кунлик хисобот
            st.markdown("### 📅 Кунлик хисобот")
            
            report_date = st.date_input("Хисобот санаси", date.today(), key="report_date")
            
            if 'selected_product' in locals() and selected_product:
                prod_info = products_db[selected_product]
                daily_dose = weight * prod_info['daily_dose_per_kg']
                
                daily_report = {
                    "Бола исми": child_name,
                    "Сана": report_date.strftime("%Y-%m-%d"),
                    "Ёши": f"{age_years} йил {age_months} ой",
                    "Огирлик": f"{weight} кг",
                    "Озукавий аралашма": selected_product,
                    "Кунлик миқдор": f"{daily_dose:.1f} г",
                    "Оқсил": f"{(daily_dose * prod_info['protein_per_100g'] / 100):.1f} г",
                    "Калория": f"{(daily_dose * prod_info['calories_per_100g'] / 100):.0f} ккал",
                    "ФА даражаси": f"{phe_level} мкмоль/л"
                }
                
                # Хисоботни кўрсатиш
                for key, value in daily_report.items():
                    st.info(f"**{key}:** {value}")
                
                # Қўшимча эслатма
                note = st.text_area("Кунлик эслатма", "Бола яхши ичди, иштаҳаси яхши", key="daily_note")
                daily_report["Эслатма"] = note
                
                # PDF юклаш
                report_text = json.dumps(daily_report, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Кунлик хисоботни юклаб олиш (JSON)",
                    data=report_text,
                    file_name=f"FKU_daily_report_{child_name}_{report_date.strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            # Ойлик хисобот
            st.markdown("### 📈 Ойлик статистика")
            
            month = st.selectbox("Ойни танланг", 
                                ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                                 "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
                                index=date.today().month - 1,
                                key="month_select")
            
            # Статистика маълумотлари
            months_data = {
                "Ой": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь"],
                "Ўртача ФА": [230, 240, 235, 245, 238, 242],
                "Огирлик (кг)": [11.8, 12.0, 12.2, 12.5, 12.7, 13.0],
                "Аралашма сарф (кг)": [3.5, 3.6, 3.7, 3.8, 3.9, 4.0]
            }
            
            monthly_df = pd.DataFrame(months_data)
            
            # График
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=monthly_df["Ой"],
                y=monthly_df["Ўртача ФА"],
                mode='lines+markers',
                name='ФА даражаси',
                line=dict(color='red', width=3)
            ))
            
            fig3.update_layout(
                title="Ойлар бўйича ФА даражаси",
                xaxis_title="Ой",
                yaxis_title="ФА (мкмоль/л)",
                height=300
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Харажат хисоби
            if 'selected_product' in locals() and selected_product:
                prod_info = products_db[selected_product]
                daily_dose = weight * prod_info['daily_dose_per_kg']
                monthly_cost = (daily_dose * 30 * prod_info['price_per_kg'] / 1000)
                yearly_cost = monthly_cost * 12
                
                st.metric("💵 Ойлик харажат", f"{monthly_cost:,.0f} сўм")
                st.metric("💰 Йиллик харажат", f"{yearly_cost:,.0f} сўм")
                
                # Excel хисобот
                excel_df = pd.DataFrame([{
                    "Сана": date.today().strftime("%Y-%m-%d"),
                    "Бола исми": child_name,
                    "Аралашма": selected_product,
                    "Кунлик миқдор (г)": daily_dose,
                    "Кунлик харажат": daily_dose * prod_info['price_per_kg'] / 1000,
                    "ФА даражаси": phe_level
                }])
                
                csv = excel_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📊 Excel хисоботни юклаб олиш (CSV)",
                    data=csv,
                    file_name=f"FKU_report_{child_name}_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # 5-таб: Заҳира бошқаруви
    with tab5:
        st.markdown('<h2 class="section-header">🛒 Озукавий Аралашмалар Заҳираси</h2>', unsafe_allow_html=True)
        
        # Заҳира маълумотлари
        stock_data = []
        total_cost = 0
        
        for product, stock in product_stock.items():
            if stock > 0:
                prod_info = products_db.get(product, {})
                price = prod_info.get('price_per_kg', 0)
                package_weight = 0.4  # Ҳар бир пакет 400г
                stock_kg = stock * package_weight
                stock_cost = stock_kg * price / 1000
                total_cost += stock_cost
                
                stock_data.append({
                    "Аралашма": product,
                    "Пакетлар сони": stock,
                    "Умумий огирлик (кг)": f"{stock_kg:.1f}",
                    "Қиммати (сўм)": f"{stock_cost:,.0f}",
                    "Статус": "✅ Етарли" if stock > 5 else "⚠️ Кам" if stock > 2 else "⛔ Тугаш"
                })
        
        if stock_data:
            stock_df = pd.DataFrame(stock_data)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(stock_df, use_container_width=True)
            
            with col2:
                st.metric("📦 Жами пакетлар", sum(product_stock.values()))
                st.metric("💰 Жами қиймат", f"{total_cost:,.0f} сўм")
                days_supply = sum(product_stock.values()) // 3
                st.metric("📅 Етарлилик", f"{days_supply} кун")
            
            # Заҳира таклифи
            st.markdown("### 📋 Яқинда тугаш таклифи:")
            
            low_stock = [p for p, s in product_stock.items() if s <= 3]
            if low_stock:
                for product in low_stock:
                    st.warning(f"**{product}** заҳираси кам: {product_stock[product]} пакет қолди")
            else:
                st.success("✅ Барча аралашмалар заҳираси етарли")
            
            # Буйртма қилиш
            st.markdown("### 🛍️ Янгӣ аралашма буйртмаси:")
            
            order_col1, order_col2, order_col3 = st.columns(3)
            
            with order_col1:
                order_product = st.selectbox("Аралашма", list(products_db.keys()), key="order_product")
            
            with order_col2:
                order_quantity = st.number_input("Пакетлар сони", 1, 100, 5, key="order_quantity")
            
            with order_col3:
                order_priority = st.selectbox("Зарбурият", ["Одатда", "Ошкор", "Жуда ошкор"], key="order_priority")
            
            if st.button("📝 Буйртмани яратиш", key="create_order"):
                st.success(f"✅ {order_quantity} та {order_product} пакети буйртма қилинди!")
                
                # Буйртма тафсилотлари
                prod_info = products_db[order_product]
                order_cost = order_quantity * 0.4 * prod_info['price_per_kg'] / 1000
                
                st.info(f"""
                **Буйртма тафсилотлари:**
                - Аралашма: {order_product}
                - Миқдор: {order_quantity} пакет ({order_quantity * 0.4:.1f} кг)
                - Нархи: {order_cost:,.0f} сўм
                - Етиб бориш муддати: 3-5 иш куни
                """)
    
    # 6-таб: Қўшимча маълумотлар
    with tab6:
        st.markdown('<h2 class="section-header">ℹ️ ФКУ Ҳақида Маълумот</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="info-card">
                <h4>ℹ️ Фенилкетонурия (ФКУ) ҳақида:</h4>
                <p>ФКУ - фенилаланин аминокислотасини метаболизмлаш бузилиши. Бунда фенилаланин организмда тўпланиб, мияга зарар етказиши мумкин.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📋 ФКУ ташхис қўйилганда эътибор бериш керак:")
            
            important_points = [
                "Фенилаланинга кам бўлган диета сақлаш",
                "Мунтазам лаборатория текширувлари",
                "Маҳсулот этикеткаларини диққат билан ўқиш",
                "Диетолог билан мулокотда бўлиш",
                "Жисмоний фаолликни унутмаслик"
            ]
            
            for point in important_points:
                st.markdown(f"✅ {point}")
        
        with col2:
            st.markdown("""
            <div class="warning-card">
                <h4>⚠️ Диққат қилиш керак бўлган озукалар:</h4>
                <p>Юқори фенилаланинга эга бўлган озукалардан қочиш керак:</p>
            </div>
            """, unsafe_allow_html=True)
            
            high_phe_foods = [
                "Гўшти ва балиқ маҳсулотлари",
                "Сут ва сут маҳсулотлари",
                "Тухум",
                "Дон маҳсулотлари (катта миқдорда)",
                "Йонғоқлар",
                "Баъзи мева-сабзавотлар"
            ]
            
            for food in high_phe_foods:
                st.markdown(f"❌ {food}")
            
            st.markdown("""
            <div class="success-card">
                <h4>✅ Истеъмол қилинадиган озукалар:</h4>
                <p>Фенилаланинга кам бўлган озукалар:</p>
            </div>
            """, unsafe_allow_html=True)
            
            low_phe_foods = [
                "Махсус ФКУ аралашмалари",
                "Кўпчилик мевалар",
                "Кўпчилик сабзавотлар",
                "Махсус ФКУ нон маҳсулотлари",
                "Қандолат маҳсулотлари (чекланган)"
            ]
            
            for food in low_phe_foods:
                st.markdown(f"✓ {food}")
        
        # Алоқа маълумотлари
        st.markdown("---")
        st.markdown("### 📞 Алоқа учун:")
        
        contact_col1, contact_col2, contact_col3 = st.columns(3)
        
        with contact_col1:
            st.info("**👨‍⚕️ Шифокор:**\nДр. Алиев А.\n📱 +998 90 123 45 67")
        
        with contact_col2:
            st.info("**🍎 Диетолог:**\nДиетолог Мадина\n📱 +998 91 234 56 78")
        
        with contact_col3:
            st.info("**🏥 Клиника:**\nБола шифокорлиги маркази\n📍 Тошкент, Миробод тумани")

# Streamlit Cloud тарзида ишлаш учун настройка
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Настройкалар")

# Тема
theme = st.sidebar.selectbox("Тема", ["Очиқ", "Қоронғи"], index=0)

# Тил (симуляция)
language = st.sidebar.selectbox("Тил", ["Ўзбекча", "Русча", "Инглизча"], index=0)

# Маълумотларни санглаш
if st.sidebar.button("♻️ Барча маълумотларни янгилаш"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Streamlit Cloud")
st.sidebar.info("""
Дастурни Streamlit Cloud-га жойлаштириш учун:

1. GitHub репозиторий яратинг
2. app.py файлини юкланг
3. streamlit.io га киринг
4. New app танланг
5. Репозиторийни танланг

Дастур автоматик равишда жойлашади!
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 1rem;">
    <p>© 2024 ФКУ Озукавий Аралашмалар Тизими | 
    <a href="#" style="color: #3B82F6;">Махфийлик сиёсати</a> | 
    <a href="#" style="color: #3B82F6;">Фойдаланиш шартлари</a></p>
    <p style="font-size: 0.9rem;">Бу дастур фақат маълумот олиш учун. Ҳар қандай тиббий қарор учун шифокорга мурожаат қилинг.</p>
</div>
""", unsafe_allow_html=True)

# requirements.txt файли учун тавсия
st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Зарур пакетлар")
st.sidebar.code("""
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
pillow>=10.0.0
""")
