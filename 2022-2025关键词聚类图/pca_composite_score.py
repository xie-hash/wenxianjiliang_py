# -*- coding: utf-8 -*-
"""
文献计量学综合指标计算脚本
方法：Z-score标准化 + 主成分分析(PCA)
方法学依据：
  - Leydesdorff, L. (2007). "Betweenness centrality as an indicator..."
    Journal of the American Society for Information Science and Technology
  - Cobo, M.J. et al. (2011). "Science mapping software tools..."
    Journal of the American Society for Information Science and Technology
  - OECD (2008). "Handbook on Constructing Composite Indicators"
  - Waltman, L. & van Eck, N.J. (2013). "A smart local moving algorithm..."
    Journal of Statistical Mechanics

输入：2022.xlsx (Data工作表)
输出：2022_综合排名.xlsx
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置 ====================
INPUT_FILE = r'c:\Users\谢\Desktop\vscodepj\文献计量学\2022-2025关键词聚类图\2025.xlsx'
OUTPUT_FILE = r'c:\Users\谢\Desktop\vscodepj\文献计量学\2022-2025关键词聚类图\2025_综合排名.xlsx'
SHEET_NAME = 'Data'

# 需要标准化的指标列
METRICS = ['Betweenness', 'Closeness', 'PageRank']

# ==================== 第一步：读取数据 ====================
print("=" * 60)
print("文献计量学综合指标计算 - Z-score + PCA")
print("=" * 60)

df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
print(f"\n✓ 成功读取数据：{len(df)} 个节点")
print(f"  列名：{list(df.columns)}")

# ==================== 第二步：描述性统计 ====================
print("\n" + "-" * 60)
print("【描述性统计】")
print("-" * 60)
stats = df[METRICS].describe().T[['mean', 'std', 'min', 'max']]
stats.columns = ['均值(Mean)', '标准差(Std)', '最小值(Min)', '最大值(Max)']
print(stats.to_string(float_format=lambda x: f'{x:.6f}'))

# ==================== 第三步：Z-score标准化 ====================
print("\n" + "-" * 60)
print("【Z-score标准化】")
print("-" * 60)

scaler = StandardScaler()
z_scores = scaler.fit_transform(df[METRICS])
z_df = pd.DataFrame(z_scores, columns=[f'{col}_Z' for col in METRICS])

# 打印标准化后数据范围检查
for col in METRICS:
    z_col = f'{col}_Z'
    print(f"  {col}: 均值={z_df[z_col].mean():.6f}, 标准差={z_df[z_col].std():.6f}")

# ==================== 第四步：PCA分析 ====================
print("\n" + "-" * 60)
print("【主成分分析(PCA)】")
print("-" * 60)

pca = PCA()
pca_scores = pca.fit_transform(z_scores)

# 方差解释率
explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

print(f"\n  各主成分方差解释率 (Explained Variance Ratio):")
for i, (ev, cv) in enumerate(zip(explained_variance, cumulative_variance)):
    print(f"    PC{i+1}: {ev:.4f} ({ev*100:.2f}%) | 累计: {cv:.4f} ({cv*100:.2f}%)")

# 载荷矩阵 (component loadings = 特征向量 * sqrt(特征值))
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
print(f"\n  主成分载荷矩阵 (Component Loadings):")
loadings_df = pd.DataFrame(
    loadings,
    index=METRICS,
    columns=[f'PC{i+1}' for i in range(len(METRICS))]
)
print(loadings_df.to_string(float_format=lambda x: f'{x:.4f}'))

# 特征向量
print(f"\n  主成分特征向量 (Eigenvectors):")
eigenvectors_df = pd.DataFrame(
    pca.components_.T,
    index=METRICS,
    columns=[f'PC{i+1}' for i in range(len(METRICS))]
)
print(eigenvectors_df.to_string(float_format=lambda x: f'{x:.4f}'))

# ==================== 第五步：计算综合得分 ====================
print("\n" + "-" * 60)
print("【综合得分计算】")
print("-" * 60)

# 提取第一主成分得分作为综合得分
pc1_scores = pca_scores[:, 0]

# 方法学说明：
# PCA的第一主成分(PC1)可以解释大部分数据变异，
# 它捕捉了三个中心性指标的共同变异，
# 可以作为综合影响力的度量。

# 将综合得分缩放到0-100范围以便解释
pc1_min, pc1_max = pc1_scores.min(), pc1_scores.max()
composite_score = (pc1_scores - pc1_min) / (pc1_max - pc1_min) * 100

# 计算排名（得分越高排名越前）
rank = composite_score.argsort()[::-1].argsort() + 1

print(f"\n  PC1解释方差比例: {explained_variance[0]*100:.2f}%")
print(f"  (若>60%表示第一主成分能很好地代表综合指标)")
print(f"  综合得分范围: {composite_score.min():.2f} ~ {composite_score.max():.2f}")

# ==================== 第六步：生成输出DataFrame ====================
result_df = pd.DataFrame({
    'Node': df['Node'],
    'Cluster': df['Cluster'],
    'Betweenness_原始值': df['Betweenness'],
    'Closeness_原始值': df['Closeness'],
    'PageRank_原始值': df['PageRank'],
    'Betweenness_Z': z_df['Betweenness_Z'],
    'Closeness_Z': z_df['Closeness_Z'],
    'PageRank_Z': z_df['PageRank_Z'],
    '综合得分(PC1)': composite_score,
    '排名': rank
})

# 按排名排序
result_df = result_df.sort_values('排名').reset_index(drop=True)

print(f"\n✓ 综合排名前10的节点:")
print("-" * 80)
print(f"{'排名':<4} {'Node':<25} {'Cluster':<8} {'综合得分':<10}")
print("-" * 80)
for _, row in result_df.head(10).iterrows():
    print(f"{int(row['排名']):<4} {str(row['Node']):<25} {int(row['Cluster']):<8} {row['综合得分(PC1)']:.2f}")

# ==================== 第七步：输出统计摘要表 ====================
summary_data = {
    '统计量': [
        'PC1方差解释率(%)',
        'PC2方差解释率(%)',
        'PC3方差解释率(%)',
        '累计方差解释率(%)',
        'Betweenness_载荷',
        'Closeness_载荷',
        'PageRank_载荷',
        'Betweenness_均值',
        'Closeness_均值',
        'PageRank_均值',
        'Betweenness_标准差',
        'Closeness_标准差',
        'PageRank_标准差',
    ],
    '数值': [
        f'{explained_variance[0]*100:.2f}',
        f'{explained_variance[1]*100:.2f}',
        f'{explained_variance[2]*100:.2f}',
        f'{cumulative_variance[0]*100:.2f}',
        f'{loadings[0, 0]:.4f}',
        f'{loadings[1, 0]:.4f}',
        f'{loadings[2, 0]:.4f}',
        f'{stats.loc["Betweenness", "均值(Mean)"]:.4f}',
        f'{stats.loc["Closeness", "均值(Mean)"]:.6f}',
        f'{stats.loc["PageRank", "均值(Mean)"]:.6f}',
        f'{stats.loc["Betweenness", "标准差(Std)"]:.4f}',
        f'{stats.loc["Closeness", "标准差(Std)"]:.6f}',
        f'{stats.loc["PageRank", "标准差(Std)"]:.6f}',
    ]
}
summary_df = pd.DataFrame(summary_data)

# ==================== 第八步：保存到Excel ====================
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    result_df.to_excel(writer, sheet_name='综合得分', index=False)
    summary_df.to_excel(writer, sheet_name='统计摘要', index=False)

    # 调整列宽
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = max(len(str(cell.value or '')) for cell in column)
            worksheet.column_dimensions[column[0].column_letter].width = max_length + 2

print(f"\n" + "=" * 60)
print(f"✓ 结果已保存至: {OUTPUT_FILE}")
print(f"  Sheet 1: 综合得分 (含Z-score值、PC1综合得分、排名)")
print(f"  Sheet 2: 统计摘要 (含方差解释率、载荷矩阵、描述统计)")
print("=" * 60)

# ==================== 方法学引用信息 ====================
print("\n\n【方法学参考文献 - 可在论文中引用】")
print("-" * 60)
print("""
标准化方法:
  - Z-score标准化 (StandardScaler)
    参考: OECD (2008). Handbook on Constructing Composite Indicators.

主成分分析(PCA):
  - Leydesdorff, L. (2007). Betweenness centrality as an indicator of the
    interdisciplinarity of scientific journals. JASIST, 58(9), 1303-1319.
  - Cobo, M.J. et al. (2011). Science mapping software tools: Review,
    analysis, and cooperative study. JASIST, 62(7), 1382-1402.
  - Waltman, L. & van Eck, N.J. (2013). A smart local moving algorithm for
    large-scale modularity-based community detection. J. Stat. Mech., P03008.
""")
