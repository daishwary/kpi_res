import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="KPI Performance Dashboard", layout="wide")

# Function to load data
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    # Ensure required columns exist
    required_columns = ['Month', 'Team', 'Project', 'Lead', 'Actual Money', 'Target Money']
    if not all(col in df.columns for col in required_columns):
        st.error(f"Excel file must contain these columns: {', '.join(required_columns)}")
        st.stop()
    return df

# Upload file
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Convert Month to datetime
    df['Month'] = pd.to_datetime(df['Month'])
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_teams = st.sidebar.multiselect("Select Teams", options=df['Team'].unique())
    selected_projects = st.sidebar.multiselect("Select Projects", options=df['Project'].unique())
    selected_leads = st.sidebar.multiselect("Select Leads", options=df['Lead'].unique())
    
    # Apply filters
    if selected_teams:
        df = df[df['Team'].isin(selected_teams)]
    if selected_projects:
        df = df[df['Project'].isin(selected_projects)]
    if selected_leads:
        df = df[df['Lead'].isin(selected_leads)]
    
    # Calculate KPIs
    total_actual = df['Actual Money'].sum()
    total_target = df['Target Money'].sum()
    achievement_percentage = (total_actual / total_target * 100) if total_target != 0 else 0
    
    # Create three columns for KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Actual Money", value=f"${total_actual:,.2f}")
    with col2:
        st.metric(label="Total Target Money", value=f"${total_target:,.2f}")
    with col3:
        st.metric(label="Achievement Percentage", value=f"{achievement_percentage:.2f}%")
    
    # Monthly Performance Trend
    st.subheader("Monthly Performance Trend")
    monthly_data = df.groupby('Month').agg({'Actual Money': 'sum', 'Target Money': 'sum'}).reset_index()
    fig = px.line(monthly_data, x='Month', y=['Actual Money', 'Target Money'],
                  title="Actual vs Target Money by Month")
    st.plotly_chart(fig, use_container_width=True)
    
    # Team-wise Performance
    st.subheader("Team-wise Performance")
    team_data = df.groupby('Team').agg({'Actual Money': 'sum', 'Target Money': 'sum'}).reset_index()
    team_data['Achievement %'] = (team_data['Actual Money'] / team_data['Target Money'] * 100).round(2)
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(team_data.style.format({
            'Actual Money': "${:,.2f}",
            'Target Money': "${:,.2f}",
            'Achievement %': "{:.2f}%"
        }), height=300)
    
    with col2:
        fig = px.bar(team_data, x='Team', y=['Actual Money', 'Target Money'],
                      barmode='group', title="Team-wise Actual vs Target")
        st.plotly_chart(fig, use_container_width=True)
    
    # Project-wise Analysis
    st.subheader("Project-wise Analysis")
    project_data = df.groupby('Project').agg({'Actual Money': 'sum', 'Target Money': 'sum'}).reset_index()
    project_data['Achievement %'] = (project_data['Actual Money'] / project_data['Target Money'] * 100).round(2)
    
    fig = px.bar(project_data, x='Project', y='Achievement %',
                 title="Project-wise Achievement Percentage")
    st.plotly_chart(fig, use_container_width=True)
    
    # Lead-wise Performance
    st.subheader("Lead-wise Performance")
    lead_data = df.groupby('Lead').agg({'Actual Money': 'sum', 'Target Money': 'sum'}).reset_index()
    lead_data['Achievement %'] = (lead_data['Actual Money'] / lead_data['Target Money'] * 100).round(2)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(lead_data, names='Lead', values='Actual Money',
                     title="Lead-wise Actual Money Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(lead_data, x='Target Money', y='Actual Money', color='Lead',
                         size='Actual Money', title="Actual vs Target by Lead")
        st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Data")
        st.dataframe(df.style.format({
            'Actual Money': "${:,.2f}",
            'Target Money': "${:,.2f}"
        }), use_container_width=True)

else:
    st.info("Please upload an Excel file through the sidebar to get started")
