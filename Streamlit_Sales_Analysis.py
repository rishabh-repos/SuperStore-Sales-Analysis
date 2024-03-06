import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')


#first we are setting up the page configurations such as name and icon
st.set_page_config(page_title="Superstore_Sales_Analysis", page_icon=":bar_chart:",layout="wide")

st.title(":department_store: SuperStore")
st.markdown('<style>h1 { text-align: center; } div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)



#creating a file uploader for the analysis purpose "by this we can perform EDA on diffrent dataset"
fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("Superstore 2023.csv")

#main developement starts from here

#converting datetime format
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d/%m/%Y %H:%M:%S")

##creating column for start date and end date.
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

#whichever date you select your data frame will be updated from that perticular date
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

##creation of side bar to filter the data base on region, state and city
st.sidebar.header("Choose your filter: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy() #if no region is selected copy the data from which is already in df
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy() #if no state is selected copy the data from which is already in df2 mean region
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick the City",df3["City"].unique())

#the flow of data selection (VERY CRUCIAL) using permutation and combination

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()



custom_colors = px.colors.qualitative.Set3
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 color="Category", # Specify the color parameter
                 color_discrete_sequence=custom_colors,
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)



custom_colors = ['#800000', '#8B4513', '#A0522D', '#A9A9A9', '#D2B48C', '#D3D3D3', '#DCDCDC']
with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.4,color_discrete_sequence = custom_colors)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))


with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')


with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')



filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", 
               labels={"Sales": "Amount", "month_year": "Month Year"},
               title="Monthly Sales Trend",
               height=500, width=1000,
               template="plotly_dark",  # Change template to a dark theme for better visibility
               color_discrete_sequence=["red"])  # Assign a color sequence to the line

fig2.update_xaxes(title="Month Year", tickangle=45)  # Rotate x-axis labels for better readability

st.plotly_chart(fig2, use_container_width=True)

# to download the Time Series Analysis data
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')


# Create a scatter plot with a color scale
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", color="Quantity",
                   title="Relationship between Sales and Profits using Scatter Plot",
                   labels={"Sales": "Sales", "Profit": "Profit"},
                   color_continuous_scale="Viridis",  # Set the color scale to Viridis
                   opacity=0.7)  # Set marker opacity

# Update layout
data1['layout'].update(titlefont=dict(size=20),
                       xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))

# Show scatter plot
st.plotly_chart(data1, use_container_width=True)


with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))


# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")



chart1, chart2 = st.columns((2))
custom_colors = ['#708090', '#800000', '#8B4513', '#A0522D', '#A9A9A9', '#D2B48C', '#D3D3D3', '#DCDCDC']
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Segment", color_discrete_sequence=px.colors.qualitative.Pastel1 , template = "plotly_dark")
    fig.update_traces(text = filtered_df["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

custom_colors = ['#FFDAB9', '#FFA07A', '#FF7F50', '#F08080', '#FFC0CB', '#FF69B4', '#FF6347', '#DB7093']

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values = "Sales", names = "Category", color_discrete_sequence = custom_colors, template = "gridon")
    fig.update_traces(text = filtered_df["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)


import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

##Create a treemap based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category",
                  title="Sales TreeMap by Region, Category, and Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)
