import os
import re
from collections import defaultdict, Counter
import pandas as pd
import metaknowledge as mk

# ---------- 大学提取函数 ----------
def extract_universities(c1_field):
    """从 C1 字段提取大学名（取第一个逗号前部分，仅保留含 Univ/University 等关键词的机构）"""
    if not c1_field:
        return []
    if isinstance(c1_field, str):
        addr_list = [c1_field]
    else:
        addr_list = c1_field

    # 大学关键词
    uni_keywords = re.compile(r'\b(Univ|University|College|Institute\s+of\s+Technology|Polytechnic|Institut)\b', re.IGNORECASE)

    orgs = set()
    for addr in addr_list:
        if not addr:
            continue
        addr = addr.strip()
        parts = addr.split(',')
        if parts:
            org = parts[0].strip()
            # 去除末尾可能存在的句点
            org = org.rstrip('. ')
            if org and uni_keywords.search(org):
                orgs.add(org)
    return list(orgs)


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

# ---------- 3. 统计每个大学在三个时间段的发文量 ----------
uni_period_count = defaultdict(lambda: Counter())   # university -> {period: count}
period_total_count = Counter()                       # period -> 所有大学在该时期的总计数
year_distribution = Counter()
no_py_count = 0
no_c1_count = 0
total_valid = 0

for rec in rc:
    # 获取发表年份
    py_raw = rec.get("PY")
    if not py_raw:
        no_py_count += 1
        continue

    try:
        py = int(py_raw)
    except (ValueError, TypeError):
        no_py_count += 1
        continue

    year_distribution[py] += 1

    # 确定时间段
    if 2000 <= py <= 2012:
        period = "2000-2012"
    elif 2013 <= py <= 2018:
        period = "2013-2018"
    elif 2019 <= py <= 2025:
        period = "2019-2025"
    else:
        continue   # 不在目标年份范围内，跳过

    # 提取大学
    c1 = rec.get("C1")
    if not c1:
        no_c1_count += 1
        continue

    unis = extract_universities(c1)
    if not unis:
        no_c1_count += 1
        continue

    total_valid += 1
    for uni in unis:
        uni_period_count[uni][period] += 1
        period_total_count[period] += 1

print(f"\n年份范围: {min(year_distribution.keys()) if year_distribution else 'N/A'} - {max(year_distribution.keys()) if year_distribution else 'N/A'}")
print(f"有PY字段但无C1/大学信息的记录数: {no_c1_count}")
print(f"无PY字段的记录数: {no_py_count}")
print(f"成功统计的记录数: {total_valid}")
print(f"\n年份分布（前20）: {dict(year_distribution.most_common(20))}")

# ---------- 4. 计算总发文量并取前10 ----------
uni_total = {}
for uni, pc in uni_period_count.items():
    uni_total[uni] = sum(pc.values())

top10_unis = sorted(uni_total.items(), key=lambda x: x[1], reverse=True)[:10]

# 各时期总发文量
p1_total = period_total_count.get("2000-2012", 1)
p2_total = period_total_count.get("2013-2018", 1)
p3_total = period_total_count.get("2019-2025", 1)

print(f"\n各时期总发文量（所有大学合计，一篇多大学文献每个大学各计一次）:")
print(f"  2000-2012: {p1_total}")
print(f"  2013-2018: {p2_total}")
print(f"  2019-2025: {p3_total}")

print(f"\n=== 发文量前十大学（含百分比） ===")
header = f"{'排名':<6}{'大学':<50}{'2000-2012发文':<28}{'2013-2018发文':<28}{'2019-2025发文':<28}{'总发文量':<10}"
print(header)
print("=" * len(header))
for rank, (uni, total) in enumerate(top10_unis, 1):
    p1 = uni_period_count[uni].get("2000-2012", 0)
    p2 = uni_period_count[uni].get("2013-2018", 0)
    p3 = uni_period_count[uni].get("2019-2025", 0)
    p1_str = f"{p1} ({p1/p1_total*100:.2f}%)"
    p2_str = f"{p2} ({p2/p2_total*100:.2f}%)"
    p3_str = f"{p3} ({p3/p3_total*100:.2f}%)"
    print(f"{rank:<6}{uni:<50}{p1_str:<28}{p2_str:<28}{p3_str:<28}{total:<10}")

# ---------- 5. 输出 CSV ----------
rows = []
for rank, (uni, total) in enumerate(top10_unis, 1):
    p1 = uni_period_count[uni].get("2000-2012", 0)
    p2 = uni_period_count[uni].get("2013-2018", 0)
    p3 = uni_period_count[uni].get("2019-2025", 0)
    rows.append({
        "排名": rank,
        "大学": uni,
        "2000-2012发文": f"{p1} ({p1/p1_total*100:.2f}%)",
        "2013-2018发文": f"{p2} ({p2/p2_total*100:.2f}%)",
        "2019-2025发文": f"{p3} ({p3/p3_total*100:.2f}%)",
        "总发文量": total
    })

df = pd.DataFrame(rows)
output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\大学发文时段统计_top10.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"\n已输出 CSV 文件到: {output_path}")
print(df.to_string(index=False))
