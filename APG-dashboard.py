import pandas as pd 
import streamlit as st
import plotly.express as px

# Load Excel data for both sheets
data_master = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Public Sector")
data_private = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Private sector nominees")
data_presenters = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Presenters")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Master (Stats)", "Public sector", "Private sector", "Presenters"])

# -------- Tab 1: Stats --------
with tab1:
    st.title("Overall Stats Dashboard")

    # Filter 'Registered on website' where the value is 'No' or empty (NaN)
    filtered_presenters = data_presenters[(data_presenters['Registered on website'] == 'No') | (data_presenters['Registered on website'].isna())]
    
    # Combine total participants from all sheets, applying the filter for 'Registered on website' == 'No' or empty
    total_filtered_master = data_master['No'].count()  # Master list doesn't have a registered column
    total_filtered_private = data_private['No'].count()  # Assuming Private Sector doesn't have a registered column

    # For presenters, we take the unique count of 'No' column from the filtered presenters
    total_filtered_presenters = filtered_presenters['No'].nunique()

    # Sum up all the filtered totals
    total_filtered_participants = total_filtered_master + total_filtered_private + total_filtered_presenters

    museum_tour_count_public = data_master[data_master['Bank Negara Museum and Art Gallery tour'] == 'Yes'].shape[0]
    official_dinner_count_public = data_master[data_master['Official dinner'] == 'Yes'].shape[0]

    museum_tour_count_private = data_private[data_private['Bank Negara Museum and Art Gallery tour'] == 'Yes'].shape[0]
    official_dinner_count_private = data_private[data_private['Official dinner'] == 'Yes'].shape[0]

    total_museum_tour_participants = museum_tour_count_public + museum_tour_count_private
    total_dinner_participants = official_dinner_count_public + official_dinner_count_private

    # Display the total number of participants (Filtered)
    st.metric(label="Total Number of Participants", value=total_filtered_participants)
    st.metric(label="Total Number of Museum Tour", value=total_museum_tour_participants)
    st.metric(label="Total Number of Official Dinner", value=total_dinner_participants)

    # -------- Breakdown by Day and Stream --------
    
    # Function to calculate total participants per day and stream (without plenary session for master and private sector)
    def calculate_participants_for_stream_day(stream_name, day_value):
        if stream_name == 'Plenary session':
            # Use pre-computed plenary session value for master list and private sector
            master_participants = data_master.shape[0]  # Assuming this represents plenary participants from master list
            private_participants = 0  # Assuming no plenary session from private sector, adjust if needed
        elif stream_name == 'OC Meeting' and day_value == 'Day 1':
            # All participants from the master list attend the OC Meeting
            master_participants = data_master.shape[0]
            private_participants = 0  # No need to include private sector or presenters for OC Meeting
        else:
            # From Registrations (Master List) for other streams
            master_participants = data_master[data_master[f'{stream_name} stream'] == 'Yes'].shape[0]
            # From Private Sector for other streams
            private_participants = data_private[data_private[f'{stream_name} stream'] == 'Yes'].shape[0]

        # From Presenters, filter by stream, day, and 'Registered on website'
        presenter_participants = filtered_presenters[
            (filtered_presenters['Stream'] == stream_name) & 
            (filtered_presenters['Day'] == day_value)
        ]['No'].nunique()

        # Return the sum of all participants from the three sources
        return master_participants + private_participants + presenter_participants

    # ---- Table for Day 1 ----
    st.subheader("Day 1 Breakdown (Table)")
    plenary_day1 = data_master.shape[0] + filtered_presenters[(filtered_presenters['Stream'] == 'Plenary session') & 
                    (filtered_presenters['Day'] == 'Day 1')].shape[0]
    oc_meeting_day1 = data_master.shape[0]  # All participants in the Master List
    abuse_day1 = calculate_participants_for_stream_day('Abuse of legal persons', 'Day 1')
    cyber_day1 = calculate_participants_for_stream_day('Cyber-enabled fraud/scams', 'Day 1')

    day1_data = {
        'Session': ['Plenary Session', 'OC Meeting', 'Abuse of Legal Persons', 'Cyber-enabled Fraud/Scams'],
        'Participants': [plenary_day1, oc_meeting_day1, abuse_day1, cyber_day1]
    }
    st.table(pd.DataFrame(day1_data))

    # ---- Table for Day 2 ----
    st.subheader("Day 2 Breakdown (Table)")
    abuse_day2 = calculate_participants_for_stream_day('Abuse of legal persons', 'Day 2')
    cyber_day2 = calculate_participants_for_stream_day('Cyber-enabled fraud/scams', 'Day 2')

    day2_data = {
        'Session': ['Abuse of Legal Persons', 'Cyber-enabled Fraud/Scams'],
        'Participants': [abuse_day2, cyber_day2]
    }
    st.table(pd.DataFrame(day2_data))

    # ---- Table for Day 3 ----
    st.subheader("Day 3 Breakdown (Table)")
    plenary_day3 = data_master.shape[0] + filtered_presenters[(filtered_presenters['Stream'] == 'Plenary session') & 
                    (filtered_presenters['Day'] == 'Day 3')].shape[0]
    abuse_day3 = calculate_participants_for_stream_day('Abuse of legal persons', 'Day 3')
    cyber_day3 = calculate_participants_for_stream_day('Cyber-enabled fraud/scams', 'Day 3')

    day3_data = {
        'Session': ['Plenary Session', 'Abuse of Legal Persons', 'Cyber-enabled Fraud/Scams'],
        'Participants': [plenary_day3, abuse_day3, cyber_day3]
    }
    st.table(pd.DataFrame(day3_data))

    # -------- Generate bar chart for day-stream breakdown --------
    st.subheader("Participants Breakdown by Day and Stream (Bar Chart)")
    def get_day_stream_data():
        day_stream_data = []
        for day in ['Day 1', 'Day 2', 'Day 3']:
            # Include Plenary session for Day 1 and Day 3, and OC Meeting only for Day 1
            if day == 'Day 1':
                streams = ['Plenary session', 'Abuse of legal persons', 'Cyber-enabled fraud/scams', 'OC Meeting']
            elif day == 'Day 3':
                streams = ['Plenary session', 'Abuse of legal persons', 'Cyber-enabled fraud/scams']
            else:
                streams = ['Abuse of legal persons', 'Cyber-enabled fraud/scams']  # No plenary session for Day 2

            for stream in streams:
                total_participants = calculate_participants_for_stream_day(stream, day)
                day_stream_data.append({'Day': day, 'Stream': stream, 'Participants': total_participants})
        return pd.DataFrame(day_stream_data)

    # Generate bar chart for day-stream breakdown
    day_stream_data = get_day_stream_data()
    fig_day_stream = px.bar(
        day_stream_data,
        x='Day',
        y='Participants',
        color='Stream',
        title='Participants by Day and Stream',
        labels={'Day': 'Day', 'Participants': 'Number of Participants', 'Stream': 'Stream'},
        category_orders={"Day": ['Day 1', 'Day 2', 'Day 3']}  # Ensure correct order of days
    )
    st.plotly_chart(fig_day_stream)

# -------- Tab 2: Registrations (Master list) --------
with tab2:
    st.title("Public Participant Dashboard")

    # Total Number of Participants (using count of 'First Name')
    total_participants = data_master['No'].count()
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
    
# -------- Tab 3: Private Sector Nominees --------
with tab3:
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
    museum_tour_count = data_private[data_private['Bank Negara Museum and Art Gallery tour'] == 'Yes'].shape[0]
    official_dinner_count = data_private[data_private['Official dinner'] == 'Yes'].shape[0]

    st.title("Session Participation (Private Sector Nominees)")
    st.metric(label="Cyber-enabled Fraud/Scams Stream", value=cyber_stream_count)
    st.metric(label="Abuse of Legal Persons Stream", value=abuse_stream_count)
    st.metric(label="Bank Negara Museum and Art Gallery Tour", value=museum_tour_count)
    st.metric(label="Official Dinner", value=official_dinner_count)


# -------- Tab 4: Presenters --------
with tab4:
    st.title("Presenters Dashboard")

    # Count the number of unique presenters based on 'Name' column
    total_presenters = data_presenters['No'].nunique()
    st.metric(label="Total Number of Presenters", value=total_presenters)

    # Count by Role (Facilitator, Presenter, Panelist, Moderator, Blank)
    role_counts = data_presenters['Role'].fillna('Blank').value_counts().reset_index()
    role_counts.columns = ['Role', 'Count']
    
    # Plot the role breakdown
    fig_role = px.bar(
        role_counts,
        x='Role',
        y='Count',
        title='Role Breakdown',
        labels={'Role': 'Role', 'Count': 'Number of Presenters'}
    )
    st.plotly_chart(fig_role)

    # Presenters breakdown by Day and Stream (e.g., Day 1 by Stream)
    st.title("Presenters Breakdown by Day and Stream")
    day_stream_counts = data_presenters.groupby(['Day', 'Stream']).size().reset_index(name='Count')
    
    fig_day_stream = px.bar(
        day_stream_counts,
        x='Day',
        y='Count',
        color='Stream',
        title='Presenters by Day and Stream',
        labels={'Day': 'Day', 'Count': 'Number of Presenters', 'Stream': 'Stream'}
    )
    st.plotly_chart(fig_day_stream)
