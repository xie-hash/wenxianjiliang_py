import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def extract_corresponding_author(rp_field):
    """从 WOS 的 RP 字段提取通讯作者名"""
    if not rp_field:
        return None
    # 典型格式: "Smith, J (reprint author), University of ..."
    match = re.search(r'([^,]+?)\s*\(reprint author\)', rp_field)
    if match:
        return match.group(1).strip()
    return None

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

    # 筛选被引次数 ≥30 的记录（可根据需要调整阈值）
    valid_records = [r for r in rc if int(r.get('TC', 0)) >= 30]
    print(f"满足被引≥30的记录数: {len(valid_records)}")

    if not valid_records:
        print("没有满足条件的记录，程序退出。")
        return

    rc_filtered = mk.RecordCollection(valid_records)

    # 构建作者耦合网络（只考虑第一作者和通讯作者）
    ref_to_authors = defaultdict(set)          # 参考文献 -> 作者集合
    author_pub_count = Counter()               # 作者发文数
    author_total_cites = Counter()             # 作者总被引

    for record in rc_filtered:
        authors = record.get('AU')              # 所有作者列表
        if not authors:
            continue
        refs = record.get('CR')                 # 参考文献列表
        if not refs:
            continue

        # 提取第一作者和通讯作者
        first_author = authors[0]                # 第一作者
        rp_field = record.get('RP')
        corr_author = extract_corresponding_author(rp_field)

        selected_authors = set()
        if first_author:
            selected_authors.add(first_author)
        if corr_author and corr_author != first_author:
            selected_authors.add(corr_author)

        if not selected_authors:
            continue   # 该记录无可用的作者，跳过

        # 更新作者发文数和总被引
        tc = int(record.get('TC', 0))
        for author in selected_authors:
            author_pub_count[author] += 1
            author_total_cites[author] += tc

        # 为每篇参考文献添加这些作者
        for ref in refs:
            ref_to_authors[ref].update(selected_authors)

    # 计算作者耦合边权重（共同引用数）
    edge_weight = defaultdict(int)   # (author1, author2) -> 共同引用数
    for ref, authors in ref_to_authors.items():
        auth_list = list(authors)
        if len(auth_list) < 2:
            continue
        for i in range(len(auth_list)):
            for j in range(i+1, len(auth_list)):
                a1, a2 = auth_list[i], auth_list[j]
                # 排序以保证无向边一致性
                if a1 < a2:
                    edge_weight[(a1, a2)] += 1
                else:
                    edge_weight[(a2, a1)] += 1

    # 构建 networkx 图
    G = nx.Graph()
    for author in author_pub_count:
        G.add_node(author,
                   pub_count=author_pub_count[author],
                   total_cites=author_total_cites[author],
                   avg_cites=author_total_cites[author] / author_pub_count[author],
                   label=author)   # VOSviewer 标签
    for (a1, a2), weight in edge_weight.items():
        G.add_edge(a1, a2, weight=weight)

    print(f"作者耦合网络（仅第一/通讯作者） - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    # 删除可能含非法字符的属性（这里基本没有，但保留安全处理）
    for node, data in G.nodes(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
    for u, v, data in G.edges(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]

    # 导出 GML
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\作者耦合（只考虑通讯和一作）.gml"
    nx.write_gml(G, output_path)
    print(f"已导出作者耦合网络至: {output_path}")
    print("在 VOSviewer 中打开后，可使用 Overlay 视图按发文量(pub_count)、总被引(total_cites)或平均被引(avg_cites)着色。")

if __name__ == "__main__":
    main()