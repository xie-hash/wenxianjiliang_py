# -*- coding: utf-8 -*-
"""创建文献情况.csv文件"""
import csv
import os

data = [
    ['序号', '期刊', '核心子领域(3-5)', 'JCR分区(类别)', '排名百分位', 'NP', '贡献率', 'TC', 'h指数', 'g指数'],
    [1, 'Journal of Biomolecular Structure & Dynamics',
     'biological structure & dynamics, computational structural biology, bioinformatics, virtual drug design, genomics',
     'Q3 (Biochemistry & Molecular Biology)',
     'Top 50–75% (Third quartile)', 246, '6.02%', 6403, 42, 70],
    [2, 'International Journal of Molecular Sciences (IJMS)',
     'molecular biology, molecular medicine, biochemistry, molecular chemistry',
     'Q1 (Biochemistry & Molecular Biology)',
     'Top 25%', 127, '3.11%', 2378, 24, 45],
    [3, 'Molecules',
     'organic chemistry, natural products chemistry, chemical biology, analytical chemistry, molecular science',
     'Q2 (Biochemistry & Molecular Biology; Chemistry, Multidisciplinary)',
     'Top 25–50% (Second quartile)', 109, '2.67%', 2574, 28, 46],
    [4, 'Scientific Reports',
     'multidisciplinary, natural sciences, medicine, engineering, psychology',
     'Q1 (Multidisciplinary Sciences)',
     'Top 25%', 102, '2.50%', 1511, 23, 36],
    [5, 'Viruses-Basel',
     'virology, viral pathogenesis, virus-host interactions, antiviral strategies, epidemiology',
     'Q2 (Virology)',
     'Top 25–50% (Second quartile)', 87, '2.13%', 1338, 19, 33],
    [6, 'Antiviral Research',
     'antiviral drugs, vaccines, viral pathogenesis, immunotherapy, drug targets',
     'Q1 (Pharmacology & Pharmacy; Virology)',
     'Top 25%', 81, '1.98%', 2281, 26, 45],
    [7, 'Frontiers in Pharmacology',
     'pharmacology, medicinal chemistry, toxicology, pharmacy, therapeutics',
     'Q1 (Pharmacology & Pharmacy)',
     'Top 25%', 63, '1.54%', 1856, 24, 42],
    [8, 'Pharmaceuticals',
     'pharmaceutics, drug delivery, nanomedicine, pharmaceutical technology, drug design',
     'Q1 (Chemistry, Medicinal; Pharmacology & Pharmacy)',
     'Top 25% in Chemistry, Medicinal; Top ~14.5% in Pharmacology & Pharmacy',
     61, '1.49%', 738, 13, 25],
    [9, 'PLOS ONE',
     'multidisciplinary, natural sciences, medicine, engineering, social sciences',
     'Q2 (Multidisciplinary Sciences)',
     'Top 25–50% (Second quartile)', 60, '1.47%', 901, 18, 28],
    [10, 'Journal of Molecular Structure',
     'structural chemistry, spectroscopy, molecular structure, theoretical chemistry, experimental chemistry',
     'Q1 (Spectroscopy)',
     'Top 17.7% (Ranked 14/79 in Spectroscopy)', 59, '1.44%', 1244, 19, 34]
]

output_path = os.path.join(os.path.dirname(__file__), '文献情况.csv')
with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f'CSV 文件已成功创建：{output_path}')
