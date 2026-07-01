"""
关键词 (Keyword Plus/ID) 爆发检测
=================================
方法：Kleinberg (2002) 爆发检测算法

改进：用**标准化计数**替代原始发文量作为算法输入。
  原始发文量因2020年后总发文量激增，导致所有关键词的爆发集中检测在近年。
  
  标准化方法：对每个关键词每年的原始发文量，按参考总发文量（中位数）缩放
    标准化计数 = 原始计数 × (参考总发文量 / 当年总发文量)
  
  这等效于：如果每年总发文量保持恒定，该关键词会观测到的发文量。
  这样既消除了总量激增的干扰，又保留了Kleinberg算法的完整框架和Poisson模型。

论文中可写：
  "We employed the Kleinberg burst detection algorithm (Kleinberg, 2002) 
   on the normalized occurrence counts of Keywords Plus (ID), where counts 
   were adjusted by the ratio of the median annual total publications to 
   the actual annual total publications to eliminate the confounding effect 
   of overall publication growth."

输出：关键词爆发检测.csv
"""

import metaknowledge as mk
import pandas as pd
import numpy as np
from collections import defaultdict
import math
import os

# ===================== 1. 读取数据 =====================
list_file = [
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (1).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (2).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (3).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (4).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (5).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (6).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (7).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs (8).txt",
    r"C:\Users\谢\Desktop\vscodepj\文献计量学\bib文件\savedrecs.txt",
]

print("正在读取数据...")
rc = mk.RecordCollection()
for f in list_file:
    if os.path.exists(f):
        rc += mk.RecordCollection(f)
        print(f"已加载 {os.path.basename(f)}，当前总记录数: {len(rc)}")
    else:
        print(f"文件不存在: {f}")

print(f"\n总记录数: {len(rc)}")

# ===================== 2. 提取数据 =====================
# 提取 Keyword Plus (ID 字段) 和发文年份 (PY 字段)
kw_year_count = defaultdict(lambda: defaultdict(int))
year_total = defaultdict(int)

for rec in rc:
    # Keyword Plus 使用 ID 字段
    kw_raw = rec.get("ID")
    py_raw = rec.get("PY")
    
    if not kw_raw or not py_raw:
        continue
    
    try:
        py = int(py_raw)
    except (ValueError, TypeError):
        continue
    
    if isinstance(kw_raw, str):
        kw_list = [kw_raw.strip()] if kw_raw.strip() else []
    elif isinstance(kw_raw, (list, tuple)):
        kw_list = [s.strip() for s in kw_raw if s and s.strip()]
    else:
        continue
    
    for kw in kw_list:
        kw_year_count[kw][py] += 1
        year_total[py] += 1

kw_total = {kw: sum(yr_count.values()) for kw, yr_count in kw_year_count.items()}
sorted_kw = sorted(kw_total.items(), key=lambda x: x[1], reverse=True)

all_years = sorted(year_total.keys())
print(f"\n共发现 {len(kw_total)} 个不同的关键词 (Keyword Plus)")
print(f"年份范围: {all_years[0]} - {all_years[-1]}")
print(f"收录数据共 {len(all_years)} 年")

# ===================== 3. Kleinberg 爆发检测算法 =====================
def kleinberg_burst_detection(counts, years, s=2, gamma=1.0, min_burst_years=2):
    """
    Kleinberg (2002) burst detection algorithm - standard implementation
    
    Uses a two-state automaton (base state + burst state) with Poisson emission probabilities.
    States: state 0 = background rate, state i>0 = burst rate = background * s^i
    
    Parameters:
        counts:  annual count values (original or normalized)
        years:   corresponding year list
        s:       state transition scale factor (default 2)
        gamma:   state transition cost parameter (default 1.0)
        min_burst_years: minimum burst duration
    """
    n = len(counts)
    if n < 3:
        return []
    
    x = np.array(counts, dtype=float)
    base_rate = np.mean(x)
    
    if base_rate <= 0:
        return []
    
    max_states = min(10, max(3, int(math.log(max(x) / max(base_rate, 1e-10), s)) + 3))
    
    lambdas = np.array([base_rate * (s ** j) for j in range(max_states)])
    
    def emission_cost(val, lam):
        if lam <= 0:
            return float('inf')
        if val < 0:
            val = 0
        log_prob = val * math.log(lam) - lam - math.lgamma(val + 1)
        return -log_prob
    
    emit_cost = np.zeros((n, max_states))
    for t in range(n):
        for j in range(max_states):
            emit_cost[t, j] = emission_cost(x[t], lambdas[j])
    
    trans_base = gamma * math.log(n) if n > 1 else 0
    trans_cost = np.zeros((max_states, max_states))
    for i in range(max_states):
        for j in range(i+1, max_states):
            trans_cost[i, j] = (j - i) * trans_base
    
    dp = np.full((n, max_states), float('inf'))
    bt = np.full((n, max_states), -1, dtype=int)
    
    for j in range(max_states):
        dp[0, j] = emit_cost[0, j]
    
    for t in range(1, n):
        for j in range(max_states):
            costs = dp[t-1, :] + trans_cost[:, j]
            best_i = np.argmin(costs)
            dp[t, j] = costs[best_i] + emit_cost[t, j]
            bt[t, j] = best_i
    
    best_final = np.argmin(dp[n-1, :])
    states = np.zeros(n, dtype=int)
    states[n-1] = best_final
    for t in range(n-1, 0, -1):
        states[t-1] = bt[t, states[t]]
    
    bursts = []
    in_burst = False
    burst_start = -1
    
    for t in range(n):
        if states[t] > 0 and not in_burst:
            in_burst = True
            burst_start = t
        elif (states[t] == 0 or t == n-1) and in_burst:
            t_end = t if (t == n-1 and states[t] > 0) else t - 1
            burst_len = t_end - burst_start + 1
            
            if burst_len >= min_burst_years:
                burst_vals = x[burst_start:t_end+1]
                avg_val = np.mean(burst_vals)
                intensity = avg_val / base_rate if base_rate > 0 else 0
                
                bursts.append({
                    'start_year': years[burst_start],
                    'end_year': years[t_end],
                    'duration': burst_len,
                    'intensity': round(intensity, 2),
                    'max_state': int(np.max(states[burst_start:t_end+1])),
                    'avg_count': round(avg_val, 1)
                })
            
            in_burst = False
            burst_start = -1
    
    return bursts


# ===================== 4. 执行检测 =====================
print("\n\n正在执行 Kleinberg 爆发检测（标准化计数法）...")
print("=" * 70)

# 分析时段：排除早期数据稀疏年份，聚焦2008年之后
ANALYSIS_START = 2008
years_from = [y for y in all_years if y >= ANALYSIS_START]
if years_from:
    analysis_years = list(range(min(years_from), max(years_from) + 1))
else:
    analysis_years = all_years

print(f"分析时段: {analysis_years[0]} ~ {analysis_years[-1]}，共 {len(analysis_years)} 年")

# 计算参考总发文量（取中位数）
year_totals_analysis = [year_total.get(y, 0) for y in analysis_years]
ref_total = np.median(year_totals_analysis)
print(f"参考年总发文量 (中位数): {int(ref_total)} 篇")

# 关键词比学科类别更多，设定稍高的筛选门槛
MIN_RECORDS = 50     # 至少出现50次（排除低频词）
MIN_YEARS = 6        # 至少覆盖6年

all_bursts = []

for kw_name, total in sorted_kw:
    if total < MIN_RECORDS:
        continue
    
    yr_counts = kw_year_count[kw_name]
    
    # 构建标准化计数序列
    norm_counts = []
    for y in analysis_years:
        raw_count = yr_counts.get(y, 0)
        total_y = year_total.get(y, 0)
        
        if total_y > 0 and raw_count > 0:
            # 标准化：按参考总发文量缩放
            norm_c = raw_count * (ref_total / total_y)
        else:
            norm_c = 0
        norm_counts.append(norm_c)
    
    years_with_data = sum(1 for c in norm_counts if c > 0)
    if years_with_data < MIN_YEARS:
        continue
    
    bursts = kleinberg_burst_detection(
        norm_counts, analysis_years,
        s=2, gamma=1.2, min_burst_years=2
    )
    
    if bursts:
        for b in bursts:
            # 计算原始发文量（爆发期内实际年均）
            burst_start_idx = analysis_years.index(b['start_year'])
            burst_end_idx = analysis_years.index(b['end_year'])
            raw_counts_burst = [yr_counts.get(analysis_years[i], 0) 
                                for i in range(burst_start_idx, burst_end_idx + 1)]
            
            all_bursts.append({
                '关键词': kw_name,
                '爆发开始年份': b['start_year'],
                '爆发结束年份': b['end_year'],
                '持续年数': b['duration'],
                '爆发强度': b['intensity'],
                '爆发状态等级': b['max_state'],
                '爆发期年均标准化计数': b['avg_count'],
                '爆发期原始年均发文': round(np.mean(raw_counts_burst), 1),
                '关键词总记录数': total
            })
            print(f"  {kw_name:<45} {b['start_year']}-{b['end_year']}  "
                  f"[强度={b['intensity']:.2f}x, 等级={b['max_state']}, "
                  f"标准化={b['avg_count']:.0f}/年]")

# ===================== 5. 输出 =====================
if all_bursts:
    df_bursts = pd.DataFrame(all_bursts)
    df_bursts = df_bursts.sort_values(['爆发强度', '关键词总记录数'], ascending=[False, False])
    
    print(f"\n\n{'='*70}")
    print(f"Kleinberg 爆发检测结果 ({analysis_years[0]}-{analysis_years[-1]})")
    print(f"共检测到 {len(df_bursts)} 个爆发事件")
    print(f"\n按爆发强度排序:")
    print(f"{'='*70}")
    
    display_cols = ['关键词', '爆发开始年份', '爆发结束年份', '持续年数', 
                    '爆发强度', '爆发状态等级', '爆发期年均标准化计数', '关键词总记录数']
    print(df_bursts[display_cols].to_string(index=False))
    
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\关键词爆发检测.csv"
    df_bursts.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: {output_path}")
    
    print(f"\n\n{'='*70}")
    print(f"按时间线排列:")
    print(f"{'='*70}")
    df_time = df_bursts.sort_values(['爆发开始年份', '爆发强度'], ascending=[True, False])
    print(df_time[display_cols].to_string(index=False))
    
else:
    print("\n未检测到爆发事件。")

print("\n完成！")
