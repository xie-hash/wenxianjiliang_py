# -*- coding: utf-8 -*-
"""
潜力关键词共现邻居查询工具

功能：
  1. 从bib文件中提取所有关键词（DE + ID字段）
  2. 计算关键词两两之间的共现强度
  3. 对于用户指定的关键词，输出：同簇中共现强度最高的TOP N个邻居

输入（在下方 INPUT 区域自行修改）：
  - target_keywords: 要查询的关键词列表
  - top_n: 每个关键词保留的邻居数量
  - year: 使用哪一年的Cluster归属（2022/2023/2024/2025）

输出：
  - 终端打印：每个关键词的同簇TOP N邻居
  - Excel文件：保存完整结果
"""

import pandas as pd
from collections import defaultdict
import os

# ==================== 导入metaknowledge ====================
try:
    import metaknowledge as mk
except ImportError:
    print("请先安装 metaknowledge: pip install metaknowledge")
    exit()

# ==================== 配置 ====================
BASE_DIR = r'c:\Users\谢\Desktop\vscodepj\文献计量学'
OUTPUT_DIR = r'c:\Users\谢\Desktop\vscodepj\文献计量学\2022-2025关键词聚类图'

BIB_FILES = [
    f"{BASE_DIR}\\bib文件\\savedrecs (1).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (2).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (3).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (4).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (5).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (6).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (7).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs (8).txt",
    f"{BASE_DIR}\\bib文件\\savedrecs.txt",
]

# ==================== ◇◇◇ 输入区域（自行修改）◇◇◇ ====================

target_keywords = [
    'cancer', 'mechanisms', 'binding', 'design', 'discovery', 'docking', 'drug discovery', 'identification',
    'in-vitro', 'infection', 'inhibitors', 'molecular docking', 'protein', 'binding', 'coronavirus', 'covid-19',
    'derivatives', 'design', 'discovery', 'docking', 'efficacy', 'expression', 'identification', 'in-vitro',
    'inhibition', 'prediction', 'replication', 'virus'
]

TOP_N = 10        # 每个关键词保留的TOP N个邻居
YEAR = 2025       # 使用哪一年的聚类归属

# ==================== ◇◇◇ 输入结束 ◇◇◇ ====================

# 关键词标准化映射
NORMALIZE_MAP = {
    "Sars-Cov-2": "sars-cov-2", "SARS-CoV-2": "sars-cov-2",
    "Covid-19": "covid-19", "COVID-19": "covid-19", "COVID 19": "covid-19",
    "Molecular docking": "molecular docking", "Molecular Docking": "molecular docking",
    "Molecular dynamics": "molecular-dynamics", "Molecular Dynamics": "molecular-dynamics",
    "Molecular-dynamics": "molecular-dynamics",
    "In-vitro": "in-vitro", "In vitro": "in-vitro",
    "Molecular_docking": "molecular docking",
    "Antiviral": "antiviral activity", "Anti-viral": "antiviral activity",
    "Antiviral activity": "antiviral activity",
    "Drug design": "design", "Drug Design": "design",
    "Force field": "force-field", "Force-field": "force-field", "Force Field": "force-field",
    "Crystal structure": "crystal-structure", "Crystal Structure": "crystal-structure",
    "Crystal-structure": "crystal-structure",
    "Drug discovery": "drug discovery", "Drug Discovery": "drug discovery",
    "Biological evaluation": "biological evaluation",
    "Antiviral agents": "antiviral activity",
}

def normalize_keyword(kw):
    kw = kw.strip().strip('"').strip("'")
    if not kw or len(kw) <= 1:
        return None
    if kw in NORMALIZE_MAP:
        return NORMALIZE_MAP[kw]
    return kw.lower()

# ==================== 第一步：读取bib ====================
print("=" * 60)
print("  关键词共现邻居分析")
print("=" * 60)
print("\n读取bib文件...")
rc = mk.RecordCollection()
for f in BIB_FILES:
    if os.path.exists(f):
        rc += mk.RecordCollection(f)
        print(f"  已加载: {os.path.basename(f)}，总记录数: {len(rc)}")
print(f"\n总文献数: {len(rc)}")

# ==================== 第二步：提取关键词 ====================
print("\n提取关键词（DE字段 + ID字段）...")

keyword_papers = defaultdict(set)
paper_keywords = {}

for i, record in enumerate(rc):
    try:
        all_kws = []
        for field in ['DE', 'ID']:
            raw = record.get(field, None)
            if raw is not None and raw:
                if isinstance(raw, list):
                    for kw in raw:
                        nk = normalize_keyword(str(kw))
                        if nk:
                            all_kws.append(nk)
                elif isinstance(raw, str):
                    for kw in raw.split(';'):
                        nk = normalize_keyword(kw)
                        if nk:
                            all_kws.append(nk)
        all_kws = list(set(all_kws))
        if len(all_kws) >= 2:
            pid = f"p_{i}"
            paper_keywords[pid] = all_kws
            for kw in all_kws:
                keyword_papers[kw].add(pid)
    except Exception:
        continue

print(f"  含关键词的文献数: {len(paper_keywords)}")
print(f"  不同关键词总数: {len(keyword_papers)}")

# ==================== 第三步：构建共现矩阵 ====================
print("\n计算共现强度...")
cooccur = defaultdict(lambda: defaultdict(int))
for pid, kws in paper_keywords.items():
    for i in range(len(kws)):
        for j in range(i + 1, len(kws)):
            a, b = kws[i], kws[j]
            if a != b:
                cooccur[a][b] += 1
                cooccur[b][a] += 1
print(f"  共现边数: {sum(len(v) for v in cooccur.values()) // 2}")

# ==================== 第四步：读取聚类归属 ====================
print(f"\n读取{YEAR}年关键词聚类归属...")
cluster_file = f"{OUTPUT_DIR}\\{YEAR}.xlsx"
df_cluster = pd.read_excel(cluster_file, sheet_name='Data')
kw_to_cluster = {}
for _, row in df_cluster.iterrows():
    kw_to_cluster[str(row['Node']).strip().lower()] = row['Cluster']
print(f"  已加载 {len(kw_to_cluster)} 个关键词 (共{df_cluster['Cluster'].nunique()}个簇)")

# ==================== 第五步：查询 ====================
print(f"\n{'=' * 60}")
print(f"  查询结果：同簇TOP{TOP_N}共现邻居")
print(f"{'=' * 60}")

results = []

for target in target_keywords:
    tl = target.strip().lower()
    if tl not in kw_to_cluster:
        print(f"\n  '{target}' 不在{str(YEAR)}年列表中，跳过")
        continue

    tc = kw_to_cluster[tl]
    print(f"\n  '{target}' (Cluster {tc}):")

    # 该簇所有关键词
    cluster_kws = {kw for kw, cl in kw_to_cluster.items() if cl == tc}

    # 共现邻居
    neighbors = cooccur.get(tl, {})

    # 筛选同簇
    same = [(n, w) for n, w in neighbors.items()
            if n in cluster_kws and n != tl and n in kw_to_cluster]
    same.sort(key=lambda x: x[1], reverse=True)

    if not same:
        print("    (同簇内无共现邻居)")
        continue

    for rank, (neighbor, weight) in enumerate(same[:TOP_N], 1):
        nc = kw_to_cluster.get(neighbor, '?')
        print(f"    {rank}. {neighbor:<25} (Cluster {nc})  共现: {weight}次")
        results.append({
            '目标关键词': target,
            '目标簇': tc,
            '排名': rank,
            '邻居关键词': neighbor,
            '邻居簇': nc,
            '共现次数': weight
        })

# ==================== 第六步：保存 ====================
df_result = pd.DataFrame(results)
if len(df_result) > 0:
    out = f"{OUTPUT_DIR}\\共现邻居查询结果.xlsx"
    df_result.to_excel(out, index=False)
    print(f"\n结果已保存至: {out}")
else:
    print("\n无结果")

print(f"\n{'─' * 40}")
print(f"  查询: {len(target_keywords)} 个关键词")
print(f"  结果: {df_result['目标关键词'].nunique() if len(df_result) > 0 else 0} 个有效")
print(f"  共 {len(df_result)} 条共现对")
