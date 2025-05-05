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

def show_transport_info():
    st.header("Transport Information Page")

    company_id = st.number_input("Medical Company ID", min_value=0, step=1,
                                 value=st.session_state.get("transport_company_id", 0),
                                 key="transport_company_id")

    num_platoons = st.number_input("Number of Platoons", min_value=0, step=1,
                                   value=st.session_state.get("transport_num_platoons", 0),
                                   key="transport_num_platoons")

    transport_methods = ["Helicopter", "Truck", "Boat", "Drone", "Airplane"]
    all_platoon_transports = []

    for p in range(int(num_platoons)):
        st.subheader(f"Platoon {p+1} Transportation Info")

        num_transports = st.number_input(f"Number of Transportation Options for Platoon {p+1}", min_value=0, step=1,
                                         value=st.session_state.get(f"num_transports_{p}", 0),
                                         key=f"num_transports_{p}")

        platoon_transports = []

        for i in range(int(num_transports)):
            st.markdown(f"**Transport Option {i+1} for Platoon {p+1}**")

            method = st.selectbox(
                f"Select Transportation Method", transport_methods,
                index=transport_methods.index(st.session_state.get(f"method_{p}_{i}", "Helicopter")),
                key=f"method_{p}_{i}"
            )

            days_away = st.number_input(f"Days Away from Supply Base", min_value=0.0, step=0.1,
                                        value=st.session_state.get(f"days_away_{p}_{i}", 0.0),
                                        key=f"days_away_{p}_{i}")

            avg_days_between = st.number_input(
                f"Average Days Between Restocks", min_value=0.0, step=0.1,
                value=st.session_state.get(f"avg_days_{p}_{i}", 0.0),
                key=f"avg_days_{p}_{i}")

            max_days_between = st.number_input(
                f"Maximum Days Between Restocks", min_value=0.0, step=0.1,
                value=st.session_state.get(f"max_days_{p}_{i}", 0.0),
                key=f"max_days_{p}_{i}")

            transport_capacity = st.number_input(
                f"Transport Capacity (pints)", min_value=0, step=1,
                value=st.session_state.get(f"transport_capacity_{p}_{i}", 0),
                key=f"transport_capacity_{p}_{i}")

            platoon_transports.append({
                "Method": method,
                "Days Away from Base": days_away,
                "Average Days Between Restocks": avg_days_between,
                "Maximum Days Between Restocks": max_days_between,
                "Transport Capacity (pints)": transport_capacity
            })

        all_platoon_transports.append({
            "Platoon Number": p + 1,
            "Transport Options": platoon_transports
        })

    if st.button("Submit Transport Info"):
        st.session_state["transport_info"] = {
            "Company ID": company_id,
            "Platoons": all_platoon_transports
        }
        save_session_state()
        st.success("Transport data saved!")

    if "transport_info" in st.session_state:
        st.subheader("Platoon Summary")
        for platoon in st.session_state["transport_info"].get("Platoons", []):
            with st.expander(f"Platoon {platoon['Platoon Number']} Summary"):
                for idx, option in enumerate(platoon["Transport Options"]):
                    st.markdown(f"**Transport {idx + 1}:**")
                    st.write(option)

def main():
    load_saved_data()
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Medical Logistics Company", "Transport Info", "Conflict Prediction"],
            icons=["house", "hospital", "truck", "exclamation-triangle"],
            menu_icon="cast",
            default_index=0
        )
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
