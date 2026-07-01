import os
import re
import metaknowledge as mk
from collections import Counter

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

# ---------- 3. 初始化统计容器 ----------
author_keywords_all = []          # 存储所有作者关键词（原始出现）
keywords_plus_all = []            # 存储所有 Keywords Plus（原始出现）
paper_authors_count = []          # 每篇论文的作者数量
paper_countries = []              # 每篇论文的国家集合
total_citations = 0               # 总被引次数
year_counts = Counter()
all_refs = []           # 总参考文献

# ---------- 4. 提取国家的简化函数 ----------
def extract_country_from_address(addr):
    """
    从地址字符串中提取国家名称
    规则：取最后一个逗号后的部分，去除末尾的数字/点号后返回
    """
    if not addr:
        return None
    parts = addr.split(',')
    if len(parts) > 1:
        last = parts[-1].strip()
        # 去除末尾可能存在的数字、点号（如邮政编码、句号）
        last = re.sub(r'[0-9\.]+$', '', last).strip()
        return last if last else None
    return None

# ---------- 5. 遍历每条记录 ----------
for rec in rc:
    # ---- 5.1 作者关键词 (DE) ----
    de = rec.get('DE')
    if de:
        if isinstance(de, str):
            kws = de.split(";",maxsplit=-1)
        elif isinstance(de,list):
            kws = de
        else:
            print("类型不是list or str ")
        for kw in kws:
            kw = kw.strip()
            if kw:
                author_keywords_all.append(kw)

    # ---- 5.2 Keywords Plus (ID) ----
    id_field = rec.get('ID')
    if id_field:
        if isinstance(id_field, str):
            kws = id_field.split(";",maxsplit=-1)
        elif isinstance(id_field,list):
            kws = id_field
        else:
            print("类型不是list or str ")
        for kw in kws:
            kw = kw.strip()
            if kw:
                keywords_plus_all.append(kw)

    # ---- 5.3 作者数量 ----
    authors = rec.get('AU')
    if authors:
        if isinstance(authors, str):
            authors = [authors]
        n_authors = len(authors)
    else:
        n_authors = 0
    paper_authors_count.append(n_authors)

    # ---- 5.4 从地址提取国家 ----
    countries_set = set()
    addresses = rec.get('C1')
    if addresses:
        if isinstance(addresses, str):
            addresses = [addresses]
        for addr in addresses:
            country = extract_country_from_address(addr)
            if country:
                countries_set.add(country)
    paper_countries.append(countries_set)

    # ---- 5.5 被引次数 ----
    tc = rec.get('TC', 0)
    try:
        total_citations += int(tc)
    except:
        pass

    # --- 总参考文献数量 ---
    
    refs = rec.get('CR', [])
    print(type(refs))
    if isinstance(refs, str):   # 极少数情况可能是字符串
        refs = [refs]
    all_refs.extend(refs)       # 每条参考文献作为整体添加


    # ---- 5.6 出版年份 ----
    py = rec.get('PY')
    if py:
        try:
            year = int(py)
            year_counts[year] += 1
        except:
            pass

# ---------- 6. 计算统计指标 ----------
# 6.1 独立作者论文数 / 合作作者论文数
n_independent = sum(1 for n in paper_authors_count if n == 1)
n_collaborative = sum(1 for n in paper_authors_count if n >= 2)
total_papers = len(paper_authors_count)

# 6.2 跨国合作论文数（国家集合大小 >= 2）
n_international = sum(1 for cset in paper_countries if len(cset) >= 2)

# 6.3 平均被引次数
avg_citation = total_citations / total_papers if total_papers > 0 else 0

# 6.4 年增长率（复合年增长率 CAGR）
years_sorted = sorted(year_counts.keys())
if len(years_sorted) >= 2:
    first_year = years_sorted[0]
    last_year = years_sorted[-1]
    first_count = year_counts[first_year]
    last_count = year_counts[last_year]
    n_years = last_year - first_year
    if n_years > 0 and first_count > 0:
        cagr = (last_count / first_count) ** (1 / n_years) - 1
    else:
        cagr = None
else:
    cagr = None

# 逐年环比增长率
yearly_growth = {}
prev_count = None
for y in sorted(year_counts.keys()):
    curr = year_counts[y]
    if prev_count is not None:
        growth = (curr - prev_count) / prev_count if prev_count > 0 else 0
        yearly_growth[y] = growth
    prev_count = curr

# ---------- 7. 输出结果 ----------
print("\n==================== 统计结果 ====================")
print(f"总论文数: {total_papers}")
print(f"独立作者论文数 (作者数=1): {n_independent}")
print(f"合作作者论文数 (作者数>=2): {n_collaborative}")
print(f"跨国合作论文数 (国家数>=2): {n_international}")
print(f"总被引次数: {total_citations}")
print(f"平均每篇被引次数: {avg_citation:.2f}")

print("\n--- 作者关键词 (DE) 列表（去重后）---")
unique_author_kws = sorted(set(author_keywords_all))
print(f"数量: {len(unique_author_kws)}")
# 如需查看前20个示例，取消下一行注释
# print("示例:", unique_author_kws[:20])

print("\n--- Keywords Plus (ID) 列表（去重后）---")
unique_id_kws = sorted(set(keywords_plus_all))
print(f"数量: {len(unique_id_kws)}")
# print("示例:", unique_id_kws[:20])

print("\n--- 历年发文量 ---")
for y in years_sorted:
    print(f"  {y}: {year_counts[y]} 篇")

if cagr is not None:
    print(f"\n论文数量复合年增长率 (CAGR, {first_year}-{last_year}): {cagr:.2%}")
else:
    print("\n无法计算复合年增长率（年份不足或起始年为0）")

if yearly_growth:
    print("\n--- 逐年环比增长率 ---")
    for y, g in yearly_growth.items():
        print(f"  {y}: {g:.2%}")
unique_ref_count = len(set(all_refs))
print(f"去重后的参考文献总数: {unique_ref_count}")
