import os
import re
from collections import defaultdict, Counter
import pandas as pd
import metaknowledge as mk

# ---------- 国家提取函数（直接从 country.py 复制） ----------
def standardize_country(country):
    """
    标准化国家名称，将美国相关变体统一为 "United States"。
    """
    if not country:
        return country
    country_clean = country.strip()
    country_upper = country_clean.upper()

    # 检测是否以 "USA" 结尾
    if country_upper.endswith('USA'):
        return "United States"

    # 检测是否包含 " USA " 作为单词
    if re.search(r'\bUSA\b', country_upper):
        return "United States"

    # 精确匹配常见美国变体
    us_variants = {"USA", "U.S.A.", "UNITED STATES", "UNITED STATES OF AMERICA", "US", "U.S."}
    if country_upper in us_variants:
        return "United States"

    # 其他国家原样返回
    return country_clean

def extract_country_from_address(addr):
    """从地址字符串中提取国家名称（取最后一个逗号后部分）"""
    if not addr:
        return None
    parts = addr.split(',')
    country = parts[-1].strip()
    if not country:
        return None
    # 去除末尾可能存在的句点
    country = country.rstrip('. ')
    return standardize_country(country)

def extract_countries_from_c1(c1_field):
    """从 C1 字段提取所有国家（去重并标准化）"""
    if not c1_field:
        return []
    if isinstance(c1_field, str):
        addr_list = [c1_field]
    else:
        addr_list = c1_field
    countries = set()
    for addr in addr_list:
        country = extract_country_from_address(addr)
        if country:
            countries.add(country)
    return list(countries)

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

# ---------- 3. 统计每个国家在三个时间段的发文量 ----------
country_period_count = defaultdict(lambda: Counter())   # country -> {period: count}
period_total_count = Counter()                           # period -> 所有国家在该时期的总计数
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

    # 提取国家
    c1 = rec.get("C1")
    if not c1:
        no_c1_count += 1
        continue

    countries = extract_countries_from_c1(c1)
    if not countries:
        no_c1_count += 1
        continue

    total_valid += 1
    for country in countries:
        country_period_count[country][period] += 1
        period_total_count[period] += 1

print(f"\n年份范围: {min(year_distribution.keys()) if year_distribution else 'N/A'} - {max(year_distribution.keys()) if year_distribution else 'N/A'}")
print(f"有PY字段但无C1/国家信息的记录数: {no_c1_count}")
print(f"无PY字段的记录数: {no_py_count}")
print(f"成功统计的记录数: {total_valid}")
print(f"\n年份分布（前20）: {dict(year_distribution.most_common(20))}")

# ---------- 4. 计算总发文量并取前10 ----------
country_total = {}
for country, pc in country_period_count.items():
    country_total[country] = sum(pc.values())

top10_countries = sorted(country_total.items(), key=lambda x: x[1], reverse=True)[:10]

# 各时期总发文量
p1_total = period_total_count.get("2000-2012", 1)
p2_total = period_total_count.get("2013-2018", 1)
p3_total = period_total_count.get("2019-2025", 1)

print(f"\n各时期总发文量（所有国家合计，一篇多国文献每个国家各计一次）:")
print(f"  2000-2012: {p1_total}")
print(f"  2013-2018: {p2_total}")
print(f"  2019-2025: {p3_total}")

print(f"\n=== 发文量前十国家（含百分比） ===")
header = f"{'排名':<6}{'国家':<25}{'2000-2012发文':<28}{'2013-2018发文':<28}{'2019-2025发文':<28}{'总发文量':<10}"
print(header)
print("=" * len(header))
for rank, (country, total) in enumerate(top10_countries, 1):
    p1 = country_period_count[country].get("2000-2012", 0)
    p2 = country_period_count[country].get("2013-2018", 0)
    p3 = country_period_count[country].get("2019-2025", 0)
    p1_str = f"{p1} ({p1/p1_total*100:.2f}%)"
    p2_str = f"{p2} ({p2/p2_total*100:.2f}%)"
    p3_str = f"{p3} ({p3/p3_total*100:.2f}%)"
    print(f"{rank:<6}{country:<25}{p1_str:<28}{p2_str:<28}{p3_str:<28}{total:<10}")

# ---------- 5. 输出 CSV ----------
rows = []
for rank, (country, total) in enumerate(top10_countries, 1):
    p1 = country_period_count[country].get("2000-2012", 0)
    p2 = country_period_count[country].get("2013-2018", 0)
    p3 = country_period_count[country].get("2019-2025", 0)
    rows.append({
        "排名": rank,
        "国家": country,
        "2000-2012发文": f"{p1} ({p1/p1_total*100:.2f}%)",
        "2013-2018发文": f"{p2} ({p2/p2_total*100:.2f}%)",
        "2019-2025发文": f"{p3} ({p3/p3_total*100:.2f}%)",
        "总发文量": total
    })

df = pd.DataFrame(rows)
output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\国家发文时段统计_top10.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"\n已输出 CSV 文件到: {output_path}")
print(df.to_string(index=False))
