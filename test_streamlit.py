#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import sys
import os

# Add the app directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="🏈 Football Betting Dashboard Test",
    page_icon="⚽",
    layout="wide"
)

st.title("🏈 Football LSTM Betting Dashboard - Test")

st.write("Testing basic Streamlit functionality...")

# Test data loading
try:
    if os.path.exists("data/bets_today.csv"):
        bets_df = pd.read_csv("data/bets_today.csv")
        st.success(f"✅ Successfully loaded {len(bets_df)} bets")
        st.dataframe(bets_df)
    else:
        st.error("❌ bets_today.csv not found")
        
    if os.path.exists("data/lstm/predictions_today.csv"):
        pred_df = pd.read_csv("data/lstm/predictions_today.csv")
        st.success(f"✅ Successfully loaded {len(pred_df)} predictions")
        st.dataframe(pred_df)
    else:
        st.error("❌ predictions_today.csv not found")
        
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")

# Test BettingTracker
try:
    from betting_tracker import BettingTracker
    tracker = BettingTracker()
    stats = tracker.get_statistics()
    st.success("✅ BettingTracker loaded successfully")
    st.json(stats)
except Exception as e:
    st.error(f"❌ Error loading BettingTracker: {str(e)}")

st.write("Test completed!")