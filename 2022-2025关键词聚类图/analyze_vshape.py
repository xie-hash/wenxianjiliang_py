# -*- coding: utf-8 -*-
"""关键词三类独立分类 + 重分析"""
import pandas as pd, numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

BASE = r'c:\Users\谢\Desktop\vscodepj\文献计量学\2022-2025关键词聚类图'
FILES = {2022: f'{BASE}\\2022.xlsx',2023: f'{BASE}\\2023.xlsx',2024: f'{BASE}\\2024.xlsx',2025: f'{BASE}\\2025.xlsx'}
METRICS = ['Betweenness','Closeness','PageRank']

all_scores = {}
for year, fp in FILES.items():
    df = pd.read_excel(fp, sheet_name='Data')
    scaler = StandardScaler()
    z = scaler.fit_transform(df[METRICS])
    pca = PCA()
    pc = pca.fit_transform(z)
    c = (pc[:,0]-pc[:,0].min())/(pc[:,0].max()-pc[:,0].min())*100
    all_scores[str(year)] = pd.DataFrame({'Node':df['Node'],str(year):c})

nodes = set()
for v in all_scores.values(): nodes.update(v['Node'])
merged = pd.DataFrame({'Node':list(nodes)})
for y in ['2022','2023','2024','2025']:
    merged = merged.merge(all_scores[y], on='Node', how='left')

# ============ 三类独立分类（无优先级，独立判断） ============

# 条件A: 核心支柱 - 三年或以上得分>=50
def is_core(row):
    return sum(1 for y in ['2022','2023','2024','2025'] if pd.notna(row[y]) and row[y]>=50) >= 3

# 条件B: 上升新星 - 连续两年上升（2023→2024上涨, 且2024→2025上涨）
def is_rising(row):
    return (pd.notna(row['2023']) and pd.notna(row['2024']) and pd.notna(row['2025'])
            and row['2024'] > row['2023'] and row['2025'] > row['2024'])

# 条件C: V型反弹 - 先降后升 (2024相对前期下降, 2024→2025反弹≥10分)
def is_vshape(row):
    if not (pd.notna(row['2024']) and pd.notna(row['2025'])):
        return False
    rebound = row['2025'] > row['2024'] and (row['2025'] - row['2024']) >= 10
    if not rebound:
        return False
    if pd.notna(row['2023']) and row['2024'] < row['2023']:
        return True
    if pd.notna(row['2022']) and row['2024'] < row['2022']:
        return True
    return False

core_nodes = set(merged[merged.apply(is_core,axis=1)]['Node'].tolist())
rising_nodes = set(merged[merged.apply(is_rising,axis=1)]['Node'].tolist())
vshape_nodes = set(merged[merged.apply(is_vshape,axis=1)]['Node'].tolist())

# ============ 输出到CSV ============
OUTPUT = BASE  # 保存到同一目录

# 辅助函数：获取关键词的4年得分
def get_row_data(node):
    r = merged[merged['Node']==node].iloc[0]
    return [r[y] for y in ['2022','2023','2024','2025']]

# 1. 各分类详细信息
def save_category_csv(name, nodes, extra_cols=None):
    rows = []
    for n in sorted(nodes):
        scores = get_row_data(n)
        row = {'Node': n, '2022': scores[0], '2023': scores[1], '2024': scores[2], '2025': scores[3]}
        if extra_cols:
            row.update(extra_cols(n, scores))
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(f'{OUTPUT}\\{name}.csv', index=False, encoding='utf-8-sig')
    print(f'  ✓ 已保存: {name}.csv ({len(rows)}条)')

print('\n保存CSV文件...')
save_category_csv('A-核心支柱型', core_nodes)
save_category_csv('B-上升新星型', rising_nodes)
save_category_csv('C-V型反弹型', vshape_nodes,
                  lambda n,s: {'涨幅': round(s[3]-s[2], 1)})

# 2. 重叠分析表
overlap_ab = core_nodes & rising_nodes
overlap_ac = core_nodes & vshape_nodes
overlap_bc = rising_nodes & vshape_nodes
overlap_abc = core_nodes & rising_nodes & vshape_nodes
only_core = core_nodes - rising_nodes - vshape_nodes
only_rising = rising_nodes - core_nodes - vshape_nodes
only_vshape = vshape_nodes - core_nodes - rising_nodes

overlap_rows = []
for label, nodes in [('仅A-核心支柱', only_core), ('仅B-上升新星', only_rising),
                      ('仅C-V型反弹', only_vshape), ('A∩B', overlap_ab),
                      ('A∩C', overlap_ac), ('B∩C', overlap_bc),
                      ('A∩B∩C', overlap_abc)]:
    for n in sorted(nodes):
        scores = get_row_data(n)
        overlap_rows.append({
            '归属类别': label, 'Node': n,
            '2022': scores[0], '2023': scores[1], '2024': scores[2], '2025': scores[3],
            '2025-2024涨幅': round(scores[3]-scores[2], 1) if pd.notna(scores[3]) and pd.notna(scores[2]) else None
        })

df_overlap = pd.DataFrame(overlap_rows)
df_overlap.to_csv(f'{OUTPUT}\\重叠分析.csv', index=False, encoding='utf-8-sig')
print(f'  ✓ 已保存: 重叠分析.csv ({len(overlap_rows)}条)')

# 3. 汇总统计
summary = pd.DataFrame([
    {'分类': 'A-核心支柱型', '数量': len(core_nodes), '标准': '三年或以上得分≥50'},
    {'分类': 'B-上升新星型', '数量': len(rising_nodes), '标准': '2023→2024且2024→2025连续两年上升'},
    {'分类': 'C-V型反弹型', '数量': len(vshape_nodes), '标准': '先降后升且反弹≥10分'},
    {'分类': '仅A(唯一核心支柱)', '数量': len(only_core), '标准': ''},
    {'分类': '仅B(唯一上升新星)', '数量': len(only_rising), '标准': ''},
    {'分类': '仅C(唯一V型反弹)', '数量': len(only_vshape), '标准': ''},
    {'分类': 'A∩B', '数量': len(overlap_ab), '标准': ''},
    {'分类': 'A∩C', '数量': len(overlap_ac), '标准': ''},
    {'分类': 'B∩C', '数量': len(overlap_bc), '标准': ''},
    {'分类': 'A∩B∩C', '数量': len(overlap_abc), '标准': ''},
])
summary.to_csv(f'{OUTPUT}\\分类统计摘要.csv', index=False, encoding='utf-8-sig')
print(f'  ✓ 已保存: 分类统计摘要.csv')

# ============ 终端简要输出 ============
print(f'\n{"="*50}')
print(f'  分类结果摘要')
print(f'{"="*50}')
print(f'  A类(核心支柱): {len(core_nodes)}个')
print(f'  B类(上升新星): {len(rising_nodes)}个')
print(f'  C类(V型反弹):  {len(vshape_nodes)}个')
print(f'  仅A: {len(only_core)} | 仅B: {len(only_rising)} | 仅C: {len(only_vshape)}')
print(f'  A∩B: {len(overlap_ab)} | A∩C: {len(overlap_ac)} | B∩C: {len(overlap_bc)} | A∩B∩C: {len(overlap_abc)}')
print(f'  所有CSV文件已保存至: {OUTPUT}')
