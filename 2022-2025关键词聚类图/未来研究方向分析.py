# -*- coding: utf-8 -*-
"""根据TOP7共现邻居数据，生成更细致的未来研究方向分析报告（Markdown格式）"""

import os

OUTPUT_DIR = r'c:\Users\谢\Desktop\vscodepj\文献计量学\2022-2025关键词聚类图'

# ==================== 详细数据（TOP 7） ====================
# 格式：{关键词: (分类, Cluster, [(邻居1, 次数), ...(邻居7, 次数)])}
DATA = {
    # ============ A类: 核心支柱型 ============
    'binding': ('A-核心支柱', 1, [
        ('covid-19', 52), ('docking', 47), ('protein', 41),
        ('molecular-dynamics', 35), ('prediction', 32), ('replication', 25), ('mechanism', 23)
    ]),
    'design': ('A-核心支柱', 2, [
        ('molecular docking', 128), ('derivatives', 67), ('biological evaluation', 55),
        ('inhibitors', 54), ('discovery', 45), ('antiviral activity', 43), ('in-vitro', 27)
    ]),
    'discovery': ('A-核心支柱', 2, [
        ('molecular docking', 83), ('inhibitors', 48), ('design', 45),
        ('derivatives', 27), ('antiviral activity', 27), ('in-vitro', 14), ('biological evaluation', 13)
    ]),
    'docking': ('A-核心支柱', 1, [
        ('covid-19', 107), ('drug discovery', 81), ('molecular-dynamics', 59),
        ('protein', 54), ('binding', 47), ('prediction', 43), ('dynamics', 42)
    ]),
    'drug discovery': ('A-核心支柱', 1, [
        ('covid-19', 83), ('docking', 81), ('prediction', 51),
        ('replication', 40), ('protein', 33), ('molecular-dynamics', 24), ('database', 20)
    ]),
    'identification': ('A-核心支柱', 3, [
        ('sars-cov-2', 73), ('infection', 40), ('virus', 36),
        ('coronavirus', 36), ('protease', 17), ('crystal-structure', 16), ('acid', 11)
    ]),
    'in-vitro': ('A-核心支柱', 2, [
        ('molecular docking', 83), ('antiviral activity', 49), ('biological evaluation', 28),
        ('design', 27), ('derivatives', 25), ('inhibitors', 19), ('discovery', 14)
    ]),
    'infection': ('A-核心支柱', 3, [
        ('sars-cov-2', 58), ('identification', 40), ('coronavirus', 30),
        ('virus', 30), ('inhibitor', 18), ('crystal-structure', 14), ('drug', 11)
    ]),
    'inhibitors': ('A-核心支柱', 2, [
        ('molecular docking', 107), ('design', 54), ('discovery', 48),
        ('derivatives', 42), ('antiviral activity', 34), ('biological evaluation', 22), ('in-vitro', 19)
    ]),
    'molecular docking': ('A-核心支柱', 2, [
        ('design', 128), ('antiviral activity', 117), ('inhibitors', 107),
        ('derivatives', 99), ('in-vitro', 83), ('discovery', 83), ('biological evaluation', 81)
    ]),
    'protein': ('A-核心支柱', 1, [
        ('covid-19', 80), ('docking', 54), ('binding', 41),
        ('prediction', 38), ('replication', 37), ('drug discovery', 33), ('dynamics', 20)
    ]),

    # ============ B类: 上升新星型 ============
    'cancer': ('B-上升新星', 4, [
        ('inhibition', 11), ('activation', 9), ('cells', 6),
        ('inflammation', 5), ('resistance', 4), ('metabolism', 4), ('mechanisms', 4)
    ]),
    'mechanisms': ('B-上升新星', 4, [
        ('cells', 6), ('inflammation', 6), ('inhibition', 6),
        ('activation', 5), ('resistance', 5), ('cancer', 4), ('metabolism', 3)
    ]),

    # ============ C类: V型反弹型 ============
    'coronavirus': ('C-V型反弹', 3, [
        ('sars-cov-2', 180), ('virus', 48), ('identification', 36),
        ('infection', 30), ('protease', 18), ('drug', 13), ('inhibitor', 7)
    ]),
    'covid-19': ('C-V型反弹', 1, [
        ('docking', 107), ('drug discovery', 83), ('protein', 80),
        ('replication', 73), ('binding', 52), ('prediction', 46), ('molecular-dynamics', 42)
    ]),
    'derivatives': ('C-V型反弹', 2, [
        ('molecular docking', 99), ('design', 67), ('antiviral activity', 44),
        ('inhibitors', 42), ('biological evaluation', 41), ('discovery', 27), ('in-vitro', 25)
    ]),
    'efficacy': ('C-V型反弹', 1, [
        ('covid-19', 28), ('protein', 12), ('drug discovery', 9),
        ('replication', 8), ('binding', 7), ('docking', 5), ('mechanism', 4)
    ]),
    'expression': ('C-V型反弹', 1, [
        ('covid-19', 18), ('replication', 13), ('protein', 11),
        ('docking', 8), ('binding', 8), ('prediction', 6), ('complex', 5)
    ]),
    'inhibition': ('C-V型反弹', 4, [
        ('flavonoids', 12), ('cancer', 11), ('cells', 10),
        ('activation', 10), ('inflammation', 7), ('mechanisms', 6), ('resistance', 5)
    ]),
    'prediction': ('C-V型反弹', 1, [
        ('drug discovery', 51), ('covid-19', 46), ('docking', 43),
        ('protein', 38), ('binding', 32), ('database', 20), ('replication', 15)
    ]),
    'replication': ('C-V型反弹', 1, [
        ('covid-19', 73), ('drug discovery', 40), ('protein', 37),
        ('docking', 30), ('binding', 25), ('mechanism', 17), ('prediction', 15)
    ]),
    'virus': ('C-V型反弹', 3, [
        ('sars-cov-2', 97), ('coronavirus', 48), ('identification', 36),
        ('infection', 30), ('crystal-structure', 14), ('inhibitor', 12), ('dengue', 11)
    ]),
}

# ==================== 辅助信息 ====================
CLUSTER_NAMES = {
    1: '计算对接与分子动力学模拟',
    2: '药物设计与体外活性评价',
    3: '病毒学与感染机制',
    4: '细胞凋亡与炎症信号通路机制',
}

# ==================== 更细致的研究方向描述 ====================
def generate_direction(keyword, cat, cluster, neighbors):
    """为每个关键词生成细粒度的研究方向描述"""
    top3 = [n[0] for n in neighbors[:3]]
    all_7 = [f"{n[0]}({n[1]})" for n in neighbors]
    top3_str = '、'.join(top3)

    cluster_desc = {
        1: '基于计算对接的靶向结合机制研究与分子动力学验证',
        2: '先导化合物设计—合成—体外活性评价全链条开发',
        3: '冠状病毒(尤其是SARS-CoV-2)的感染机制与结构病毒学研究',
        4: '细胞凋亡与炎症信号通路的调控机制及其在疾病中的作用',
    }[cluster]

    # 针对每个关键词生成独特的方向
    specific_direction = {
        # ===== Cluster 1 =====
        'docking': f'分子对接技术驱动的新型抑制剂筛选策略，重点关注与{top3_str}的交叉验证',
        'protein': f'靶标蛋白的结构特征解析与功能预测，探索{top3_str}相互作用网络',
        'binding': f'配体-受体结合模式的分子机制研究，整合{top3_str}的多维结构信息',
        'drug discovery': f'基于{top3_str}的虚拟筛选与药物发现流程优化',
        'covid-19': f'SARS-CoV-2主蛋白酶及刺突蛋白的{top3_str}研究，从分子对接到抗病毒活性验证',
        'replication': f'SARS-CoV-2复制机制的分子基础研究，通过{top3_str}揭示病毒生命周期的干预靶点',
        'prediction': f'{top3_str}的机器学习预测模型构建，加速候选药物的靶向性评估',
        'efficacy': f'{top3_str}多维度关联分析的药效评价体系，建立从分子结合到细胞水平的验证链',
        'expression': f'{top3_str}的蛋白表达与功能调控机制，解析宿主细胞对病毒感染的分子响应',
        # ===== Cluster 2 =====
        'molecular docking': f'大规模分子对接结合{top3_str}的先导化合物发现与多轮迭代优化',
        'design': f'基于{top3_str}的合理药物设计策略，融合衍生物构效关系与体外活性验证',
        'inhibitors': f'新型{top3_str}的发现与构效关系研究，从对接筛选到生物评价的完整流程',
        'discovery': f'抗病毒{top3_str}的活性筛选与先导化合物发现',
        'in-vitro': f'{top3_str}的体外抗病毒活性评价模型，系统评估候选化合物的抑制效能',
        'derivatives': f'{top3_str}的衍生物设计与结构优化策略，提升靶向亲和力与药代性质',
        # ===== Cluster 3 =====
        'identification': f'{top3_str}的关键功能位点鉴定与结构解析，为靶向药物设计提供分子基础',
        'infection': f'{top3_str}的病毒感染机制与宿主互作网络，探索抗病毒干预新策略',
        'coronavirus': f'{top3_str}的冠状病毒跨种传播机制与广度中和抗体靶点研究',
        'virus': f'{top3_str}的病毒结构蛋白的构象变化与抗病毒药物靶向策略',
        # ===== Cluster 4 =====
        'cancer': f'{top3_str}介导的癌症发展信号通路与天然产物干预策略',
        'mechanisms': f'细胞{top3_str}炎性及凋亡的多层级调控机制，揭示疾病治疗的潜在靶点',
        'inhibition': f'{top3_str}的多靶点抑制活性评估与药理机制解析',
    }

    return specific_direction.get(keyword, f'{top3_str}的交叉研究方向')


# ==================== 生成Markdown ====================
lines = []
lines.append('# 未来研究方向分析\n')
lines.append('## 基于关键词共现网络的精细化学科方向研判\n')
lines.append('> 以下分析基于2022—2025年关键词共现数据（TOP 7共现邻居），'
             '将离散的关键词还原为具有明确学科边界的精细化研究方向。\n')

# 分类遍历
seen_neighbors = set()

for cat_label, cat_num, cat_title in [
    ('A-核心支柱', '一', '核心支柱型'),
    ('B-上升新星', '二', '上升新星型'),
    ('C-V型反弹',  '三', 'V型反弹型')
]:
    items = [(k, v) for k, v in DATA.items() if v[0] == cat_label]
    items.sort(key=lambda x: x[0])

    lines.append(f'---\n')
    lines.append(f'## {cat_num}、{cat_title}\n')

    for keyword, (cat, cluster, neighbors) in items:
        cluster_name = CLUSTER_NAMES.get(cluster, f'Cluster {cluster}')
        direction = generate_direction(keyword, cat, cluster, neighbors)

        lines.append(f'### {keyword}\n')
        lines.append(f'- **分类**：{cat}  |  **所属簇**：Cluster {cluster}')
        lines.append(f'- **研究方向**：{direction}')
        lines.append(f'- **共现邻居词（按频次排序）**：\n')

        for i, (neighbor, weight) in enumerate(neighbors, 1):
            if neighbor in seen_neighbors:
                flag = '（已在前文出现）'
            else:
                flag = '（← 本词独有高频邻居）'
                seen_neighbors.add(neighbor)
            lines.append(f'  {i}. **{neighbor}** ({weight}次){flag}')

        lines.append('')

# ==================== 跨方向整合 ====================
lines.append('---\n')
lines.append('## 四、跨方向整合：四大研究主线的深层汇聚\n')

for cl in [1, 2, 3, 4]:
    cluster_name = CLUSTER_NAMES[cl]
    items = [(k, v) for k, v in DATA.items() if v[1] == cl]
    items.sort(key=lambda x: x[0])

    lines.append(f'### Cluster {cl}：{cluster_name}\n')
    lines.append(f'该簇汇聚了 {len(items)} 个潜力关键词，形成以下细分方向群：\n')

    for kw, (cat, c, neighbors) in items:
        direction = generate_direction(kw, cat, c, neighbors)
        cat_short = {'A-核心支柱': '核心', 'B-上升新星': '新星', 'C-V型反弹': 'V型'}[cat]
        lines.append(f'- **{kw}**【{cat_short}】：{direction}')
    lines.append('')

    # 该簇独有高频关联关键词（在潜力关键词TOP7中出现但本身不是潜力关键词）
    all_neighbors_in_cluster = set()
    for kw, (cat, c, neighbors) in DATA.items():
        if c == cl:
            for n, w in neighbors:
                all_neighbors_in_cluster.add(n)
    cluster_kws = {k for k, _ in items}
    unique_high_freq = sorted([n for n in all_neighbors_in_cluster if n not in cluster_kws])
    if unique_high_freq:
        lines.append(f'  该簇高频关联关键词：{", ".join(unique_high_freq)}')
        lines.append('')

# ==================== 结论 ====================
lines.append('---\n')
lines.append('## 五、结论与展望\n')
lines.append('综合上述TOP 7共现邻域分析，该领域的研究呈现以下精细化的态势：\n')

for i, cl in enumerate([1, 2, 3, 4], 1):
    cluster_name = CLUSTER_NAMES[cl]
    count = len([1 for _, (_, c, _) in DATA.items() if c == cl])
    lines.append(f'{i}. **{cluster_name}**（{count}个潜力关键词）：')
    items = [(k, v) for k, v in DATA.items() if v[1] == cl]
    for kw, (cat, _, _) in items:
        lines.append(f'   • {kw}')
    lines.append('')

lines.append('以上精细化方向分析不仅揭示各关键词的研究内涵，'
             '也为后续文献综述"以关键词为线索、以共现网络为骨架"的结构化写作提供了直接的素材支撑。\n')

# ==================== 保存 ====================
output_file = os.path.join(OUTPUT_DIR, '未来研究方向分析.md')
content = '\n'.join(lines)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'✓ 已生成: {output_file}')
print(f'  共 {len(DATA)} 个关键词，输出 {len(lines)} 行内容')
