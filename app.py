
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("earthquake_1995-2023.csv")

# Handle missing categorical values
df["country"] = df["country"].fillna("Unknown")
df["alert"] = df["alert"].fillna("Unknown")

# Title
st.title("Earthquake Data Analysis")
st.write("Explore and analyse historical earthquake records")

#sidebar

st.sidebar.header("Data Filters")

# Country selection
countries = ["All Countries"] + sorted(df["country"].unique().tolist())

selected_country = st.sidebar.selectbox(
    "Select Country",
    countries
)

# Magnitude slider
min_mag = float(df["magnitude"].min())
max_mag = float(df["magnitude"].max())

selected_magnitude = st.sidebar.slider(
    "Select Magnitude Range",
    min_value=min_mag,
    max_value=max_mag,
    value=(min_mag, max_mag),
    step=0.1
)

# Alert category selection
alerts = sorted(df["alert"].unique().tolist())

selected_alerts = st.sidebar.multiselect(
    "Select Alert Category",
    alerts,
    default=alerts
)

#filters

filtered_df = df.copy()

if selected_country != "All Countries":
    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

filtered_df = filtered_df[
    (filtered_df["magnitude"] >= selected_magnitude[0]) &
    (filtered_df["magnitude"] <= selected_magnitude[1])
]

filtered_df = filtered_df[
    filtered_df["alert"].isin(selected_alerts)
]

#kpi

st.subheader("Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Earthquakes",
        len(filtered_df)
    )

with col2:
    st.metric(
        "Sum of Magnitudes",
        round(filtered_df["magnitude"].sum(), 2)
    )

with col3:
    st.metric(
        "Average Magnitude",
        round(filtered_df["magnitude"].mean(), 2)
        if len(filtered_df) > 0 else 0
    )

col4, col5 = st.columns(2)

with col4:
    st.metric(
        "Highest Magnitude",
        round(filtered_df["magnitude"].max(), 2)
        if len(filtered_df) > 0 else 0
    )

with col5:
    st.metric(
        "Average Depth",
        round(filtered_df["depth"].mean(), 2)
        if len(filtered_df) > 0 else 0
    )


st.subheader("Earthquakes by Alert Category")

if not filtered_df.empty:
    alert_counts = filtered_df.groupby("alert").size()

    st.dataframe(
        alert_counts.reset_index(name="Number of Earthquakes"),
        use_container_width=True
    )
else:
    st.warning("No records found for the selected filters.")


st.subheader("Filtered Earthquake Records")

st.write("Total filtered records:", len(filtered_df))

st.dataframe(
    filtered_df,
    use_container_width=True
)


#data vizualization

st.header("Data Visualization")

if not filtered_df.empty:

    # Prepare date column
    filtered_df["date_time"] = pd.to_datetime(
        filtered_df["date_time"],
        dayfirst=True,
        errors="coerce"
    )

    # Create two columns
    col1, col2 = st.columns(2)

    #bar chart

    with col1:
        st.subheader("Earthquakes by Country")

        country_counts = (
            filtered_df.groupby("country")
            .size()
            .sort_values(ascending=False)
            .head(10)
        )

        fig1, ax1 = plt.subplots(figsize=(8, 5))

        ax1.bar(country_counts.index, country_counts.values)

        ax1.set_title("Countries by Earthquake Count")
        ax1.set_xlabel("Country")
        ax1.set_ylabel("Number of Earthquakes")

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        st.pyplot(fig1)
        plt.close(fig1)

        if len(country_counts) > 0:
            st.write(
                "Observation:country with the highest number of earthquakes selected from filter",
                country_counts.idxmax()
            )

    #line chart

    with col2:
        st.subheader("Yearly Earthquake Trends")

        yearly_counts = (
            filtered_df.dropna(subset=["date_time"])
            .groupby(filtered_df["date_time"].dt.year)
            .size()
        )

        fig2, ax2 = plt.subplots(figsize=(8, 5))

        ax2.plot(
            yearly_counts.index,
            yearly_counts.values,
            marker="o",
            label="Earthquakes per Year"
        )

        ax2.set_title("Earthquakes Recorded Each Year")
        ax2.set_xlabel("Year")
        ax2.set_ylabel("Number of Earthquakes")
        ax2.legend()

        plt.tight_layout()

        st.pyplot(fig2)
        plt.close(fig2)

        if len(yearly_counts) > 0:
            peak_year = yearly_counts.idxmax()

            st.write(
                "Observation: The highest number of "
                "earthquakes was recorded in",
                peak_year
            )

    #scatter plot

    st.subheader("Magnitude vs Depth")
    fig3, ax3 = plt.subplots(figsize=(9, 5))

    for alert_type in filtered_df["alert"].unique():

        data = filtered_df[filtered_df["alert"] == alert_type]

        ax3.scatter(
            data["magnitude"],
            data["depth"],
            label=alert_type,
            alpha=0.6
        )

    ax3.set_title("Relationship Between Magnitude and Depth")
    ax3.set_xlabel("Earthquake Magnitude")
    ax3.set_ylabel("Depth (km)")
    ax3.legend(title="Alert Category")

    plt.tight_layout()

    st.pyplot(fig3)
    plt.close(fig3)

    st.write(
        "Observation: The scatter plot helps identify "
        "the relationship between earthquake magnitude "
        "and depth. It also helps identify unusual records."
    )

else:
    st.warning("No data available for the selected filters.")
