import streamlit as st
import random
import pandas as pd

# --- 【重要】一番最初にこの命令を持ってくる必要があります ---
st.set_page_config(page_title="検証", layout="wide")

# --- 次にスマホ最適化のCSS ---
st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] {
        font-size: 12px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.0rem !important;
    }
    .stDataFrame div {
        font-size: 11px !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def simulate_one_session(stages, current_bankroll, stop_on_bankrupt):
    session_profit = 0  
    spins_taken = 0  
    for bet_amount, max_spins in stages:
        for _ in range(max_spins):
            spins_taken += 1  
            if bet_amount > 0:
                if stop_on_bankrupt and (current_bankroll + session_profit < bet_amount):
                    return False, session_profit, True, spins_taken - 1
                session_profit -= bet_amount
            result = random.randint(0, 36)
            if result == 0 and bet_amount > 0:
                session_profit += bet_amount * 36
                return True, session_profit, False, spins_taken
    return False, session_profit, False, spins_taken

def run_simulations(stages, trials, initial_bankroll, stop_on_bankrupt):
    results = []
    cumulative_funds = initial_bankroll
    cumulative_history = [initial_bankroll]
    wins = 0
    actual_trials = 0
    is_bankrupt_overall = False
    session_logs = []  
    bankrupt_spin = None  
    for _ in range(trials):
        actual_trials += 1
        is_win, session_profit, is_bankrupt, spins_taken = simulate_one_session(stages, cumulative_funds, stop_on_bankrupt)
        if is_win:
            wins += 1
            result_str = "🎯当"
        elif is_bankrupt:
            result_str = "💀破"
        else:
            result_str = "💦外"
        session_logs.append({
            "No": actual_trials,
            "結": result_str,
            "回": spins_taken,
            "損益": session_profit
        })
        cumulative_funds += session_profit
        cumulative_history.append(cumulative_funds)
        results.append(session_profit)
        if stop_on_bankrupt and is_bankrupt:
            is_bankrupt_overall = True
            bankrupt_spin = spins_taken
            break
    return wins, results, cumulative_history, actual_trials, is_bankrupt_overall, session_logs, bankrupt_spin

# --- UI構築 ---
st.caption("🎰 ルーレットシミュレーター")

with st.expander("📖 累積確率表", expanded=False):
    prob_data = [{"回": f"{n}", "率": f"{(1-(36/37)**n)*100:.1f}%"} for n in range(1, 301)]
    st.dataframe(pd.DataFrame(prob_data), use_container_width=True, height=150)

st.sidebar.header("💰 設定")
initial_bankroll = st.sidebar.number_input("軍資金", value=300000, step=50000)
trials = st.sidebar.number_input("セット数", value=100, step=10)
stop_on_bankrupt = st.sidebar.toggle("破産で終了", value=True)

with st.sidebar.expander("🎯 戦略"):
    wait_spins = st.number_input("見送", value=10)
    b1 = (st.number_input("額1", value=2500), st.number_input("回1", value=30))
    b2 = (st.number_input("額2", value=5000), st.number_input("回2", value=20))
    b3 = (st.number_input("額3", value=7500), st.number_input("回3", value=10))
    b4 = (st.number_input("額4", value=10000), st.number_input("回4", value=10))
    b5 = (st.number_input("額5", value=0), st.number_input("回5", value=0))
    b6 = (st.number_input("額6", value=0), st.number_input("回6", value=0))

if st.button("🚀 実行", type="primary", use_container_width=True):
    stages = [(0, wait_spins), b1, b2, b3, b4, b5, b6]
    wins, results, cumulative_history, actual_trials, is_bankrupt, session_logs, bankrupt_spin = run_simulations(
        stages, trials, initial_bankroll, stop_on_bankrupt
    )
    
    if is_bankrupt:
        st.error(f"💀{actual_trials}回目 {bankrupt_spin}回で破産", icon="🚨")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("勝率", f"{(wins/actual_trials)*100:.1f}%")
    c2.metric("残高", f"{cumulative_history[-1]:,.0f}")
    winning_spins = [l["回"] for l in session_logs if "当" in l["結"]]
    avg_win = sum(winning_spins)/len(winning_spins) if winning_spins else 0
    c3.metric("平均当", f"{avg_win:.1f}")

    st.dataframe(pd.DataFrame(session_logs).set_index("No"), use_container_width=True, height=200)
    st.line_chart(pd.DataFrame(cumulative_history, columns=["残高"]), height=200)

