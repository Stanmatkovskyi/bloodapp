import streamlit as st
import json
import io
import os
from datetime import date, time, datetime
from streamlit_option_menu import option_menu
from TransportFeedbackSim import TFSim
from visualize import *
from BloodProductStorage import BloodProductStorage
from platoon import Platoon, PlatoonDemand

st.set_page_config(page_title="Blood Logistics Tool", layout="wide")

DATA_FILE = "saved_data.json"

def load_saved_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for k, v in data.items():
            if not ("FormSubmitter:" in k or k.startswith("week_") or k.startswith("simulation_days") or k.startswith("med_platoon_id") or k.startswith("blood_inventory")):
                st.session_state[k] = v

def save_session_state():
    to_save = {k: v for k, v in st.session_state.items() if not k.startswith("_")}
    with open(DATA_FILE, "w") as f:
        json.dump(to_save, f, indent=4, default=str)

def show_home():
    st.header("Welcome to the Blood Logistics Tool")
    name = st.text_input("Enter your name", value=st.session_state.get("user_name", ""))
    st.session_state["user_name"] = name
    if name:
        st.success(f"Welcome, {name}! Please navigate to the pages on the left to proceed.")
        save_session_state()

def show_med_log_company():
    st.header("Medical Logistics Company Page")
    company_id = st.number_input("Medical Logistics Company ID", min_value=0, step=1, value=st.session_state.get("company_id", 0))
    st.session_state["company_id"] = company_id

    num_platoons = st.number_input("Number of Platoons", min_value=1, step=1, value=st.session_state.get("num_platoons", 1))
    st.session_state["num_platoons"] = num_platoons

    platoons = []
    for i in range(int(num_platoons)):
        st.subheader(f"Platoon {i+1}")
        pid = st.text_input(f"Platoon ID {i+1}", value=st.session_state.get(f"pid_{i}", ""), key=f"pid_{i}")
        size = st.number_input(f"Platoon Size {i+1}", min_value=1, value=st.session_state.get(f"size_{i}", 10), key=f"size_{i}")
        days_away = st.number_input(f"Days Away from Home Base (Platoon {i+1})", min_value=0, value=st.session_state.get(f"days_{i}", 1), key=f"days_{i}")

        platoons.append({"Platoon ID": pid, "Size": size, "Days Away": days_away})

    if st.button("Save Medical Logistics Company Info"):
        st.session_state["med_log_company_info"] = {
            "Company ID": company_id,
            "Number of Platoons": num_platoons,
            "Platoons": platoons
        }
        save_session_state()
        st.success("Medical Logistics Company info saved!")

def show_conflict_prediction():
    st.header("Conflict Prediction Page")
    with st.form(key="conflict_prediction_form"):
        T = st.number_input("Length of Simulation in Days", min_value=1, value=15, key="simulation_days")
        n = st.number_input("Number of Platoons", min_value=1, value=st.session_state.get("num_platoons", 1), key="n")
        st.markdown("### Define Conflict Assessment Ranges")
        num_ranges = st.number_input("Number of Ranges", min_value=1, value=3, key="num_ranges")
        ranges = []
        matrix = []
        conflict_level_labels = ["1: Non-Combat", "2: Sustain Combat", "3: Assault Combat", "4: Extreme Combat"]
        last_end = 0
        for i in range(num_ranges):
            st.markdown(f"**Range {i+1}**")
            start_day = st.number_input(f"Start Day of Range {i+1}", min_value=1, value=last_end+1, key=f"start_day_{i}")
            end_day = st.number_input(f"End Day of Range {i+1}", min_value=start_day, value=start_day+3, key=f"end_day_{i}")
            last_end = end_day
            ranges.append((start_day, end_day))
            dist = []
            total = 0
            for j in range(4):
                val = st.slider(f"{conflict_level_labels[j]} (0–5):", min_value=0, max_value=5, value=1, key=f"range_{i}_level_{j}")
                dist.append(val)
                total += val
            if total != 5:
                st.error(f"Range {i+1}: conflict levels must sum to 5. Current total: {total}")
            matrix.append([x/5 for x in dist])

        submit = st.form_submit_button("Submit and Run Simulation")

    if submit:
        st.session_state.ranges = ranges
        st.session_state.conflict_matrix = matrix

        try:
            l = [int(p["Days Away"]) for p in st.session_state["med_log_company_info"]["Platoons"]]
            avgOrderInterval = [3] * int(n)
            maxOrderInterval = [5] * int(n)
            TargetInv = [[1000, 40]] * int(n)
            PI = [[] for _ in range(n)]
            CI = [["FWB", 10000, 15], ["Plasma", 5000, 30]]
            platoonSize = [int(p["Size"]) for p in st.session_state["med_log_company_info"]["Platoons"]]

            CLMatrix = []
            for start, end in ranges:
                for _ in range(start, end + 1):
                    CLMatrix.append(matrix[ranges.index((start, end))])
            CLMatrix = [CLMatrix[min(i, len(CLMatrix)-1)] for i in range(int(n))]

            transportSpeed = [1] * int(n)
            transportCapacity = [1000] * int(n)

            platoons = [Platoon(l[i], BloodProductStorage([]), BloodProductStorage([]), CLMatrix[i], avgOrderInterval[i], maxOrderInterval[i], TargetInv[i]) for i in range(n)]

            st.subheader("Midway Demand Estimate")
            plot_midway_blood_demand(platoons, show_plot=True)

            avg_df, total_df = TFSim(T, n, l, avgOrderInterval, maxOrderInterval, transportSpeed, transportCapacity, TargetInv, PI, CI, CLMatrix, platoonSize)
            st.subheader("Simulation Results")
            st.write("### Average Results")
            st.dataframe(avg_df)
            st.write("### Visualizations")
            plot_unmet_demand_boxplot(avg_df)
            plot_transport_usage(avg_df)
            plot_expired(avg_df, platoon_sizes=platoonSize)

        except Exception as e:
            st.error(f"Simulation failed: {e}")

def main():
    load_saved_data()
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Medical Logistics Company", "Conflict Prediction"],
            icons=["house", "hospital", "exclamation-triangle"],
            menu_icon="cast",
            default_index=0
        )
    if selected == "Home":
        show_home()
    elif selected == "Medical Logistics Company":
        show_med_log_company()
    elif selected == "Conflict Prediction":
        show_conflict_prediction()

if __name__ == "__main__":
    main()
