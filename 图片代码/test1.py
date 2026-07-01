import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def extract_author_and_year(citation):
    """
    从参考文献字符串中提取第一作者和年份。
    返回 (author, year)，year 可能为 None。
    """
    cit_str = str(citation)
    # 提取作者：取第一个逗号前的内容（包含可能的第二个逗号前，如 "Smith, J"）
    # 匹配 "姓, 名" 后紧跟逗号和空格
    author_match = re.match(r'^([^,]+,[^,]+?) ,', cit_str)
    if author_match:
        author = author_match.group(1).strip()
    else:
        # 备选：只取第一个逗号前（如只有姓）
        author_match2 = re.match(r'^([^,]+)', cit_str)
        if author_match2:
            author = author_match2.group(1).strip()
        else:
            author = None
    
    # 提取年份：4位数字，范围1900-2026
    year_match = re.search(r'\b(19|20)\d{2}\b', cit_str)
    year = int(year_match.group(0)) if year_match else None
    return author, year

def clean_gml_properties(G):
    """删除属性名中含连字符 '-' 的属性，确保每个节点有 label"""
    for node, data in G.nodes(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
        if 'label' not in data:
            data['label'] = node   # 节点ID作为标签
    for u, v, data in G.edges(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
    return G


# ========== 请修改为您自己的文件路径 ==========
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
# ============================================

# 读取数据
rc = mk.RecordCollection()
for f in list_file:
    if os.path.exists(f):
        rc += mk.RecordCollection(f)
        print(f"已加载 {f}，总记录数: {len(rc)}")
    else:
        print(f"文件不存在: {f}")

# 筛选被引次数 >= 30 的施引文献
valid_records = [r for r in rc if int(r.get('TC', 0)) >= 30]
print(f"满足被引≥30的记录数: {len(valid_records)}")
Uni = []
for rec in rc:
    id = rec.get("DT")
    if "Article" in id:
        Uni.append("article")
    elif "Review" in id:
        Uni.append("review")
    else:
        pass
Uni = Counter(Uni)
    
print(Uni,len(Uni))
