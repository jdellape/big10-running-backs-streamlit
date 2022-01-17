#Import libraries I need
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

#This code only for allowing tooltips to display when in full screen mode (https://discuss.streamlit.io/t/tool-tips-in-fullscreen-mode-for-charts/6800/8)
st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',
             unsafe_allow_html=True)

#Describe the data app
st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Big_Ten_Conference_logo.svg/220px-Big_Ten_Conference_logo.svg.png')
st.title('Running Back Carries by Yards Gained')

st.markdown("I'm a data analyst and also a big Penn State football fan. Our fanbase griped a lot this season about our running game. My Question: How frustrating is our running game relative to other teams? So I grabbed a handful of Big Ten teams and looked at the distribution of yards gained across running back carries. Select a season and a couple teams below to see how they compared!")

st.markdown("Data courtesy of [CollegeFootballData.com](https://collegefootballdata.com/)")

#Get data from my github source
DATA_URL = 'https://raw.githubusercontent.com/jdellape/data-sources/main/cfb/rushing-analysis/big_10_carry_yards_by_running_backs.csv'
COMPARISON_DATA_URL = 'https://raw.githubusercontent.com/jdellape/data-sources/main/cfb/rushing-analysis/team_comparison_data.csv'

@st.cache
def load_data(url, nrows=None):
    data = pd.read_csv(url, nrows=nrows)
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(DATA_URL)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

#Create lists for user selection
team_list = list(data.team.unique())

season_list = list(data.season.unique())
season_list.sort(reverse=True) 

#Enable user selection
selected_season = st.selectbox(
     label='Select Season to Analyze:',
     options=season_list)

#Set teams that appear by default
#team_one = "Penn State"
#team_two = "Ohio State"

team_one = st.selectbox(
     label='Select Team 1:',
     options=team_list)

team_two = st.selectbox(
     label='Select Team 2:',
     options=[team for team in team_list if team != team_one])

#Specify the yardage bins we want for our analysis
bins_to_keep = ["(-10 | -8]","(-8 | -6]", "(-6 | -4]", "(-4 | -2]", "(-2 | 0]", "(0 | 2]", "(2 | 4]",
				"(4 | 6]", "(6 | 8]",	"(8 | 10]",	"(10 | 12]", "(12 | 14]", "(14 | 16]", "(16 | 18]",	
				"(18 | 20]", "(20 | 22]", "(22 | 24]", "(24 | 26]", "(26 | 28]", "(28 | 30]",	"(30 | 32]",	
				"(32 | 34]", "(34 | 36]",	"(36 | 38]", "(38 | 40]", "(40 | 42]", "(42 | 44]",	"(44 | 46]",	
				"(46 | 48]",	"(48 | 50]", "(50 | 52]", "(52 | 54]", "(54 | 56]",	"(56 | 58]","(58 | 60]",	
				"(60 | 62]",	"(62 | 64]", "(64 | 66]", "(66 | 68]", "(68 | 70]",	"(70 | 72]", "(72 | 74]",	
				"(74 | 76]","(76 | 78]","(78 | 80]","(80 | 82]","(82 | 84]","(84 | 86]","(86 | 88]",	
				"(88 | 90]", "(90 | 92]",	"(92 | 94]", "(94 | 96]","(96 | 98]"]

#Grab relevant subset of dataframe for analysis given user selections
data = data[data.statBin.isin(bins_to_keep)]
data = data[data.season==selected_season]
data = data[data.team.isin([team_one,team_two])]

#Get the total carries for each team
t1_data = data[data.team==team_one]
t2_data = data[data.team==team_two]

team_one_carry_count = t1_data['count'].sum() 
team_two_carry_count = t2_data['count'].sum()

#Get the team comparison data for the teams selected
comparison_data = load_data(COMPARISON_DATA_URL)
comparison_data = comparison_data[comparison_data.season==selected_season]
comparison_data = comparison_data[(comparison_data.primary_team==team_one) & (comparison_data.compared_against_team==team_two)]

#Display total carries for each team selected by user
col1, col2 = st.columns(2)
col1.metric(f"# Carries for {team_one}", team_one_carry_count)
col2.metric(f"# Carries for {team_two}", team_two_carry_count)

#Compile and display bar chart showing % of carries by yardage bin for each team 

#Specify configurations for charts
x = {"field": "statBin", "type": "ordinal", "sort": bins_to_keep, "axis":alt.Axis(title="Yards Gained")}
domain = ['Iowa', 'Michigan', 'Michigan State', 'Ohio State', 'Penn State', 'Wisconsin']
range_ = ['#000000', 'yellow', '#18453B', '#DE3121', '#00265D', '#A00001']

st.write('')
row3_space1, row3_1, row3_space2, row3_2, row3_space3 = st.columns(
    (.1, 1, .1, 1, .1))

with row3_1:
    st.subheader('Rushes by Yards Gained')
    c = alt.Chart(data).mark_bar(opacity=0.7).encode(
    x=x,
    y=alt.Y('count_over_window_sum', stack=None, axis=alt.Axis(title="% Total RB Carries", format='%')),
    color=alt.Color('team', scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(orient="top-right")),
    tooltip='count_over_window_sum'
    )
    st.altair_chart(c, use_container_width=True)

with row3_2:
    #Show the top bin differences between the teams
    st.subheader('Top Differences by Yardage Bin Between Teams')

    top_difference_df = comparison_data.iloc[:5,:]
    #Graph it in a meaningful way
    c_three = alt.Chart(top_difference_df).mark_bar().encode(
        x=x,
        y=alt.Y('difference', stack=None, axis=alt.Axis(title="Difference in % of Total Carries", format='%')),
        color=alt.condition(
            alt.datum.difference > 0,
            alt.value("steelblue"),  # The positive color
            alt.value("orange")  # The negative color
    ))

    st.altair_chart(c_three, use_container_width=True)

st.write('')


#Begin row for cumulative % of total runs breakdown
row4_space1, row4_1, row4_space2, row4_2, row4_space3 = st.columns(
    (.1, 1, .1, 1, .1))

with row4_1:
    st.subheader("Cumulative Percentage of Total Runshes by Yards Gained")

    #Incorporate the code at this link to make this chart interactive
    #https://altair-viz.github.io/gallery/multiline_tooltip.html

    #Show a cumulative line chart plotting both teams on single chart
    c_two = alt.Chart(data).mark_line().encode(
        x=x,
        y=alt.Y('cum_sum_as_window_percentage', stack=None, axis=alt.Axis(title=None, format='%')),
        color=alt.Color('team', scale=alt.Scale(domain=domain, range=range_), legend=None),
        tooltip='cum_sum_as_window_percentage'
    )                   
    st.altair_chart(c_two, use_container_width=True)

with row4_2:
    st.subheader("Difference in Cumulative Percentage Between Teams")
    #Get information regarding the cumulative perfect differences between t1 and t2
    cum_perc_diff_list = [v1 - v2 for v1, v2 in zip(list(t1_data.cum_sum_as_window_percentage), list(t2_data.cum_sum_as_window_percentage))]

    cum_series = pd.DataFrame({
      'statBin': bins_to_keep,
      'cum_diff': cum_perc_diff_list
    })

    # Basic Altair line chart where it picks automatically the colors for the lines
    cum_diff_chart = alt.Chart(cum_series).mark_line(
        point=alt.OverlayMarkDef(color="red")
        ).encode(
        x=x,
        y=alt.Y('cum_diff', axis=alt.Axis(title=None, format='%'))
    )
    st.altair_chart(cum_diff_chart)

st.write('') 





