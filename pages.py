from pymongo import MongoClient
import requests
import streamlit as st

# Connection to the MongoDB database
client = MongoClient("mongodb+srv://Adri64320:espasers@cluster0.k8kcqd9.mongodb.net/?retryWrites=true&w=majority")
db = client["allgameSection"]
db_teams = client['teams']
db_comp = client['competition']
collect_comp = db_comp['competition']
collect_teams = db_teams['teams']
inserted_document = db.ma_collection.find_one()
matchs = inserted_document.get("results", [])
db_game = client['each_game']
# Sélectionner la collection
collection = db_game['game']

def page1():
    st.image("logo/logoRugby.png",width=100)
    options_season = ["2024","2023","2022","2021","2020","2019","2018","2017","2016","2015","2014","2013"]
    selected_index_season = st.session_state.get('selected_index_season', 0)
    selected_season_str = st.selectbox('Select a season:', options_season, index=selected_index_season)
   

    filterSeason = f'Live Rugby API - TOP 14 Teams - {selected_season_str}'

    filter_season = {'meta.title': filterSeason}
    season_details = collect_comp.find_one(filter_season)
    if not season_details:
        url = f"https://rugby-live-data.p.rapidapi.com/teams/1230/{selected_season_str}"

        headers = {
            "X-RapidAPI-Key": "3eb55b2411mshedef4509e9deee0p14ced6jsn3c1a8f0dc791",
            "X-RapidAPI-Host": "rugby-live-data.p.rapidapi.com"
        }
        response_team = requests.get(url, headers=headers)
        season_details = response_team.json()
        if isinstance(season_details, dict):
                # Insert single document if data is a dictionary
            collect_comp.insert_one(season_details)
        elif isinstance(season_details, list):
                # Insert multiple documents if data is a list of dictionaries
            collect_comp.insert_many(season_details)
        else:
            print("Invalid JSON structure")
    st.session_state.season_details = season_details 
    options_teams = [f"{team['id']} - {team['name']}" for team in season_details['results']]
    selected_index_team = st.session_state.get('selected_index_team', 0)
    selected_team_str = st.selectbox('Select a match:', options_teams, index=selected_index_team)
    team_id = None
    team_name = None
    for i, team in enumerate(season_details['results']):
        team_str = f"{team['id']} - {team['name']}"
        if team_str == selected_team_str:
            team_id = team['id']
            team_name = team['name']
            
            # Store the selected index in session_state
            st.session_state.selected_index_team = i
            break



    #Probleme HEREEEEEEEE
    filterTeam = selected_season_str
    filter_team = {
        'results.0.season': filterTeam,
        '$and': [
            {
                '$or': [
                    {'results.0.home': team_name},
                    {'results.0.away': team_name}
                ]
            },
            {
                '$or': [
                    {'results.1.home': team_name},
                    {'results.1.away': team_name}
                ]
            }
        ]
    }
    team_details = collect_teams.find_one(filter_team)

    if not team_details:
        url = f"https://rugby-live-data.p.rapidapi.com/fixtures-by-team-by-season/{team_id}/{selected_season_str}"

        headers = {
            "X-RapidAPI-Key": "3eb55b2411mshedef4509e9deee0p14ced6jsn3c1a8f0dc791",
            "X-RapidAPI-Host": "rugby-live-data.p.rapidapi.com"
        }

        response_team_details = requests.get(url, headers=headers)
        team_details = response_team_details.json()
        
        
        if isinstance(team_details, dict):
                # Insert single document if data is a dictionary
            collect_teams.insert_one(team_details)
        elif isinstance(team_details, list):
                # Insert multiple documents if data is a list of dictionaries
            collect_teams.insert_many(team_details)
        else:
            print("Invalid JSON structure")
    
    st.session_state.team_details = team_details
    




    
   

    options = [f"{match['id']} - {match['home']} vs {match['away']} - {match['home_score']}:{match['away_score']} - {match['status']} - {match['season']}" for match in team_details['results']]
    selected_index = st.session_state.get('selected_index', 0)
    selected_match_str = st.selectbox('Select a match:', options, index=selected_index)
    # Find the match_id of the selected match
    match_id = None
    for i, match in enumerate(team_details['results']):
        match_str = f"{match['id']} - {match['home']} vs {match['away']} - {match['home_score']}:{match['away_score']} - {match['status']} - {match['season']}"
        if match_str == selected_match_str:
            match_id = match['id']
            
            # Store the selected index in session_state
            st.session_state.selected_index = i
            break
    # Retrieval and display of details of the selected match
    if match_id:

        filter = {'results.match.id': match_id}

        match_details = collection.find_one(filter)

        if not match_details:

            url = f"https://rugby-live-data.p.rapidapi.com/match/{match_id}"  
            headers = {
                "X-RapidAPI-Key": "3eb55b2411mshedef4509e9deee0p14ced6jsn3c1a8f0dc791",
                "X-RapidAPI-Host": "rugby-live-data.p.rapidapi.com"
            }    
            response = requests.get(url, headers=headers)
            match_details = response.json()
            if isinstance(match_details, dict):
                # Insert single document if data is a dictionary
                collection.insert_one(match_details)
            elif isinstance(match_details, list):
                # Insert multiple documents if data is a list of dictionaries
                collection.insert_many(match_details)
            else:
                print("Invalid JSON structure")
        


        st.session_state.match_details = match_details  # Store match_details in session state

        # Creation of columns
        col1, col2, col3, col4 = st.columns(4)

        # Display referee details in the leftmost column
        with col1:
            st.header('Referee Details')
            try:
                for referee in match_details.get('results', {}).get('referees', []):
                    st.text(f"Name: {referee['name']}")
                    st.text(f"Country: {referee['country']}")
                    st.text(f"Role: {referee['role']}")
                    st.text("----")
            except KeyError:
                st.text("Referee information not available")

        # Display match details in the middle column
        with col2:
            st.header('Home Team Details ')
            st.text(f"Score: {match_details['results']['match']['home_score']}")
            st.text(f"Team: {match_details['results']['match']['home_team']}")
            if st.button("Details of each home player"):
                st.session_state.page = 2
            if st.button("Details of home team"):
                st.session_state.page = 5
            # ... and so on for other details

        # Display match details in the right column
        with col3:
            st.header('Away Team Details')
            st.text(f"Score: {match_details['results']['match']['away_score']}")
            st.text(f"Team: {match_details['results']['match']['away_team']}")
            if st.button("Details of each away player"):
                st.session_state.page = 3
            if st.button("Details of away team"):
                st.session_state.page = 6
            # ... and so on for other details
        with col4:
            st.header('Match Details')
            st.text(f"Date: {match_details['results']['match']['date']}")
            st.text(f"Status: {match_details['results']['match']['status']}")
            st.text(f"Venue: {match_details['results']['match']['venue']}")
            st.text(f"Competition: {match_details['results']['match']['comp_name']}")
            if st.button("More match details"):
                st.session_state.page = 4
            if st.button("Comparison of the two teams"):
                st.session_state.page = 7
        
            
def page2():
    st.image("logo/logoRugby.png",width=100)
    match_details = st.session_state.match_details  # Access match_details from session state

    # Create a list of strings with position and name
    options = [f"{player['position']} : {player['name'] }" for player in match_details['results']['home']['teamsheet']]
    matchs_details = st.session_state.match_details 
    # Create a selectbox with the options list
    selected_player_str = st.selectbox('Select a player:', options)
    n = 0
    for player in matchs_details['results']['home']['teamsheet']:
        player_str = f"{player['position']} : {player['name']}"
        if player_str == selected_player_str:
            joueur_id = n
            break
        n += 1
        
    col1, col2, col3 = st.columns(3)
    with col1:

        st.subheader(f"Number and name of the player : {selected_player_str}")
        match_details = st.session_state.match_details
        st.write(f"Number of passes: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['passes']}")
        st.write(f"Number of tries: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['tries']}")
        st.write(f"Number of tackles: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['tackles']}")
        st.write(f"Number of missed_conversion_goals: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['missed_conversion_goals']}")
        dominant_tackles = match_details['results']['home']['teamsheet'][joueur_id]['match_stats'].get('dominant_tackles', 'Not available')
        st.write(f"Number of dominant_tackles: {dominant_tackles}")
        st.write(f"Number of penalties_conceded: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['penalties_conceded']}")
        st.write(f"Number of turnovers_conceded: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['turnovers_conceded']}")
        st.write(f"Number of rucks_lost: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['rucks_lost']}")
        st.write(f"Number of clean_breaks: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['clean_breaks']}")
    
    with col2:

        st.write(f"Number of rucks_won: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['rucks_won']}")
        st.write(f"Number of tackle_success: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['tackle_success']}")
        st.write(f"Number of defenders_beaten: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['defenders_beaten']}")
        st.write(f"Number of offload: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['offload']}")
        st.write(f"Number of drop_goals_converted: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['drop_goals_converted']}")
        st.write(f"Number of runs: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['runs']}")
        st.write(f"Number of metres: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['metres']}")
        st.write(f"Number of missed_penalty_goals: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['missed_penalty_goals']}")
        st.write(f"Number of points: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['points']}")
        st.write(f"Number of conversion_goals: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['conversion_goals']}")

    with col3:

        st.write(f"Number of try_assists: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['try_assists']}")
        st.write(f"Number of drop_goal_missed: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['drop_goal_missed']}")
        st.write(f"Number of lineouts_won: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['lineouts_won']}")
        st.write(f"Number of missed_tackles: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['missed_tackles']}")
        st.write(f"Number of penalty_goals: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['penalty_goals']}")
        st.write(f"Number of bad_passes: {match_details['results']['home']['teamsheet'][joueur_id]['match_stats']['bad_passes']}")
        
        if st.button("Go to Page 1"):
            st.session_state.page = 1

def page3():
    st.image("logo/logoRugby.png",width=100)

    match_details = st.session_state.match_details  # Access match_details from session state

    # Create a list of strings with position and name
    options = [f"{player['position']} : {player['name'] }" for player in match_details['results']['away']['teamsheet']]
    matchs_details = st.session_state.match_details 
    # Create a selectbox with the options list
    selected_player_str = st.selectbox('Select a player:', options)
    n = 0
    for player in matchs_details['results']['away']['teamsheet']:
        player_str = f"{player['position']} : {player['name']}"
        if player_str == selected_player_str:
            joueur_id = n
            break
        n += 1
    
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(f"Number and name of the player : {selected_player_str}")
        match_details = st.session_state.match_details
        st.write(f"Number of passes: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['passes']}")
        st.write(f"Number of tries: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['tries']}")
        st.write(f"Number of tackles: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['tackles']}")
        st.write(f"Number of missed_conversion_goals: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['missed_conversion_goals']}")
        dominant_tackles = match_details['results']['away']['teamsheet'][joueur_id]['match_stats'].get('dominant_tackles', 'Not available')
        st.write(f"Number of dominant_tackles: {dominant_tackles}")
        st.write(f"Number of penalties_conceded: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['penalties_conceded']}")
        st.write(f"Number of rucks_won: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['rucks_won']}")
        st.write(f"Number of tackle_success: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['tackle_success']}")
        st.write(f"Number of defenders_beaten: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['defenders_beaten']}")
    
    with col2:

        st.write(f"Number of offload: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['offload']}")
        st.write(f"Number of drop_goals_converted: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['drop_goals_converted']}")
        st.write(f"Number of runs: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['runs']}")
        st.write(f"Number of metres: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['metres']}")
        st.write(f"Number of missed_penalty_goals: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['missed_penalty_goals']}")
        st.write(f"Number of points: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['points']}")
        st.write(f"Number of conversion_goals: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['conversion_goals']}")
        st.write(f"Number of try_assists: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['try_assists']}")
        st.write(f"Number of drop_goal_missed: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['drop_goal_missed']}")
        st.write(f"Number of lineouts_won: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['lineouts_won']}")
    with col3:
        st.write(f"Number of missed_tackles: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['missed_tackles']}")
        st.write(f"Number of penalty_goals: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['penalty_goals']}")
        st.write(f"Number of bad_passes: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['bad_passes']}")
        st.write(f"Number of turnovers_conceded: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['turnovers_conceded']}")
        st.write(f"Number of rucks_lost: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['rucks_lost']}")
        st.write(f"Number of clean_breaks: {match_details['results']['away']['teamsheet'][joueur_id]['match_stats']['clean_breaks']}")   
        if st.button("Go to Page 1"):
            st.session_state.page = 1

def page4():
    if st.button("Go to Page 1"):
        st.session_state.page = 1
    st.image("logo/logoRugby.png",width=100)
    matchs_details = st.session_state.match_details 

    col1, col2 = st.columns(2)
    col1.subheader(f"HOME : {matchs_details['results']['match']['home_team']}")
    col2.subheader(f"AWAY : {matchs_details['results']['match']['away_team']}")

    # Sort events by time if they are not already sorted
    events = sorted(matchs_details['results']['events'], key=lambda x: x['time'])

    # Iterate through sorted events
    for event in events:
        if event['type'] == 'Substitution':
            if event['home_or_away'] == 'home':
                with col1:
                    st.markdown(f"""
                    <div style="border:2px solid grey; padding:10px; margin:5px; display: flex; justify-content: space-between;">
                        <span><strong>Type of event:</strong> {event['type']}</span>
                        <span><strong>Time:</strong> {event['time']}</span>
                        <span><strong>Name of the outgoing player:</strong> {event['player_1_name']} </span>
                        <span><strong>Name of the incoming player:</strong> {event['player_2']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("<br><br><br>", unsafe_allow_html=True)
            else:
                with col1:
                    st.markdown("<br><br><br>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="border:2px solid grey; padding:10px; margin:5px; display: flex; justify-content: space-between;">
                        <span><strong>Type of event:</strong> {event['type']}</span>
                        <span><strong>Time:</strong> {event['time']}</span>
                        <span><strong>Name of the outgoing player:</strong> {event['player_1_name']} </span>
                        <span><strong>Name of the incoming player:</strong> {event['player_2']}</span>

                    </div>
                    """, unsafe_allow_html=True)



        elif event['home_or_away'] == 'home':
            with col1:
                st.markdown(f"""
                <div style="border:2px solid grey; padding:10px; margin:5px; display: flex; justify-content: space-between;">
                    <span><strong>Type of event:</strong> {event['type']}</span>
                    <span><strong>Time:</strong> {event['time']}</span>
                    <span><strong>Name of the player:</strong> {event['player_1_name']}</span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
            
        else:
            with col1:
                st.markdown("<br><br>", unsafe_allow_html=True)  # Insert blank space in the home column
            with col2:
                st.markdown(f"""
                <div style="border:2px solid grey; padding:10px; margin:5px; display: flex; justify-content: space-between;">
                    <span><strong>Type of event:</strong> {event['type']}</span>
                    <span><strong>Time:</strong> {event['time']}</span>
                    <span><strong>Name of the player:</strong> {event['player_1_name']}</span>
                </div>
                """, unsafe_allow_html=True)

    
    
def page5():
    if st.button("Go to Page 1"):
        st.session_state.page = 1
    matchs_details = st.session_state.match_details 
    st.subheader(f"HOME : {matchs_details['results']['match']['home_team']}")

    st.image("logo/logoRugby.png",width=100)
    matchs_details = st.session_state.match_details 
    col1, col2, col3 = st.columns(3)

    with col1:
        for stats in matchs_details['results']['home']['team_stats']['attack']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['home']['team_stats']['defence']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['home']['team_stats']['discipline']:
            st.write(f"{stats['stat']} : {stats['value']}")
    with col2:
        for stats in matchs_details['results']['home']['team_stats']['kicking']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['home']['team_stats']['breakdown']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['home']['team_stats']['lineouts']:
            st.write(f"{stats['stat']} : {stats['value']}")
    with col3:
        for stats in matchs_details['results']['home']['team_stats']['scrums']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['home']['team_stats']['possession']:
            st.write(f"{stats['stat']} : {stats['value']}")








def page6():
    if st.button("Go to Page 1"):
        st.session_state.page = 1
    matchs_details = st.session_state.match_details 
    st.subheader(f"AWAY : {matchs_details['results']['match']['away_team']}")

    st.image("logo/logoRugby.png",width=100)
    matchs_details = st.session_state.match_details 
    col1, col2, col3 = st.columns(3)

    with col1:
        for stats in matchs_details['results']['away']['team_stats']['attack']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['away']['team_stats']['defence']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['away']['team_stats']['discipline']:
            st.write(f"{stats['stat']} : {stats['value']}")
    with col2:
        for stats in matchs_details['results']['away']['team_stats']['kicking']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['away']['team_stats']['breakdown']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['away']['team_stats']['lineouts']:
            st.write(f"{stats['stat']} : {stats['value']}")
    with col3:
        for stats in matchs_details['results']['away']['team_stats']['scrums']:
            st.write(f"{stats['stat']} : {stats['value']}")
        for stats in matchs_details['results']['away']['team_stats']['possession']:
            st.write(f"{stats['stat']} : {stats['value']}")



def page7():
    if st.button("Go to Page 1"):
        st.session_state.page = 1
    matchs_details = st.session_state.match_details
    st.image("logo/logoRugby.png", width=100)
    
    # Getting categories
    try:
        home_categories = set(matchs_details['results']['home']['team_stats'].keys())
    except KeyError:
        home_categories = set()
        st.write("No team stats available for home team")

    try:
        away_categories = set(matchs_details['results']['away']['team_stats'].keys())
    except KeyError:
        away_categories = set()
        st.write("No team stats available for away team")

    categories_to_compare = list(home_categories & away_categories)

    # Selectbox for categories
    selected_category = st.selectbox('Select a category:', categories_to_compare)
    
    col1, col2 = st.columns(2)
    col1.subheader(f"HOME: {matchs_details['results']['match']['home_team']} {matchs_details['results']['match']['home_score']}")
    col2.subheader(f"AWAY: {matchs_details['results']['match']['away_team']} {matchs_details['results']['match']['away_score']}")
    
    col1.subheader(selected_category.capitalize())
    col2.subheader(selected_category.capitalize())
    
    try:
        home_stats = {stat['stat']: float(stat['value']) for stat in matchs_details['results']['home']['team_stats'][selected_category]}
    except KeyError:
        home_stats = {}
        col1.write(f"No data available for {selected_category}")

    try:
        away_stats = {stat['stat']: float(stat['value']) for stat in matchs_details['results']['away']['team_stats'][selected_category]}
    except KeyError:
        away_stats = {}
        col2.write(f"No data available for {selected_category}")

    for stat, home_stat in home_stats.items():
        away_stat = away_stats.get(stat)
        
        if away_stat is not None:
            if selected_category == 'discipline' or stat.replace('_', ' ').capitalize() == "Carries not made gain line" or stat.replace('_', ' ').capitalize() == "Turnovers conceded" or stat.replace('_', ' ').capitalize() == "Missed tackles" or stat.replace('_', ' ').capitalize() == "Scrums lost" or stat.replace('_', ' ').capitalize() == "Missed conversion goals" or stat.replace('_', ' ').capitalize() == "Missed penalty goals" or stat.replace('_', ' ').capitalize() == "Rucks lost" or stat.replace('_', ' ').capitalize() == "Mauls lost" or stat.replace('_', ' ').capitalize() == "Lineouts lost":
                home_color = "red" if home_stat > away_stat else "green"
                away_color = "red" if away_stat > home_stat else "green"
            else:
                home_color = "green" if home_stat > away_stat else "red"
                away_color = "green" if away_stat > home_stat else "red"

            col1.markdown(f"""
            <div style="color:{home_color};">
                <h4>{stat.replace('_', ' ').capitalize()}</h4>
                <p>{home_stat}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col2.markdown(f"""
            <div style="color:{away_color};">
                <h4>{stat.replace('_', ' ').capitalize()}</h4>
                <p>{away_stat}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1.write(f"No data available for {stat}")
