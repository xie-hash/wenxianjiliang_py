"""参考文献爆发的时间段特征分析"""
import pandas as pd

df = pd.read_csv(r'c:\Users\谢\Desktop\vscodepj\文献计量学\参考文献爆发检测.csv', encoding='utf-8-sig')

periods = [
    ('2008-2011: 基础工具建立期', 2008, 2012),
    ('2012-2016: 方法成熟与应用期', 2012, 2017),
    ('2017-2019: COVID前夜(大数据+AI)', 2017, 2020),
    ('2020-2021: COVID大爆发期', 2020, 2022),
    ('2022-2023: 后COVID+AI崛起期', 2022, 2024),
    ('2024-2026: 最新前沿', 2024, 2027),
]

print('=' * 90)
print('爆发文献按时间段的系统分析')
print('=' * 90)

for pname, start, end in periods:
    g = df[(df['爆发开始年份'] >= start) & (df['爆发开始年份'] < end)]
    if len(g) == 0:
        continue
    
    print(f'\n{"="*90}')
    print(f'【{pname}】爆发事件: {len(g)}个')
    print(f'  平均爆发强度: {g["爆发强度"].mean():.2f}x  |  '
          f'平均持续: {g["持续年数"].mean():.1f}年  |  '
          f'平均总被引: {g["参考文献总被引"].mean():.0f}')
    print()
    
    for _, r in g.sort_values('爆发强度', ascending=False).iterrows():
        ref = str(r['参考文献标识'])[:45]
        orig = str(r['参考文献原始示例'])[:70]
        print(f'  {ref:<45} {int(r["爆发开始年份"])}-{int(r["爆发结束年份"])}  '
              f'强度={r["爆发强度"]:.1f}x  被引={int(r["参考文献总被引"])}')
        print(f'  → {orig}')
        print()

print()
print('=' * 90)
print('类型分布概览')
print('=' * 90)

for pname, start, end in periods:
    g = df[(df['爆发开始年份'] >= start) & (df['爆发开始年份'] < end)]
    if len(g) == 0:
        continue
    
    refs = g['参考文献原始示例'].str.upper().tolist()
    
    n_covid = sum(1 for r in refs if any(k in r for k in ['COVID', 'SARS', 'CORONAVIRUS']))
    n_tool = sum(1 for r in refs if any(k in r for k in ['AUTODOCK', 'VINA', 'AMBER', 'GROMACS', 'SWISS', 'ADME', 'VMD', 'PYMOL']))
    n_clinical = sum(1 for r in refs if any(k in r for k in ['LANCET', 'JAMA', 'NEW ENGL']))
    
    print(f'{pname:<40} | 总数={len(g):>3} | COVID={n_covid:>2} | 方法学={n_tool:>2} | 临床={n_clinical:>2}')
