import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def normalize_keyword(kw):
    """关键词标准化：小写、去除首尾空格、内部多空格合并"""
    if not kw:
        return ""
    kw = kw.strip().lower()
    kw = re.sub(r'\s+', ' ', kw)
    return kw

def extract_author_keywords(record):
    """
    仅从 DE 字段提取作者关键词。
    若 DE 不存在则返回空列表（不补充 ID 字段）。
    """
    keywords = set()
    de = record.get('DE')
    if not de:
        return []
    if isinstance(de, str):
        # 分号或换行分隔
        parts = re.split(r'[;\n]', de)
        for p in parts:
            kw = normalize_keyword(p)
            if kw:
                keywords.add(kw)
    else:
        for p in de:
            kw = normalize_keyword(p)
            if kw:
                keywords.add(kw)
    return list(keywords)

def main():
    # 文件列表（与之前完全一致）
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

    # 读取所有文件并合并
    rc = mk.RecordCollection()
    for f in list_file:
        if os.path.exists(f):
            rc += mk.RecordCollection(f)
            print(f"已加载 {f}，当前总记录数: {len(rc)}")
        else:
            print(f"文件不存在: {f}")

    # 筛选被引次数 ≥30 的记录
    valid_records = [r for r in rc if int(r.get('TC', 0)) >= 30]
    print(f"满足被引≥30的记录数: {len(valid_records)}")

    if not valid_records:
        print("没有满足条件的记录，程序退出。")
        return

    rc_filtered = mk.RecordCollection(valid_records)

    # 统计作者关键词出现频次
    keyword_freq = Counter()
    # 每篇文献的作者关键词列表（用于共现）
    paper_keywords = []

    for record in rc_filtered:
        kws = extract_author_keywords(record)
        if len(kws) < 2:
            continue
        paper_keywords.append(kws)
        for kw in kws:
            keyword_freq[kw] += 1

    print(f"去重后的作者关键词数量: {len(keyword_freq)}")

    # 构建共现矩阵
    cooccurrence = defaultdict(int)
    for kws in paper_keywords:
        for i in range(len(kws)):
            for j in range(i+1, len(kws)):
                kw1, kw2 = kws[i], kws[j]
                if kw1 < kw2:
                    pair = (kw1, kw2)
                else:
                    pair = (kw2, kw1)
                cooccurrence[pair] += 1

    # 构建 NetworkX 图
    G = nx.Graph()
    for kw, freq in keyword_freq.items():
        G.add_node(kw, frequency=freq, label=kw)
    for (kw1, kw2), weight in cooccurrence.items():
        G.add_edge(kw1, kw2, weight=weight)

    print(f"作者关键词共现网络 - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    # 删除属性名中含 '-' 的键
    for node, data in G.nodes(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
    for u, v, data in G.edges(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]

    # 导出 GML
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\作者关键词.gml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nx.write_gml(G, output_path)
    print(f"已导出作者关键词共现网络至: {output_path}")
    print("在 VOSviewer 中打开后，可使用 Overlay 视图按 frequency（关键词出现频次）着色。")

if __name__ == "__main__":
    main()