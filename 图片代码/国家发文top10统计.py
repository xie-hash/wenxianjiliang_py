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

def calculate_h_index(citation_list):
    """
    计算 h-index
    citation_list: 该国家所有论文的引用次数列表
    """
    sorted_cites = sorted(citation_list, reverse=True)
    h = 0
    for i, cites in enumerate(sorted_cites):
        if cites >= i + 1:
            h = i + 1
        else:
            break
    return h

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

# ---------- 3. 统计每个国家的各项指标 ----------
# country -> {指标}
country_pub_count = Counter()              # 发文数
country_citation_lists = defaultdict(list)  # 每篇论文的引用次数列表（用于计算 h-index）
country_total_cites = Counter()            # 总引用量

no_py_count = 0
no_c1_count = 0
total_valid = 0
total_pub_count = 0  # 用于计算发文占比的总发文数

# 记录每个国家的论文UT（用于去重，一篇论文涉及多个国家时，每个国家只计一次）
country_papers = defaultdict(set)

for rec in rc:
    # 获取发表年份（只保留 2000-2025 年间的文献，与原脚本保持一致）
    py_raw = rec.get("PY")
    if not py_raw:
        no_py_count += 1
        continue

    try:
        py = int(py_raw)
    except (ValueError, TypeError):
        no_py_count += 1
        continue

    # 只统计 2000-2025 年的文献
    if py < 2000 or py > 2025:
        continue

    # 提取国家
    c1 = rec.get("C1")
    if not c1:
        no_c1_count += 1
        continue

    countries = extract_countries_from_c1(c1)
    if not countries:
        no_c1_count += 1
        continue

    # 获取引用次数
    tc_raw = rec.get("TC")
    try:
        tc = int(tc_raw) if tc_raw else 0
    except (ValueError, TypeError):
        tc = 0

    # 获取论文唯一标识
    ut = rec.get("UT")

    total_valid += 1
    for country in countries:
        # 去重：同一篇论文只计一次
        if ut and ut in country_papers[country]:
            # 虽然不重复计数论文，但引用次数仍要累计（同一篇论文每个国家都获得完整引用）
            pass
        else:
            if ut:
                country_papers[country].add(ut)
            country_pub_count[country] += 1
            total_pub_count += 1
        
        country_total_cites[country] += tc
        country_citation_lists[country].append(tc)

print(f"\n有PY字段但无C1/国家信息的记录数: {no_c1_count}")
print(f"无PY字段的记录数: {no_py_count}")
print(f"成功统计的记录数: {total_valid}")
print(f"有效论文总数（一篇多国文献只计一次）: {total_pub_count}")

# ---------- 4. 计算总发文量并取前10 ----------
top10_countries = sorted(country_pub_count.items(), key=lambda x: x[1], reverse=True)[:10]

# 计算所有国家的总发文数（用于占比计算）
total_all_pubs = sum(country_pub_count.values())

print(f"\n所有国家总发文数（去重后，一篇多国文献每个国家各计一次）: {total_all_pubs}")

print(f"\n=== 发文量前十国家指标统计 ===")
header = f"{'排名':<6}{'国家':<25}{'发文数':<10}{'发文占比':<12}{'总引用量':<12}{'h指数':<8}{'每篇引用数':<12}"
print(header)
print("=" * len(header))

# 准备 CSV 数据
rows = []
for rank, (country, pub_count) in enumerate(top10_countries, 1):
    total_cites = country_total_cites[country]
    citation_list = country_citation_lists[country]
    h_index = calculate_h_index(citation_list)
    avg_cites = total_cites / pub_count if pub_count > 0 else 0
    pub_pct = (pub_count / total_all_pubs * 100) if total_all_pubs > 0 else 0
    
    print(f"{rank:<6}{country:<25}{pub_count:<10}{pub_pct:.2f}%{'':>7}{total_cites:<12}{h_index:<8}{avg_cites:.2f}{'':>5}")
    
    rows.append({
        "排名": rank,
        "国家": country,
        "发文数": pub_count,
        "发文占比": f"{pub_pct:.2f}%",
        "总引用量": total_cites,
        "h指数": h_index,
        "每篇引用数": round(avg_cites, 2)
    })

# ---------- 5. 输出 CSV ----------
df = pd.DataFrame(rows)
output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\国家发文top10统计.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"\n已输出 CSV 文件到: {output_path}")
print(df.to_string(index=False))
