"""
参考文献 (CR 字段) 爆发检测
===========================
方法：Kleinberg (2002) 爆发检测算法

基于文章的被引信息（CR 字段），分析参考文献的爆发强度。
对于每篇施引文章，使用其 PY（出版年份）作为引用发生的年份，
统计每条参考文献在逐年被引次数的时间序列。

改进：用标准化计数替代原始被引次数作为算法输入。
  原始被引次数因2020年后总发文量激增，导致所有参考文献的爆发集中检测在近年。
  
  标准化方法：对每条参考文献每年的原始被引次数，按参考总发文量（中位数）缩放
    标准化计数 = 原始计数 * (参考总发文量 / 当年总发文量)
  
参考文献标识方式：第一作者姓氏, 出版年份, V卷号, P起始页码
  例如："Alam MA, 2016, V7, P1132"

输出：参考文献爆发检测.csv
"""

import metaknowledge as mk
import pandas as pd
import numpy as np
from collections import defaultdict
import math
import os
import re

# 忽略 metaknowledge 的 Citation 解析警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="metaknowledge")

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

# ===================== 2. 从 CR 字段解析参考文献 =====================

def get_ref_key(citation):
    """
    从 metaknowledge 的 Citation 对象构建参考文献唯一标识。
    
    Citation 对象具有以下属性:
      author: 第一作者 (如 "Andrei G")
      year: 出版年份 (如 1993)
      journal: 期刊名称 (如 "ANTIVIR RES")
      V: 卷号 (如 "V22")
      P: 页码 (如 "P45")
      DOI: DOI号
      original: 原始字符串
    
    返回: (key, ref_year) 或 None
    """
    try:
        author = citation.author
        year = citation.year
        vol = citation.V
        page = citation.P
    except Exception:
        return None
    
    # 验证必要的字段
    if not author or not year or not vol:
        return None
    
    try:
        year = int(year)
    except (ValueError, TypeError):
        return None
    
    # 构建唯一标识: "作者, 年份, V卷号, P页码"
    vol_str = str(vol).strip()
    if page and str(page).strip():
        key = f"{author}, {year}, {vol_str}, {page}"
    else:
        key = f"{author}, {year}, {vol_str}"
    
    return (key, year)


print("\n正在解析参考文献 (CR 字段 - metaknowledge Citation 对象)...")
print("=" * 70)

ref_year_count = defaultdict(lambda: defaultdict(int))
citing_year_total = defaultdict(int)
ref_info = {}
ref_examples = {}

total_records = len(rc)
processed = 0

for rec in rc:
    cr_raw = rec.get("CR")
    py_raw = rec.get("PY")
    
    if not cr_raw or not py_raw:
        continue
    
    try:
        citing_year = int(py_raw)
    except (ValueError, TypeError):
        continue
    
    # CR 字段在 metaknowledge 中已解析为 Citation 对象列表
    if isinstance(cr_raw, (list, tuple)):
        citations = cr_raw
    else:
        continue
    
    for citation in citations:
        result = get_ref_key(citation)
        if result is None:
            continue
        
        key, ref_year = result
        ref_year_count[key][citing_year] += 1
        
        if key not in ref_info:
            ref_info[key] = ref_year
        if key not in ref_examples:
            # 保存原始字符串前120字符
            orig = citation.original if hasattr(citation, 'original') else str(citation)
            ref_examples[key] = orig[:120]
    
    citing_year_total[citing_year] += 1
    
    processed += 1
    if processed % 1000 == 0:
        print(f"  已处理 {processed}/{total_records} 条记录...")

print(f"\n完成解析！")
print(f"共处理 {processed} 条有 CR 字段的记录")
print(f"共发现 {len(ref_year_count)} 条不同的参考文献")

# ===================== 3. 筛选高频参考文献 =====================
# 绝对明确：被引次数极少的文章不可能有统计上有意义的"爆发"。
# Kleinberg 算法检测的是相对增长率的异常，但在总被引 < 20 的情况下，
# 1-2 次被引的变化在标准化后会被极度放大，产生虚假爆发。
# 因此我们设置：
#   1) 总被引次数 >= 20 次（绝对最低门槛）
#   2) 至少在某一年被引 >= 3 次（排除偶然引用）
#   3) 至少覆盖 4 年 

MIN_CITATIONS = 20    # 总被引绝对门槛
MIN_PEAK_YEAR = 3     # 单年最高被引次数门槛

ref_total = {}
for key, yr_counts in ref_year_count.items():
    ref_total[key] = sum(yr_counts.values())

# 先按绝对门槛筛选
qualified_refs = []
for key, total in ref_total.items():
    yr_counts = ref_year_count[key]
    peak = max(yr_counts.values()) if yr_counts else 0
    if total >= MIN_CITATIONS and peak >= MIN_PEAK_YEAR:
        qualified_refs.append((key, total, peak))

sorted_refs = sorted(qualified_refs, key=lambda x: x[1], reverse=True)
print(f"\n参考文献总被引范围: {sorted_refs[-1][1] if sorted_refs else 0} ~ {sorted_refs[0][1] if sorted_refs else 0}")
print(f"总被引 >= {MIN_CITATIONS} 且 单年峰值 >= {MIN_PEAK_YEAR} 的参考文献数: {len(sorted_refs)}")

all_years = sorted(citing_year_total.keys())
print(f"引用年份范围: {all_years[0]} - {all_years[-1]}")
print(f"收录数据共 {len(all_years)} 年")

# 取前 20%（从高质量候选中选取更广泛的样本）
top_ratio = 0.20
top_n = max(1, int(len(sorted_refs) * top_ratio))
top_refs = [(key, total) for key, total, peak in sorted_refs[:top_n]]
print(f"\n筛选：前 {top_ratio*100:.0f}%（共 {top_n} 条参考文献）")
print(f"最低总被引: {top_refs[-1][1]}")


# ===================== 4. Kleinberg 爆发检测算法 =====================

def kleinberg_burst_detection(counts, years, s=2, gamma=1.0, min_burst_years=2):
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


# ===================== 5. 执行爆发检测 =====================
print("\n\n正在执行 Kleinberg 爆发检测（标准化计数法）...")
print("=" * 70)

ANALYSIS_START = 2008
years_from = [y for y in all_years if y >= ANALYSIS_START]
if years_from:
    analysis_years = list(range(min(years_from), max(years_from) + 1))
else:
    analysis_years = all_years

print(f"分析时段: {analysis_years[0]} ~ {analysis_years[-1]}，共 {len(analysis_years)} 年")

year_totals_analysis = [citing_year_total.get(y, 0) for y in analysis_years]
ref_total_pub = np.median(year_totals_analysis)
print(f"参考年总发文量 (中位数): {int(ref_total_pub)} 篇")

MIN_YEARS = 4

all_bursts = []

for ref_key, total_citations in top_refs:
    yr_counts = ref_year_count[ref_key]
    
    years_with_data = sum(1 for y in analysis_years if yr_counts.get(y, 0) > 0)
    if years_with_data < MIN_YEARS:
        continue
    
    norm_counts = []
    for y in analysis_years:
        raw_count = yr_counts.get(y, 0)
        total_y = citing_year_total.get(y, 0)
        
        if total_y > 0 and raw_count > 0:
            norm_c = raw_count * (ref_total_pub / total_y)
        else:
            norm_c = 0
        norm_counts.append(norm_c)
    
    bursts = kleinberg_burst_detection(
        norm_counts, analysis_years,
        s=2, gamma=1.0, min_burst_years=2
    )
    
    if bursts:
        for b in bursts:
            burst_start_idx = analysis_years.index(b['start_year'])
            burst_end_idx = analysis_years.index(b['end_year'])
            raw_counts_burst = [yr_counts.get(analysis_years[i], 0)
                                for i in range(burst_start_idx, burst_end_idx + 1)]
            
            all_bursts.append({
                '参考文献标识': ref_key,
                '参考文献原始示例': ref_examples.get(ref_key, ''),
                '参考文献出版年份': ref_info.get(ref_key, ''),
                '爆发开始年份': b['start_year'],
                '爆发结束年份': b['end_year'],
                '持续年数': b['duration'],
                '爆发强度': b['intensity'],
                '爆发状态等级': b['max_state'],
                '爆发期年均标准化被引': b['avg_count'],
                '爆发期原始年均被引': round(np.mean(raw_counts_burst), 1),
                '参考文献总被引': total_citations
            })
            print(f"  {ref_key[:50]:<50} {b['start_year']}-{b['end_year']}  "
                  f"[强度={b['intensity']:.2f}x, 等级={b['max_state']}, "
                  f"标准化={b['avg_count']:.0f}/年, 共被引={total_citations}]")

# ===================== 6. 输出 =====================
if all_bursts:
    df_bursts = pd.DataFrame(all_bursts)
    df_bursts = df_bursts.sort_values(['爆发强度', '参考文献总被引'], ascending=[False, False])
    
    print(f"\n\n{'='*70}")
    print(f"Kleinberg 爆发检测结果 ({analysis_years[0]}-{analysis_years[-1]})")
    print(f"基于前 5% 高频参考文献，共检测到 {len(df_bursts)} 个爆发事件")
    print(f"\n按爆发强度排序:")
    print(f"{'='*70}")
    
    display_cols = ['参考文献标识', '爆发开始年份', '爆发结束年份', '持续年数',
                    '爆发强度', '爆发状态等级', '爆发期年均标准化被引', '参考文献总被引']
    print(df_bursts[display_cols].to_string(index=False))
    
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\参考文献爆发检测.csv"
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
