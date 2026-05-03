import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
from datetime import datetime, date
import calendar
import io
import os

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# IMPORTANT: Get API key from environment variable (NOT hardcoded)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Only create client if API key exists
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None
    st.warning("⚠️ GROQ_API_KEY not found. AI features will be disabled. Please add your API key to environment variables.")

st.set_page_config(page_title="Metricly", layout="wide", page_icon="📊")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Add logo
    st.image("logo.png", width=160)
    
    st.markdown("<div class='nav-label'>MENU</div>", unsafe_allow_html=True)
    page = st.radio("", ["Dashboard", "Campaigns", "Calendar"], label_visibility="collapsed")

    st.markdown("<div class='nav-label'>QUICK STATS</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='sidebar-stat'>
            <span>Active Campaigns</span>
            <span class='stat-val'>3</span>
        </div>
        <div class='sidebar-stat'>
            <span>Posts Scheduled</span>
            <span class='stat-val'>12</span>
        </div>
        <div class='sidebar-stat'>
            <span>Avg Engagement</span>
            <span class='stat-val'>8.4%</span>
        </div>
    """, unsafe_allow_html=True)

# ── Dashboard Page ────────────────────────────────────────────────────────────
if page == "Dashboard":
    st.markdown("""
        <div class='page-header'>
            <div>
                <h1>Welcome to Metricly</h1>
                <p class='hub-title'>Your Marketing Intelligence Hub</p>
                <p class='slogan'>Track Smarter. Grow Faster. Powered by AI.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CSV Template Download
    template_df = pd.DataFrame({
        "Post": ["Reel 1", "Post 2", "Reel 3", "Story 1", "Reel 4"],
        "Likes": [1200, 800, 1500, 600, 2000],
        "Shares": [200, 100, 300, 80, 400],
        "Saves": [150, 50, 200, 30, 250]
    })
    buffer = io.BytesIO()
    template_df.to_csv(buffer, index=False)
    buffer.seek(0)

    col_up, col_dl = st.columns([3, 1])
    with col_dl:
        st.download_button(
            label="Download CSV Template",
            data=buffer,
            file_name="metricly_template.csv",
            mime="text/csv"
        )

    uploaded_file = st.file_uploader("Upload Marketing Data (CSV)", type="csv", label_visibility="collapsed")

    if not uploaded_file:
        st.markdown("""
            <div class='upload-zone'>
                <div class='upload-icon'>+</div>
                <h3>Drop your CSV here</h3>
                <p>Download the template above, fill it in, and upload it here</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        df = pd.read_csv(uploaded_file)
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        label_col = df.columns[0]

        # ── Metric Cards ──
        st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)
        cols = st.columns(len(numeric_cols))
        colors = ["#db97ff", "#f472b6", "#a78bfa", "#c084fc"]
        for i, col in enumerate(numeric_cols):
            total = int(df[col].sum())
            best = df.loc[df[col].idxmax(), label_col]
            color = colors[i % len(colors)]
            with cols[i]:
                st.markdown(f"""
                    <div class='metric-card' style='border-top: 4px solid {color}'>
                        <div class='metric-label'>{col}</div>
                        <div class='metric-value' style='color:{color}'>{total:,}</div>
                        <div class='metric-sub'>Best: {best}</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts Row ──
        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown("<div class='card-title'>Performance Overview</div>", unsafe_allow_html=True)
            fig = go.Figure()
            chart_colors = ["#db97ff", "#f472b6", "#a78bfa", "#c084fc"]
            for i, col in enumerate(numeric_cols):
                fig.add_trace(go.Scatter(
                    x=df[label_col], y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=chart_colors[i % len(chart_colors)], width=3),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(219, 151, 255, 0.08)'
                ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9b7daa', family='DM Sans'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=0, r=0, t=30, b=0),
                height=280
            )
            fig.update_xaxes(showgrid=False, showline=False)
            fig.update_yaxes(showgrid=True, gridcolor='#e9d5ff', showline=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("<div class='card-title'>Content Mix</div>", unsafe_allow_html=True)
            if len(numeric_cols) > 0:
                pie_col = numeric_cols[0]
                fig2 = px.pie(
                    df, values=pie_col, names=label_col,
                    color_discrete_sequence=["#db97ff", "#410061", "#a78bfa", "#c084fc", "#f472b6"]
                )
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#9b7daa'),
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=280,
                    showlegend=True,
                    legend=dict(orientation="v", x=0.7)
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label', hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)

        # ── Overall Progress + Bar Chart ──
        col3, col4 = st.columns([2, 3])

        with col3:
            st.markdown("<div class='card-title'>Overall Progress</div>", unsafe_allow_html=True)
            if len(numeric_cols) > 0:
                max_possible = df[numeric_cols[0]].max() * len(df) * len(numeric_cols)
                actual = sum(df[c].sum() for c in numeric_cols)
                progress_pct = min(int((actual / max_possible) * 100) if max_possible > 0 else 0, 100)
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=progress_pct,
                    number={'suffix': '%', 'font': {'size': 36, 'color': '#410061'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#e9d5ff'},
                        'bar': {'color': '#410061', 'thickness': 0.3},
                        'bgcolor': '#f9f0ff',
                        'borderwidth': 0,
                        'steps': [
                            {'range': [0, 50], 'color': '#f3e8ff'},
                            {'range': [50, 80], 'color': '#e9d5ff'},
                            {'range': [80, 100], 'color': '#db97ff'}
                        ],
                        'threshold': {
                            'line': {'color': '#db97ff', 'width': 4},
                            'thickness': 0.75,
                            'value': progress_pct
                        }
                    }
                ))
                fig3.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#9b7daa'),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=240
                )
                st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown("<div class='card-title'>Top Performing Posts</div>", unsafe_allow_html=True)
            if len(numeric_cols) > 0:
                sort_col = numeric_cols[0]
                df_sorted = df.sort_values(sort_col, ascending=True)
                fig4 = px.bar(
                    df_sorted, x=sort_col, y=label_col,
                    orientation='h',
                    color=sort_col,
                    color_continuous_scale=["#f3e8ff", "#410061"]
                )
                fig4.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#9b7daa'),
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=240,
                    coloraxis_showscale=False
                )
                fig4.update_xaxes(showgrid=True, gridcolor='#e9d5ff')
                fig4.update_yaxes(showgrid=False)
                st.plotly_chart(fig4, use_container_width=True)

        # ── Data Table ──
        st.markdown("<div class='card-title'>Raw Data</div>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── AI Analyze ──
        st.markdown("<br>", unsafe_allow_html=True)
        if client and st.button("Analyze Data with AI"):
            with st.spinner("Analyzing your data..."):
                prompt = f"""
                Analyze this marketing data and give:
                1. Key insights
                2. Best performing content
                3. What can be improved
                Data:
                {df.to_string()}
                """
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(f"""
                    <div class='insight-box'>
                        <h3>AI Insights</h3>
                        <p>{response.choices[0].message.content.replace('*', '').replace('#', '').replace(chr(10), '<br>')}</p>
                    </div>
                """, unsafe_allow_html=True)
        elif not client:
            st.info("💡 Add your GROQ_API_KEY to enable AI insights")

# ── Campaigns Page ────────────────────────────────────────────────────────────
elif page == "Campaigns":
    st.markdown("""
        <div class='page-header'>
            <div>
                <h1>Campaign Generator</h1>
                <p class='subtitle'>Let AI build your full marketing strategy</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    goal = st.text_input("What is your campaign goal?", placeholder="e.g. Grow Instagram for a fashion brand in Dubai")

    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("Platform", ["Instagram", "TikTok", "LinkedIn", "Twitter/X", "All Platforms"])
    with col2:
        duration = st.selectbox("Campaign Duration", ["1 Week", "2 Weeks", "1 Month", "3 Months"])

    if client and st.button("Generate Campaign"):
        with st.spinner("Building your strategy..."):
            prompt = f"""
            Create a detailed marketing campaign for:
            Goal: {goal}
            Platform: {platform}
            Duration: {duration}

            Include:
            - Target audience profile
            - Content ideas (at least 5 specific ideas)
            - Posting schedule
            - Growth strategy
            - KPIs to track
            - Hashtag strategy
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(f"""
                <div class='insight-box'>
                    <h3>Your Campaign Strategy</h3>
                    <p>{response.choices[0].message.content.replace('*', '').replace('#', '').replace(chr(10), '<br>')}</p>
                </div>
            """, unsafe_allow_html=True)
    elif not client:
        st.info("💡 Add your GROQ_API_KEY to generate campaigns")

# ── Calendar Page ─────────────────────────────────────────────────────────────
elif page == "Calendar":
    st.markdown("""
        <div class='page-header'>
            <div>
                <h1>Marketing Calendar</h1>
                <p class='subtitle'>Track your campaigns and deadlines</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        selected_month = st.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month - 1)
        selected_year = st.number_input("Year", min_value=2024, max_value=2030, value=datetime.now().year)

    month_num = list(calendar.month_name).index(selected_month)
    cal = calendar.monthcalendar(selected_year, month_num)
    today = date.today()

    st.markdown("<div class='card-title'>Add Deadline or Campaign</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        event_name = st.text_input("Event Name", placeholder="e.g. Launch Reel")
    with c2:
        event_date = st.date_input("Date")
    with c3:
        event_type = st.selectbox("Type", ["Post", "Reel", "Campaign Launch", "Review", "Deadline"])

    if "events" not in st.session_state:
        st.session_state.events = []

    if st.button("Add to Calendar"):
        st.session_state.events.append({
            "name": event_name,
            "date": event_date,
            "type": event_type
        })
        st.success(f"Added: {event_name} on {event_date}")

    st.markdown("<div class='card-title'>" + selected_month + " " + str(selected_year) + "</div>", unsafe_allow_html=True)

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    header_html = "<div class='cal-grid'>"
    for d in days:
        header_html += f"<div class='cal-header'>{d}</div>"

    for week in cal:
        for day in week:
            if day == 0:
                header_html += "<div class='cal-cell empty'></div>"
            else:
                current = date(selected_year, month_num, day)
                is_today = current == today
                events_today = [e for e in st.session_state.events if e["date"] == current]
                event_html = "".join([f"<div class='cal-event'>{e['type']}: {e['name']}</div>" for e in events_today])
                today_class = "cal-today" if is_today else ""
                header_html += f"<div class='cal-cell {today_class}'><span class='cal-day'>{day}</span>{event_html}</div>"

    header_html += "</div>"
    st.markdown(header_html, unsafe_allow_html=True)

    if st.session_state.events:
        st.markdown("<div class='card-title'>Upcoming Events</div>", unsafe_allow_html=True)
        events_df = pd.DataFrame(st.session_state.events)
        events_df = events_df.sort_values("date")
        st.dataframe(events_df, use_container_width=True, hide_index=True)
