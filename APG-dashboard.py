import pandas as pd 
import streamlit as st
import plotly.express as px



# Define a simple username and password (in a real app, use proper authentication)
USERNAME = "apgdashie"
PASSWORD = "jpkp2024@"

# Create a function to display the login page
def login():
    st.title("Login")

    # Create a form for login
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        # Check if login button is pressed
        if login_button:
            if username == USERNAME and password == PASSWORD:
                # Store login status in session_state
                st.session_state["logged_in"] = True
                st.success("Logged in successfully! Please click on the Login button again to continue.")
            else:
                st.error("Incorrect username or password")

# Define a function to display the main dashboard (after successful login)
def show_dashboard():
    # Load Excel data for both sheets
    data_master = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Public Sector")
    data_private = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Private sector nominees")
    data_presenters = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Presenters")
    data_master_list = pd.read_excel("2024 Typologies Workshop registrations v2.xlsx", sheet_name="Master List")

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

        # Display the total number of participants (Filtered) side by side
        col1, col2, col3 = st.columns(3)  # Create 3 columns

        # Display metrics in each column with partial bold text
        with col1:
            st.markdown("Total Number of **Participants**")
            st.metric(label="Participants", value=total_filtered_participants, label_visibility="collapsed")

        with col2:
            st.markdown("Total Number of **Museum Tour**")
            st.metric(label="Museum Tour", value=total_museum_tour_participants, label_visibility="collapsed")

        with col3:
            st.markdown("Total Number of **Official Dinner**")
            st.metric(label="Official Dinner", value=total_dinner_participants, label_visibility="collapsed")

        # -------- Dietary Requirements Breakdown --------
        # Filter out 'None', 'Halal', and empty values from 'Dietary Requirements'
        filtered_dietary_data = data_master_list[
            (data_master_list['Dietary Requirements'].notna()) & 
            (data_master_list['Dietary Requirements'] != 'None') & 
            (data_master_list['Dietary Requirements'] != 'Halal')
        ]

        # Process the filtered 'Dietary Requirements' column
        dietary_counts = filtered_dietary_data['Dietary Requirements'].value_counts().reset_index()
        dietary_counts.columns = ['Dietary Requirements', 'Count']

        # Create a pie chart for dietary requirements using Plotly
        fig_dietary = px.pie(
            dietary_counts, 
            names='Dietary Requirements', 
            values='Count', 
            title='Dietary Requirements Breakdown',
            hole=0.4  # Donut chart style
        )

        # Create two columns: one for the pie chart and one for the table with numbers
        col1, col2 = st.columns([2, 1])  # Adjust column sizes if necessary

        # Display the pie chart in the first column
        with col1:
            st.plotly_chart(fig_dietary)

        # Display the dietary requirement counts as a table in the second column
        with col2:
            st.write("Dietary Requirements Count")
            st.table(dietary_counts)

        # -------- Grouped Bar Chart for Stream Participation --------
        st.subheader("Stream Participation")

        # Count the participants for "Abuse of legal persons stream" (from both the master list and filtered presenters)
        abuse_count_master = data_master_list[data_master_list['Abuse of legal persons stream'] == 'Yes'].shape[0]
        abuse_count_presenters = filtered_presenters[filtered_presenters['Stream'].str.contains('Abuse of legal persons', na=False)].shape[0]
        abuse_total_count = abuse_count_master + abuse_count_presenters

        # Count the participants for "Cyber-enabled fraud/scams stream" (from both the master list and filtered presenters)
        cyber_count_master = data_master_list[data_master_list['Cyber-enabled fraud/scams stream'] == 'Yes'].shape[0]
        cyber_count_presenters = filtered_presenters[filtered_presenters['Stream'].str.contains('Cyber enabled fraud/scams', na=False)].shape[0]
        cyber_total_count = cyber_count_master + cyber_count_presenters

        # Count "OC Meeting" where "Sector" is "Public"
        oc_meeting_count = data_master_list[data_master_list['Sector'] == 'Public'].shape[0]

        # Count "Plenary session" based on "Public" in "Sector" and check in the presenters
        plenary_count = (
            data_master_list[data_master_list['Sector'] == 'Public'].shape[0] +  # Count from master list
            filtered_presenters[filtered_presenters['Stream'].str.contains('Plenary session', na=False)].shape[0]  # Count from presenters
        )

        # Prepare the data for the grouped bar chart
        grouped_data = pd.DataFrame({
            'Stream': ['Abuse of Legal Persons', 'Cyber-enabled Fraud/Scams', 'OC Meeting', 'Plenary Session'],
            'Participants': [abuse_total_count, cyber_total_count, oc_meeting_count, plenary_count]
        })

        # Create the grouped bar chart using Plotly
        fig_grouped_bar = px.bar(
            grouped_data,
            x='Stream',
            y='Participants',
            title='Participants by Stream',
            labels={'Stream': 'Stream', 'Participants': 'Number of Participants'},
            color='Stream',
            text='Participants'  # Show the participant numbers on top of the bars
        )

        # Display the bar chart
        st.plotly_chart(fig_grouped_bar)


    # -------- Tab 2: Registrations (Master list) --------
    with tab2:
        st.title("Public Participant Dashboard")

        # Total Number of Participants (using count of 'First Name')
        total_participants = data_master['No'].count()
        st.metric(label="Total Number of Participants (Public Sector)", value=total_participants)

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
        st.title("Country Breakdown")
        country_counts_chart = data_master['Country'].value_counts().reset_index()
        country_counts_chart.columns = ['Country', 'Count']
        country_counts_chart = country_counts_chart.sort_values(by='Count', ascending=False)

        fig_country_master = px.bar(
            country_counts_chart,
            x='Country',
            y='Count',
            title='Country',
            labels={'Country': 'Country', 'Count': 'Number of Participants'}
        )
        st.plotly_chart(fig_country_master)

        # -- Dietary Requirements Breakdown with Plotly (Sorted by highest count) --
        st.title("Dietary Requirements Breakdown")
        data_master['Dietary Requirements'] = data_master['Dietary Requirements'].fillna('None')
        dietary_filtered = data_master[data_master['Dietary Requirements'] != 'None']
        dietary_counts_chart = dietary_filtered['Dietary Requirements'].value_counts().reset_index()
        dietary_counts_chart.columns = ['Dietary Requirements', 'Count']
        dietary_counts_chart = dietary_counts_chart.sort_values(by='Count', ascending=False)

        fig_dietary_master = px.bar(
            dietary_counts_chart,
            x='Dietary Requirements',
            y='Count',
            title='Dietary Requirements',
            labels={'Dietary Requirements': 'Dietary Requirements', 'Count': 'Number of Participants'}
        )
        st.plotly_chart(fig_dietary_master)

        # Session Participation Metrics
        st.title("Session Participation")

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
        st.title("Private Sector Dashboard")

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
            title='Country Breakdown',
            labels={'Member': 'Country', 'Count': 'Number of Participants'}
        )
        st.plotly_chart(fig_country_private)

        # -- Dietary Requirements Breakdown with Plotly (Sorted by highest count) --
        st.title("Dietary Requirements Breakdown")
        data_private['Dietary requirements'] = data_private['Dietary requirements'].fillna('None')
        dietary_filtered = data_private[data_private['Dietary requirements'] != 'None']
        dietary_counts_chart = dietary_filtered['Dietary requirements'].value_counts().reset_index()
        dietary_counts_chart.columns = ['Dietary Requirements', 'Count']
        dietary_counts_chart = dietary_counts_chart.sort_values(by='Count', ascending=False)

        fig_dietary_master = px.bar(
            dietary_counts_chart,
            x='Dietary Requirements',
            y='Count',
            title='Dietary Requirements',
            labels={'Dietary Requirements': 'Dietary Requirements', 'Count': 'Number of Participants'}
        )
        st.plotly_chart(fig_dietary_master)

        # Count participants in streams: 'Cyber-enabled fraud/scams stream' and 'Abuse of legal persons stream'
        cyber_stream_count = data_private[data_private['Cyber-enabled fraud/scams stream'] == 'Yes'].shape[0]
        abuse_stream_count = data_private[data_private['Abuse of legal persons stream'] == 'Yes'].shape[0]
        museum_tour_count = data_private[data_private['Bank Negara Museum and Art Gallery tour'] == 'Yes'].shape[0]
        official_dinner_count = data_private[data_private['Official dinner'] == 'Yes'].shape[0]

        st.title("Session Participation")
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

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# If the user is logged in, show the dashboard; otherwise, show the login page
if st.session_state["logged_in"]:
    show_dashboard()
else:
    login()

