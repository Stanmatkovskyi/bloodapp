import streamlit as st
import json
import io
import os
from datetime import date, time, datetime
from streamlit_option_menu import option_menu
import pandas as pd
from TransportFeedbackSim import TFSim
from visualize import (
    plot_midway_blood_demand,
    plot_daily_unmet_demand_include_zeros,
    plot_unmet_demand_boxplot,
    plot_transport_usage,
    plot_transport_space_usage,
    plot_platoon_transport_histograms,
    plot_platoon_transport_space_histograms,
    plot_expired
)
from platoon import Platoon
from BloodProductStorage import BloodProductStorage

st.set_page_config(page_title="Blood Logistics Tool", layout="wide")
DATA_FILE = "saved_data.json"

st.title("ONR Blood Management Support Tool")
st.sidebar.header("User Input")

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

    num_platoons = st.number_input("Number of Platoons", min_value=0, step=1, value=st.session_state.get("num_platoons", 0))
    st.session_state["num_platoons"] = num_platoons

    platoons = []
    for i in range(int(num_platoons)):
        st.subheader(f"Platoon {i+1}")
        pid = st.text_input(f"Platoon ID {i+1}", key=f"pid_{i}")
        size = st.number_input(f"Platoon Size {i+1}", min_value=0, key=f"size_{i}")
        days_away = st.number_input(f"Days Away from Home Base (Platoon {i+1})", min_value=0, key=f"days_{i}")
        platoons.append({"Platoon ID": pid, "Size": size, "Days Away": days_away})

    st.subheader("Company Inventory")
    if "company_inventory" not in st.session_state:
        st.session_state.company_inventory = []

    with st.expander("Add Inventory Entry"):
        blood_type = st.selectbox("Blood Type", ["FWB", "Plasma"], key="inv_type")
        units = st.number_input("Units", min_value=0, step=1, key="inv_units")
        days_to_expire = st.number_input("Days to Expire", min_value=0, step=1, key="inv_expiry")
        if st.button("Add Inventory"):
            new_entry = [blood_type, units, days_to_expire]
            st.session_state.company_inventory.append(new_entry)
            st.success("Inventory added.")

    if st.session_state.company_inventory:
        st.write("Current Inventory:")
        st.table(pd.DataFrame(st.session_state.company_inventory, columns=["Type", "Units", "Days Until Expired"]))

    if st.button("Save Medical Logistics Company Info"):
        st.session_state["med_log_company_info"] = {
            "Company ID": company_id,
            "Number of Platoons": num_platoons,
            "Platoons": platoons
        }
        save_session_state()
        st.success("Medical Logistics Company info saved!")

def show_transport_info():
    st.header("Transport Information Page")
    company_id = st.number_input("Medical Company ID", min_value=0, step=1, key="transport_company_id")
    num_platoons = st.number_input("Number of Platoons", min_value=0, step=1, key="transport_num_platoons")

    transport_methods = ["Helicopter", "Truck", "Boat", "Drone", "Airplane"]
    all_platoon_transports = []

    for p in range(int(num_platoons)):
        st.subheader(f"Platoon {p+1} Transportation Info")
        num_transports = st.number_input(f"Number of Transportation Options for Platoon {p+1}", min_value=0, step=1, key=f"num_transports_{p}")
        platoon_transports = []

        for i in range(int(num_transports)):
            method = st.selectbox(f"Select Transportation Method", transport_methods, key=f"method_{p}_{i}")
            days_away = st.number_input(f"Days Away from Supply Base", min_value=0.0, step=0.1, key=f"days_away_{p}_{i}")
            avg_days_between = st.number_input(f"Average Days Between Restocks", min_value=0.0, step=0.1, key=f"avg_days_{p}_{i}")
            max_days_between = st.number_input(f"Maximum Days Between Restocks", min_value=0.0, step=0.1, key=f"max_days_{p}_{i}")
            transport_capacity = st.number_input(f"Transport Capacity (pints)", min_value=0, step=1, key=f"transport_capacity_{p}_{i}")
            platoon_transports.append({"Method": method, "Days Away from Base": days_away, "Average Days Between Restocks": avg_days_between, "Maximum Days Between Restocks": max_days_between, "Transport Capacity (pints)": transport_capacity})

        all_platoon_transports.append({"Platoon Number": p + 1, "Transport Options": platoon_transports})

    if st.button("Submit Transport Info"):
        st.session_state["transport_info"] = {"Company ID": company_id, "Platoons": all_platoon_transports}
        save_session_state()
        st.success("Transport data saved!")

    if "transport_info" in st.session_state:
        st.subheader("Platoon Summary")
        for platoon in st.session_state["transport_info"].get("Platoons", []):
            with st.expander(f"Platoon {platoon['Platoon Number']} Summary"):
                for idx, option in enumerate(platoon["Transport Options"]):
                    st.markdown(f"**Transport {idx + 1}:**")
                    st.write(option)

def show_conflict_prediction():
    st.header("Conflict Prediction Page")

    if "user_data" not in st.session_state:
        st.session_state.user_data = []

    with st.form(key="conflict_prediction_form"):
        simulation_days = st.number_input("Length of Simulation in Days:", min_value=1, value=15, key="simulation_days")
        med_platoon_id = st.number_input("Medical Platoon ID:", min_value=0, value=0, key="med_platoon_id")
        blood_inventory = st.number_input("Fresh Whole Blood Inventory on Hand (pints):", min_value=0, value=0, key="blood_inventory")
        st.markdown("### Define Conflict Assessment Ranges")
        num_ranges = st.number_input("Number of Ranges", min_value=1, value=3, key="num_ranges")

        day_ranges, conflict_matrix = [], []
        conflict_level_labels = ["1: Non-Combat", "2: Sustain Combat", "3: Assault Combat", "4: Extreme Combat"]
        last_end = 0

        for i in range(int(num_ranges)):
            st.markdown(f"**Range {i+1}**")
            start_day = st.number_input(f"Start Day of Range {i+1}", min_value=1, value=last_end + 1, key=f"start_day_{i}")
            end_day = st.number_input(f"End Day of Range {i+1}", min_value=start_day, value=min(simulation_days, start_day + 4), key=f"end_day_{i}")
            last_end = end_day
            day_ranges.append((start_day, end_day))
            range_data, total = [], 0

            for level in range(4):
                val = st.slider(f"{conflict_level_labels[level]} (0–5):", min_value=0, max_value=5, step=1, key=f"range_{i}_level_{level}")
                total += val
                range_data.append(val)

            if total != 5:
                st.error(f"Range {i+1} ({start_day}–{end_day}): conflict levels must sum to 5 (currently {total}).")
            conflict_matrix.append(range_data)

        submit = st.form_submit_button("Submit")

    if submit:
        new_entry = {
            "Length of Simulation in Days": simulation_days,
            "Medical Platoon ID": med_platoon_id,
            "Fresh Whole Blood Inventory on Hand (pints)": blood_inventory,
            "Conflict Ranges": [
                {"Days": f"{start}-{end}", "Conflict Levels": {"Labels": conflict_level_labels, "Distribution": dist}}
                for (start, end), dist in zip(day_ranges, conflict_matrix)
            ]
        }
        st.session_state.user_data.append(new_entry)
        save_session_state()
        st.success("Data added successfully!")

        if "med_log_company_info" in st.session_state and "transport_info" in st.session_state:
            med_info = st.session_state["med_log_company_info"]
            n = med_info["Number of Platoons"]
            l = [p["Days Away"] for p in med_info["Platoons"]]
            avgOrderInterval = [1] * n
            maxOrderInterval = [1] * n
            TargetInv = [[1000, 40] for _ in range(n)]
            PI = [[] for _ in range(n)]
            CI = st.session_state.company_inventory
            CLMatrix = [[1, 0, 0, 0, 0] for _ in range(n)]
            platoonSize = [p["Size"] for p in med_info["Platoons"]]
            platoons = [Platoon(l[i], BloodProductStorage([]), BloodProductStorage([]), CLMatrix[i], avgOrderInterval[i], maxOrderInterval[i], TargetInv[i], platoonSize[i]) for i in range(n)]
            st.subheader("Preview: Midway Blood Demand Distribution")
            plot_midway_blood_demand(platoons, show_plot=True)

        if st.button("Run Full Simulation"):
            med_info = st.session_state["med_log_company_info"]
            transport_info = st.session_state["transport_info"]
            n = med_info["Number of Platoons"]
            l = [p["Days Away"] for p in med_info["Platoons"]]
            avgOrderInterval, maxOrderInterval, transportCapacity = [], [], []
            for p in transport_info["Platoons"]:
                t = p["Transport Options"][0]
                avgOrderInterval.append(t["Average Days Between Restocks"])
                maxOrderInterval.append(t["Maximum Days Between Restocks"])
                transportCapacity.append(t["Transport Capacity (pints)"])
            platoonSize = [p["Size"] for p in med_info["Platoons"]]
            TargetInv = [[1000, 40] for _ in range(n)]
            PI = [[] for _ in range(n)]
            CI = st.session_state.company_inventory
            CLMatrix = []
            for _ in range(n):
                dist = [0]*5
                for r in st.session_state["user_data"][-1]["Conflict Ranges"]:
                    for j, val in enumerate(r["Conflict Levels"]["Distribution"]):
                        dist[j] += val
                total = sum(dist)
                CLMatrix.append([x / total for x in dist])
            T = st.session_state["user_data"][-1]["Length of Simulation in Days"]
            avgDF, totalDF = TFSim(T, n, l, avgOrderInterval, maxOrderInterval, [1]*n, transportCapacity, TargetInv, PI, CI, CLMatrix, platoonSize)
            st.subheader("Simulation Results")
            plot_daily_unmet_demand_include_zeros(avgDF, platoonSize, show_plot=True)
            plot_unmet_demand_boxplot(avgDF, show_plot=True)
            plot_transport_usage(avgDF, show_plot=True)
            plot_transport_space_usage(avgDF, show_plot=True)
            plot_platoon_transport_histograms(avgDF, show_plot=True)
            plot_platoon_transport_space_histograms(avgDF, show_plot=True)
            plot_expired(avgDF, platoonSize, show_plot=True)

with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Medical Logistics Company", "Transport Info", "Conflict Prediction"],
        icons=["house", "hospital", "truck", "exclamation-triangle"],
        menu_icon="cast",
        default_index=0
    )

def main():
    load_saved_data()
    if selected == "Home":
        show_home()
    elif selected == "Medical Logistics Company":
        show_med_log_company()
    elif selected == "Transport Info":
        show_transport_info()
    elif selected == "Conflict Prediction":
        show_conflict_prediction()

if __name__ == "__main__":
    main()
