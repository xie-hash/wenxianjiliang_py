# -*- coding: utf-8 -*-
"""
2022-2025 关键词综合得分 + 三类趋势分类分析
方法：Z-score标准化 + 主成分分析(PCA)

三类分类法（文献计量学专家建议）：
  A. 核心支柱型(Core Pillars): 三年或以上综合得分≥50
  B. 上升新星型(Rising Stars): 连续三年综合得分上涨
  C. V型反弹型(V-shaped Recovery): 先降后升，2024→2025大幅反弹
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置 ====================
BASE_DIR = r'c:\Users\谢\Desktop\vscodepj\文献计量学\2022-2025关键词聚类图'
FILES = {
    2022: f'{BASE_DIR}\\2022.xlsx',
    2023: f'{BASE_DIR}\\2023.xlsx',
    2024: f'{BASE_DIR}\\2024.xlsx',
    2025: f'{BASE_DIR}\\2025.xlsx',
}
SHEET_NAME = 'Data'
METRICS = ['Betweenness', 'Closeness', 'PageRank']
OUTPUT_FILE = f'{BASE_DIR}\\2022-2025_三类趋势分类分析.xlsx'

# ==================== 第一步：计算每年综合得分 ====================
print("=" * 70)
print("  2022-2025 关键词综合得分 + 三类趋势分类分析")
print("  分类方案：核心支柱型 | 上升新星型 | V型反弹型")
print("=" * 70)

all_scores = {}

for year, filepath in FILES.items():
    print(f"\n  【{year}年】PCA计算...")
    
    df = pd.read_excel(filepath, sheet_name=SHEET_NAME)
    metrics_data = df[METRICS]
    
    scaler = StandardScaler()
    z_scores = scaler.fit_transform(metrics_data)
    
    pca = PCA()
    pca_scores = pca.fit_transform(z_scores)
    
    pc1 = pca_scores[:, 0]
    pc1_min, pc1_max = pc1.min(), pc1.max()
    composite = (pc1 - pc1_min) / (pc1_max - pc1_min) * 100
    
    year_df = pd.DataFrame({
        'Node': df['Node'],
        'Cluster': df['Cluster'],
        '综合得分': composite
    })
    all_scores[year] = year_df
    
    ev_ratio = pca.explained_variance_ratio_[0] * 100
    print(f"    PC1解释方差: {ev_ratio:.2f}%")

# ==================== 第二步：合并宽表 ====================
print(f"\n{'=' * 70}")
print("  ★ 合并四年结果 ★")
print("=" * 70)

all_nodes = set()
for year_df in all_scores.values():
    all_nodes.update(year_df['Node'].tolist())

merged = pd.DataFrame({'Node': list(all_nodes)})
for year in [2022, 2023, 2024, 2025]:
    year_df = all_scores[year]
    year_df = year_df.rename(columns={'综合得分': f'{year}_综合得分', 'Cluster': f'{year}_Cluster'})
    merged = merged.merge(year_df[['Node', f'{year}_综合得分', f'{year}_Cluster']], on='Node', how='left')

# ==================== 第三步：三类分类 ====================
print("\n  【三类分类标准】")
print("  A. 核心支柱型: 三年或以上综合得分 ≥ 50")
print("  B. 上升新星型: 连续三年综合得分上涨")
print("  C. V型反弹型:  2024年相对前期下降，2024→2025显著回升(≥10分)")

# --- 分类A: 核心支柱型 ---
def is_core(row):
    count = sum(1 for y in [2022, 2023, 2024, 2025] 
                if pd.notna(row[f'{y}_综合得分']) and row[f'{y}_综合得分'] >= 50)
    return count >= 3

merged['分类A_核心支柱'] = merged.apply(is_core, axis=1)

# --- 分类B: 上升新星型 ---
def is_rising(row):
    # 检查2022→2023→2024 或 2023→2024→2025 连续三年上涨
    c1 = (pd.notna(row['2022_综合得分']) and pd.notna(row['2023_综合得分']) and pd.notna(row['2024_综合得分'])
          and row['2023_综合得分'] > row['2022_综合得分'] and row['2024_综合得分'] > row['2023_综合得分'])
    c2 = (pd.notna(row['2023_综合得分']) and pd.notna(row['2024_综合得分']) and pd.notna(row['2025_综合得分'])
          and row['2024_综合得分'] > row['2023_综合得分'] and row['2025_综合得分'] > row['2024_综合得分'])
    return c1 or c2

merged['分类B_上升新星'] = merged.apply(is_rising, axis=1)

# --- 分类C: V型反弹型 ---
def is_vshape(row):
    has_2024 = pd.notna(row['2024_综合得分'])
    has_2025 = pd.notna(row['2025_综合得分'])
    if not (has_2024 and has_2025):
        return False
    
    rebound = row['2025_综合得分'] > row['2024_综合得分'] and (row['2025_综合得分'] - row['2024_综合得分']) >= 10
    if not rebound:
        return False
    
    drop_from_peak = False
    if pd.notna(row['2023_综合得分']) and row['2024_综合得分'] < row['2023_综合得分']:
        drop_from_peak = True
    elif pd.notna(row['2022_综合得分']) and row['2024_综合得分'] < row['2022_综合得分']:
        drop_from_peak = True
    
    # 排除已归入A或B类的
    already_classified = is_core(row) or is_rising(row)
    return rebound and drop_from_peak and not already_classified

merged['分类C_V型反弹'] = merged.apply(is_vshape, axis=1)

# 汇总
merged['最终分类'] = ''
for idx, row in merged.iterrows():
    labels = []
    if row['分类A_核心支柱']: labels.append('A-核心支柱')
    if row['分类B_上升新星']: labels.append('B-上升新星')
    if row['分类C_V型反弹']: labels.append('C-V型反弹')
    if not labels: labels.append('—')
    merged.at[idx, '最终分类'] = ' | '.join(labels)

# ==================== 第四步：输出结果 ====================
core_nodes = merged[merged['分类A_核心支柱']]['Node'].tolist()
rising_nodes = merged[merged['分类B_上升新星']]['Node'].tolist()
vshape_nodes = merged[merged['分类C_V型反弹']]['Node'].tolist()

print(f"\n{'=' * 70}")
print(f"  ★ 分类结果 ★")
print(f"{'=' * 70}")
print(f"\n  A. 核心支柱型: {len(core_nodes)} 个")
print(f"     {' | '.join(core_nodes)}")
print(f"\n  B. 上升新星型: {len(rising_nodes)} 个")
for n in rising_nodes:
    r = merged[merged['Node']==n].iloc[0]
    s = [f"{r[f'{y}_综合得分']:.1f}" for y in [2022,2023,2024,2025]]
    print(f"     {n:<25} {' → '.join(s)}")
print(f"\n  C. V型反弹型: {len(vshape_nodes)} 个")
for n in vshape_nodes:
    r = merged[merged['Node']==n].iloc[0]
    s = [f"{r[f'{y}_综合得分']:.1f}" for y in [2022,2023,2024,2025]]
    print(f"     {n:<25} {s}  升幅={r['2025_综合得分']-r['2024_综合得分']:+.1f}")

# ==================== 第五步：生成趋势标记 ====================
score_matrix = merged[['Node'] + [f'{y}_综合得分' for y in [2022, 2023, 2024, 2025]]].copy()

score_matrix['趋势标记'] = ''
for idx, row in score_matrix.iterrows():
    scores = [row[f'{y}_综合得分'] for y in [2022, 2023, 2024, 2025]]
    markers = []
    for i in range(3):
        if pd.notna(scores[i]) and pd.notna(scores[i+1]):
            if scores[i+1] > scores[i]: markers.append('↑')
            elif scores[i+1] < scores[i]: markers.append('↓')
            else: markers.append('→')
        else: markers.append('-')
    score_matrix.at[idx, '趋势标记'] = '  '.join(markers)

score_matrix['分类'] = merged['最终分类'].values
score_matrix = score_matrix.sort_values('2025_综合得分', ascending=False).reset_index(drop=True)

print(f"\n\n{'─' * 95}")
print(f"{'Node':<25} {'2022':>8} {'2023':>8} {'2024':>8} {'2025':>8} {'趋势':<12} {'分类'}")
print(f"{'─' * 95}")
for _, row in score_matrix.iterrows():
    scores_str = ""
    for y in [2022, 2023, 2024, 2025]:
        v = row[f'{y}_综合得分']
        if pd.notna(v): scores_str += f"{v:>8.1f}"
        else: scores_str += f"{'N/A':>8}"
    print(f"{row['Node']:<25} {scores_str} {row['趋势标记']:<12} {row['分类']}")

# ==================== 第六步：保存到Excel ====================
output_matrix = score_matrix.copy()
output_matrix.columns = ['Node', '2022得分', '2023得分', '2024得分', '2025得分', '趋势', '分类']

# 各分类子表
core_df = merged[merged['分类A_核心支柱']][['Node'] + [f'{y}_综合得分' for y in [2022,2023,2024,2025]]].copy()
core_df.columns = ['Node', '2022得分', '2023得分', '2024得分', '2025得分']

rising_df = merged[merged['分类B_上升新星']][['Node'] + [f'{y}_综合得分' for y in [2022,2023,2024,2025]]].copy()
rising_df.columns = ['Node', '2022得分', '2023得分', '2024得分', '2025得分']

vshape_df = merged[merged['分类C_V型反弹']][['Node'] + [f'{y}_综合得分' for y in [2022,2023,2024,2025]]].copy()
vshape_df.columns = ['Node', '2022得分', '2023得分', '2024得分', '2025得分']

# 统计摘要
summary_data = {
    '分类': ['A-核心支柱型', 'B-上升新星型', 'C-V型反弹型'],
    '数量': [len(core_df), len(rising_df), len(vshape_df)],
    '判断标准': [
        '三年或以上综合得分 ≥ 50',
        '连续三年综合得分上涨（含2022→2023→2024或2023→2024→2025）',
        '2024年相对前期下降，2024→2025反弹幅度 ≥ 10分'
    ],
    '关键词': [
        '、'.join(core_nodes),
        '、'.join(rising_nodes),
        '、'.join(vshape_nodes)
    ]
}
summary_df = pd.DataFrame(summary_data)

with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    output_matrix.to_excel(writer, sheet_name='2022-2025综合得分矩阵', index=False)
    core_df.to_excel(writer, sheet_name='A-核心支柱型', index=False)
    rising_df.to_excel(writer, sheet_name='B-上升新星型', index=False)
    vshape_df.to_excel(writer, sheet_name='C-V型反弹型', index=False)
    summary_df.to_excel(writer, sheet_name='统计摘要', index=False)
    
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = max(len(str(cell.value or '')) for cell in column)
            worksheet.column_dimensions[column[0].column_letter].width = max_length + 2

print(f"\n\n✓ 详细结果已保存至: {OUTPUT_FILE}")
print(f"  Sheet 1: 2022-2025综合得分矩阵")
print(f"  Sheet 2: A-核心支柱型 (11个)")
print(f"  Sheet 3: B-上升新星型 (3个)")
print(f"  Sheet 4: C-V型反弹型 (9个)")
print(f"  Sheet 5: 统计摘要")
