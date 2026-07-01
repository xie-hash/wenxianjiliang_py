import os
import re
from collections import defaultdict
import pandas as pd
import metaknowledge as mk

# ---------- 1. 文件路径配置 ----------
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

# ---------- 2. 读取所有数据 ----------
rc = mk.RecordCollection()
for f in list_file:
    if os.path.exists(f):
        rc += mk.RecordCollection(f)
        print(f"已加载 {f}，当前总记录数: {len(rc)}")
    else:
        print(f"文件不存在: {f}")

print(f"\n总记录数: {len(rc)}")

# ---------- 3. 建立文献索引 ----------
# 使用 DOI (DI) 作为主键，若没有则用 UT (WOS 入藏号)
doi_to_info = {}      # key: DOI/UT, value: {'title':, 'gc':, 'year':, 'local_cite':0}
ut_to_doi = {}        # 若 CR 中只有 UT，可辅助映射
missing_id_count = 0

for rec in rc:
    # 获取唯一标识：优先 DOI，否则使用 UT
    doi = rec.get('DI')
    ut = rec.get('UT')
    if doi:
        uid = doi.strip()
    else:
        # 实在没有标识，跳过该记录（无法被本地引用）
        missing_id_count += 1
        continue
    
    title = rec.get('TI', '')
    gc = rec.get('TC')
    try:
        gc = int(gc) if gc else 0
    except:
        gc = 0
    
    # 出版年份：从 PY 或 DA 字段获取
    year = rec.get('PY')
    if not year:
        da = rec.get('DA')
        if da:
            year = da.split('-')[0].strip()
        else:
            year = 'Unknown'
    try:
        year = int(year) if year != 'Unknown' else 2026
    except:
        year = 2026
    
    doi_to_info[uid] = {
        'title': title,
        'gc': gc,
        'year': year,
        'local_cite': 0
    }
    # 记录 UT 到 DOI 的映射，用于 CR 中可能出现的 UT
    if ut and doi:
        ut_to_doi[ut.strip()] = uid

print(f"有效文献数（有唯一标识）: {len(doi_to_info)}，缺失标识: {missing_id_count}")

# ---------- 4. 计算本地引用次数 ----------
# 辅助函数：从 CR 字符串中提取可能的标识（DOI 或 UT）


# 遍历每条记录，解析其参考文献列表
for rec in rc:
    cr_list = rec.get('CR')
    if not cr_list:
        continue
    # 对于当前记录的每一条参考文献，尝试找到它在本地集合中的唯一标识
    for cr_item in cr_list:
        cr_str = str(cr_item)
        uid = cr_str.split(",")[-1].strip()[4:]

        if uid and uid in doi_to_info:
            doi_to_info[uid]['local_cite'] += 1

# ---------- 5. 生成最终统计表 ----------
rows = []
current_year = 2026  # 用于计算 C/Y

for uid, info in doi_to_info.items():
    gc = info['gc']
    lc = info['local_cite']
    year = info['year']
    if year != 'Unknown' and year != 2026:
        cy = round(gc / (current_year - year), 2)
    else:
        cy = 0.0
    lc_gc_ratio = round(lc / gc, 4) if gc > 0 else 0.0
    rows.append({
        'Document title': info['title'],
        'DOI/UT': uid,
        'YEAR': year,
        'GC': gc,
        'C/Y': cy,
        'LC': lc,
        'LC/GC(%)': f"{lc_gc_ratio*100:.2f}%"
    })

df = pd.DataFrame(rows)
# 按 GC 降序排序（即您原本想要的最多引用在前）
df = df.sort_values(by='GC', ascending=False)
df = df[0:20]
# 保存结果
output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\文章情况2.csv"
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n结果已保存至: {output_path}")
print(f"共 {len(df)} 条记录，前5条预览：")
print(df.head())