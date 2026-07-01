import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def normalize_keyword(kw):
    """
    关键词标准化：去除首尾空格，统一转换为小写，去除内部多余空格。
    """
    if not kw:
        return ""
    kw = kw.strip().lower()
    kw = re.sub(r'\s+', ' ', kw)
    return kw

def extract_keywords(record):
    """
    从记录中提取关键词列表。
    优先使用 DE (作者关键词)，若不存在则使用 ID (Keywords Plus)，
    若两者都存在，合并去重。
    """
    keywords = set()
    de = record.get('DE')
    if de:
        if isinstance(de, str):
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
    id_field = record.get('ID')
    if id_field:
        if isinstance(id_field, str):
            parts = re.split(r'[;\n]', id_field)
            for p in parts:
                kw = normalize_keyword(p)
                if kw:
                    keywords.add(kw)
        else:
            for p in id_field:
                kw = normalize_keyword(p)
                if kw:
                    keywords.add(kw)
    return list(keywords)

def main():
    # 文件列表（与之前一致）
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

    # 统计关键词出现频次
    keyword_freq = Counter()
    # 记录每篇文献的关键词列表（用于共现计算）
    paper_keywords = []

    for record in rc_filtered:
        kws = extract_keywords(record)
        if len(kws) < 2:
            continue
        paper_keywords.append(kws)
        for kw in kws:
            keyword_freq[kw] += 1

    total_unique_keywords = len(keyword_freq)
    print(f"去重后的关键词总数: {total_unique_keywords}")

    # ---------- 过滤：保留出现频次前40%的关键词 ----------
    # 按频次降序排序
    sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
    top_percent = 0.4
    keep_count = max(1, int(total_unique_keywords * top_percent))  # 至少保留1个
    keep_keywords_set = {kw for kw, _ in sorted_keywords[:keep_count]}
    print(f"保留前 {top_percent*100:.0f}% 的关键词，实际保留数量: {keep_count}")

    # 过滤后，更新 keyword_freq 和 paper_keywords
    filtered_keyword_freq = {kw: freq for kw, freq in keyword_freq.items() if kw in keep_keywords_set}
    # 重新构建 paper_keywords 列表，只保留过滤后的关键词，且要求每篇文献中剩余关键词数量 >=2 才用于共现
    filtered_paper_keywords = []
    for kws in paper_keywords:
        filtered_kws = [kw for kw in kws if kw in keep_keywords_set]
        if len(filtered_kws) >= 2:
            filtered_paper_keywords.append(filtered_kws)

    # 重新统计过滤后的关键词频次（实际上可以直接用 filtered_keyword_freq）
    # 但为了确保一致性，可以重新计数
    final_keyword_freq = Counter()
    for kws in filtered_paper_keywords:
        for kw in kws:
            final_keyword_freq[kw] += 1

    print(f"过滤后剩余的关键词数量: {len(final_keyword_freq)}")
    print(f"过滤后有效文献数（含至少2个保留关键词）: {len(filtered_paper_keywords)}")

    # 构建共现矩阵（仅基于过滤后的关键词）
    cooccurrence = defaultdict(int)
    for kws in filtered_paper_keywords:
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
    for kw, freq in final_keyword_freq.items():
        G.add_node(kw, frequency=freq, label=kw)
    for (kw1, kw2), weight in cooccurrence.items():
        G.add_edge(kw1, kw2, weight=weight)

    print(f"最终关键词共现网络 - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    # 删除可能含有非法字符的属性
    for node, data in G.nodes(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
    for u, v, data in G.edges(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]

    # 导出 GML 文件
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\前百分之四十关键词分析.gml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nx.write_gml(G, output_path)
    print(f"已导出过滤后的关键词共现网络至: {output_path}")
    print("在 VOSviewer 中打开后，可使用 Overlay 视图按 frequency（关键词出现频次）着色。")

if __name__ == "__main__":
    main()