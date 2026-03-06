import streamlit as st
import random
import pandas as pd

def simulate_one_session(stages, current_bankroll, stop_on_bankrupt):
    """1セットのシミュレーション。スピン回数もカウントする"""
    session_profit = 0  
    spins_taken = 0  
    
    for bet_amount, max_spins in stages:
        for _ in range(max_spins):
            spins_taken += 1  
            
            if bet_amount > 0:
                if stop_on_bankrupt and (current_bankroll + session_profit < bet_amount):
                    # 資金ショート時は「ベットできなかった」ため、実際の実行回数は spins_taken - 1
                    return False, session_profit, True, spins_taken - 1
                
                session_profit -= bet_amount
                
            result = random.randint(0, 36)
            
            if result == 0 and bet_amount > 0:
                session_profit += bet_amount * 36
                return True, session_profit, False, spins_taken
            
    # 全てのステージが終わっても当たらなかった場合
    return False, session_profit, False, spins_taken

def run_simulations(stages, trials, initial_bankroll, stop_on_bankrupt):
    """指定回数シミュレーションを繰り返す"""
    results = []
    cumulative_funds = initial_bankroll
    cumulative_history = [initial_bankroll]
    
    wins = 0
    actual_trials = 0
    is_bankrupt_overall = False
    session_logs = []  # 【変更】当たりだけでなく、全セットのログを記録する
    bankrupt_spin = None  
    
    for _ in range(trials):
        actual_trials += 1
        
        is_win, session_profit, is_bankrupt, spins_taken = simulate_one_session(stages, cumulative_funds, stop_on_bankrupt)
        
        if is_win:
            wins += 1
            result_str = "🎯 当たり"
        elif is_bankrupt:
            result_str = "💀 ショート(資金尽きる)"
        else:
            result_str = "💦 ハズレ(最後まで出ず)"
            
        # 全セットの記録を保存
        session_logs.append({
            "セット(横軸)": actual_trials,
            "結果": result_str,
            "スピン回数(回)": spins_taken,
            "そのセットの損益(W)": session_profit
        })
            
        cumulative_funds += session_profit
        cumulative_history.append(cumulative_funds)
        results.append(session_profit)
        
        if stop_on_bankrupt and is_bankrupt:
            is_bankrupt_overall = True
            bankrupt_spin = spins_taken
            break
            
    return wins, results, cumulative_history, actual_trials, is_bankrupt_overall, session_logs, bankrupt_spin


# === ここからUIの構築 (Streamlit) ===

st.set_page_config(page_title="ルーレット検証ツール", layout="wide")
st.title("🎰 ヨーロピアンルーレット 資金推移シミュレーター")

st.header("📖 【参考】「0」が少なくとも1回以上当たる確率 (1〜300回)")
with st.expander("確率表を表示する (クリックで展開)", expanded=False):
    prob_data = []
    for n in range(1, 301):
        prob = (1 - (36/37)**n) * 100
        prob_data.append({
            "スピン回数": f"{n} 回", 
            "少なくとも1回当たる確率": f"{prob:.2f} %"
        })
    df_static_prob = pd.DataFrame(prob_data)
    st.dataframe(df_static_prob, use_container_width=True, height=400)

st.markdown("---") 

# サイドバー
st.sidebar.header("💰 軍資金と検証モード")
initial_bankroll = st.sidebar.number_input("初期軍資金 (ウォン)", min_value=0, max_value=100000000, value=500000, step=50000)
trials = st.sidebar.number_input("最大試行回数 (セット数)", min_value=1, max_value=100000, value=1000, step=100)

stop_on_bankrupt = st.sidebar.toggle("⚠️ 資金ショートで強制終了する", value=True)

st.sidebar.header("ベット戦略の設定")
st.sidebar.subheader("ステージ1: 見送り")
wait_spins = st.sidebar.number_input("見送り回数", value=10, step=1)
st.sidebar.subheader("ステージ2: 第1ベット")
bet1_amount = st.sidebar.number_input("賭け額 1", value=2500, step=500)
bet1_spins = st.sidebar.number_input("回数 1", value=20, step=1)
st.sidebar.subheader("ステージ3: 第2ベット")
bet2_amount = st.sidebar.number_input("賭け額 2", value=5000, step=500)
bet2_spins = st.sidebar.number_input("回数 2", value=20, step=1)
st.sidebar.subheader("ステージ4: 第3ベット")
bet3_amount = st.sidebar.number_input("賭け額 3", value=7500, step=500)
bet3_spins = st.sidebar.number_input("回数 3", value=10, step=1)
st.sidebar.subheader("ステージ5: 第4ベット")
bet4_amount = st.sidebar.number_input("賭け額 4", value=10000, step=500)
bet4_spins = st.sidebar.number_input("回数 4", value=10, step=1)
st.sidebar.subheader("ステージ6: 第5ベット")
bet5_amount = st.sidebar.number_input("賭け額 5", value=15000, step=500)
bet5_spins = st.sidebar.number_input("回数 5", value=10, step=1)
st.sidebar.subheader("ステージ7: 第6ベット")
bet6_amount = st.sidebar.number_input("賭け額 6", value=20000, step=500)
bet6_spins = st.sidebar.number_input("回数 6", value=10, step=1)

# 実行ボタン
if st.button("🚀 シミュレーションを実行", type="primary"):
    
    custom_strategy = [
        (0, wait_spins),
        (bet1_amount, bet1_spins),
        (bet2_amount, bet2_spins),
        (bet3_amount, bet3_spins),
        (bet4_amount, bet4_spins),
        (bet5_amount, bet5_spins),
        (bet6_amount, bet6_spins)
    ]
    
    with st.spinner('計算中...'):
        wins, results, cumulative_history, actual_trials, is_bankrupt, session_logs, bankrupt_spin = run_simulations(
            custom_strategy, trials, initial_bankroll, stop_on_bankrupt
        )
    
    # 統計の計算
    win_rate = (wins / actual_trials) * 100 if actual_trials > 0 else 0
    avg_profit = sum(results) / actual_trials if actual_trials > 0 else 0
    max_loss = min(results) if results else 0
    
    # 当たった時だけのスピン回数を抽出して平均を出す
    winning_spins_only = [log["スピン回数(回)"] for log in session_logs if "当たり" in log["結果"]]
    avg_win_spin = sum(winning_spins_only) / len(winning_spins_only) if winning_spins_only else 0  
    
    # --- 結果の表示 ---
    st.header("📊 シミュレーション結果")
    
    if is_bankrupt:
        st.error(f"⚠️ 【資金ショート】 {actual_trials}セット目の **{bankrupt_spin}回目のスピン（ベット）直前** に軍資金が尽き、賭け金が払えなくなったため強制終了しました。")
    elif not stop_on_bankrupt:
        st.info(f"無限の資金があると仮定し、目標の {trials} セットを完走しました。")
    else:
        st.success(f"🎉 資金ショートすることなく、目標の {trials} セットを無事に完走しました！")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("実行できたセット数", f"{actual_trials} / {trials} 回")
    col2.metric("勝率", f"{win_rate:.2f}%")
    col3.metric("🎯 0が当たった平均回数", f"{avg_win_spin:.1f} 回目")
    col4.metric("1セット平均損益", f"{avg_profit:,.0f} ウォン")
    col5.metric("1セット最大損失額", f"{max_loss:,.0f} ウォン")

    # 【変更】全ログを表示
    st.subheader("📋 全セットの詳細履歴（グラフ連動）")
    if session_logs:
        st.write("各セット（グラフの横軸）ごとの詳細です。大負けした時に「何回連続で外したか」が一目で分かります。")
        
        df_logs = pd.DataFrame(session_logs)
        # セット数をインデックス（行の左端）に設定し、グラフの横軸と一致させる
        df_logs.set_index("セット(横軸)", inplace=True)
        
        # 損益を3桁カンマ区切りで見やすくフォーマット
        st.dataframe(df_logs.style.format({"そのセットの損益(W)": "{:,.0f}"}), height=300)
    else:
        st.warning("データがありません。")

    st.subheader("📈 資金推移グラフ (お財布の中身)")
    chart_data = pd.DataFrame(cumulative_history, columns=["お財布残高 (ウォン)"])
    st.line_chart(chart_data)