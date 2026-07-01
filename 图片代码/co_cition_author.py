import networkx as nx
import metaknowledge as mk
import os
from collections import defaultdict, Counter

def main():
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


    # 读取并合并所有记录
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

    # 构建作者共被引网络
    co_citation_weight = defaultdict(int)   # (author1, author2) -> 共被引次数
    author_freq = Counter()                  # 作者被引次数（作为参考文献出现的总次数）

    for citing_record in rc_filtered:
        refs = citing_record.get('CR')
        if not refs:
            continue

        # 收集当前引证文献中出现的所有被引作者
        authors_in_this_paper = []
        for citation in refs:
            try:
                auth = citation.auth
                if auth:
                    auth = auth.strip()
                    if auth:
                        authors_in_this_paper.append(auth)
                        author_freq[auth] += 1
            except AttributeError:
                # 如果 Citation 对象没有 auth 属性，则跳过
                continue

        # 两两组合，增加共被引边权重
        if len(authors_in_this_paper) < 2:
            continue
        for i in range(len(authors_in_this_paper)):
            for j in range(i+1, len(authors_in_this_paper)):
                a1, a2 = authors_in_this_paper[i], authors_in_this_paper[j]
                if a1 < a2:
                    co_citation_weight[(a1, a2)] += 1
                else:
                    co_citation_weight[(a2, a1)] += 1

    # 构建 networkx 图
    G = nx.Graph()
    for author, freq in author_freq.items():
        G.add_node(author,
                   cited_count=freq,   # 被引次数
                   label=author)        # VOSviewer 标签
    for (a1, a2), weight in co_citation_weight.items():
        G.add_edge(a1, a2, weight=weight)

    print(f"作者共被引网络 - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    # 删除可能含非法字符的属性（如 '-'）
    for node, data in G.nodes(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
    for u, v, data in G.edges(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]

    # 导出 GML
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\作者共被引.gml"
    nx.write_gml(G, output_path)
    print(f"已导出作者共被引网络至: {output_path}")
    print("在 VOSviewer 中打开后，可使用 Overlay 视图按被引次数(cited_count)着色。")

if __name__ == "__main__":
    main()