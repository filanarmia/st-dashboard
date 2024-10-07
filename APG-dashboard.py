import pandas as pd
import streamlit as st
import plotly.express as px

# Load Excel data for both sheets
data_master = pd.read_excel("2024 Typologies Workshop registrations 30092024.xlsx", sheet_name="Registrations (Master list)")
data_private = pd.read_excel("2024 Typologies Workshop registrations 30092024.xlsx", sheet_name="Private sector nominees")


# Create tabs
tab1, tab2 = st.tabs(["Registrations (Master list)", "Private sector nominees"])

# -------- Tab 1: Registrations (Master list) --------
with tab1:
    st.title("Workshop Participant Dashboard (Master List)")

    # Total Number of Participants (using count of 'First Name')
    total_participants = data_master['First Name'].count()
    st.metric(label="Total Number of Participants", value=total_participants)

    # Handle missing values in 'Country' column
    data_master['Country'] = data_master['Country'].fillna('Unknown')

    # -- Filters --
    selected_country = st.selectbox("Filter by Country", options=["All"] + list(data_master['Country'].unique()))
    if selected_country != "All":
        data_master = data_master[data_master['Country'] == selected_country]

    selected_organization = st.selectbox("Filter by Organization", options=["All"] + list(data_master['Organisation'].unique()))
    if selected_organization != "All":
        data_master = data_master[data_master['Organisation'] == selected_organization]

    # -- Country Breakdown Chart with Plotly (Sorted by highest count) --
    st.title("Country Breakdown Chart")
    country_counts_chart = data_master['Country'].value_counts().reset_index()
    country_counts_chart.columns = ['Country', 'Count']
    country_counts_chart = country_counts_chart.sort_values(by='Count', ascending=False)

    fig_country_master = px.bar(
        country_counts_chart,
        x='Country',
        y='Count',
        title='Country Breakdown (Master List)',
        labels={'Country': 'Country', 'Count': 'Number of Participants'}
    )
    st.plotly_chart(fig_country_master)

    # -- Dietary Requirements Breakdown with Plotly (Sorted by highest count) --
    st.title("Dietary Requirements Breakdown")
    data_master['Dietary Requirements'] = data_master['Dietary Requirements'].fillna('None')
    dietary_counts_chart = data_master['Dietary Requirements'].value_counts().reset_index()
    dietary_counts_chart.columns = ['Dietary Requirements', 'Count']
    dietary_counts_chart = dietary_counts_chart.sort_values(by='Count', ascending=False)

    fig_dietary_master = px.bar(
        dietary_counts_chart,
        x='Dietary Requirements',
        y='Count',
        title='Dietary Requirements Breakdown (Master List)',
        labels={'Dietary Requirements': 'Dietary Requirements', 'Count': 'Number of Participants'}
    )
    st.plotly_chart(fig_dietary_master)

    # Session Participation Metrics
    st.title("Session Participation (Master List)")

    # Count participants in each stream/tour/dinner
    abuse_stream_count = data_master[data_master['Abuse of legal persons stream'] == 'Yes'].shape[0]
    cyber_stream_count = data_master[data_master['Cyber-enabled fraud/scams stream'] == 'Yes'].shape[0]
    museum_tour_count = data_master[data_master['Bank Negara Museum and Art Gallery tour'] == 'Yes'].shape[0]
    official_dinner_count = data_master[data_master['Official dinner'] == 'Yes'].shape[0]

    # Display metrics for sessions
    st.metric(label="Abuse of Legal Persons Stream", value=abuse_stream_count)
    st.metric(label="Cyber-enabled Fraud/Scams Stream", value=cyber_stream_count)
    st.metric(label="Bank Negara Museum and Art Gallery Tour", value=museum_tour_count)
    st.metric(label="Official Dinner", value=official_dinner_count)

    # Passport Number Metric
    passport_count = data_master[data_master['Passport Number'].notna()].shape[0]
    st.metric(label="Participants with Passport Number", value=passport_count)

    # Display filtered data
    st.write("Master List:")
    st.write(data_master[['First Name', 'Last Name', 'Country', 'Passport Number', 'Dietary Requirements', 'Cyber-enabled fraud/scams stream', 'Abuse of legal persons stream', 'Bank Negara Museum and Art Gallery tour', 'Official dinner']])

# -------- Tab 2: Private Sector Nominees --------
with tab2:
    st.title("Private Sector Nominees Dashboard")

    # Total Number of Participants (using 'No' column)
    total_participants_private = data_private['No'].count()
    st.metric(label="Total Number of Participants (Private Sector)", value=total_participants_private)

    # Breakdown by country (using 'Member' column), sorted by highest count
    country_counts_private = data_private['Member'].value_counts().reset_index()
    country_counts_private.columns = ['Member', 'Count']
    country_counts_private = country_counts_private.sort_values(by='Count', ascending=False)

    fig_country_private = px.bar(
        country_counts_private,
        x='Member',
        y='Count',
        title='Country Breakdown (Private Sector Nominees)',
        labels={'Member': 'Country', 'Count': 'Number of Participants'}
    )
    st.plotly_chart(fig_country_private)

    # Count participants in streams: 'Cyber-enabled fraud/scams stream' and 'Abuse of legal persons stream'
    cyber_stream_count = data_private[data_private['Cyber-enabled fraud/scams stream'] == 'Yes'].shape[0]
    abuse_stream_count = data_private[data_private['Abuse of legal persons stream'] == 'Yes'].shape[0]

    st.title("Session Participation (Private Sector Nominees)")
    st.metric(label="Cyber-enabled Fraud/Scams Stream", value=cyber_stream_count)
    st.metric(label="Abuse of Legal Persons Stream", value=abuse_stream_count)

    # Optional: Displaying data for verification
    st.write("Private Sector Nominees Data:")
    st.write(data_private[['First Name', 'Last Name', 'Member', 'Cyber-enabled fraud/scams stream', 'Abuse of legal persons stream']])

