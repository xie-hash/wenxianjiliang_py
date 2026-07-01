import networkx as nx
import metaknowledge as mk
import os

def main():
    # 文件列表（请根据实际路径修改）
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

    # 创建筛选后的集合
    rc_filtered = mk.RecordCollection(valid_records)

    # 构建文献耦合网络（节点为 UT，边权重为耦合强度）
    G = rc_filtered.networkBibCoupling()
    print(f"网络 - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    # 为节点添加属性（标题、作者、年份、期刊、被引次数）
    record_dict = {r.get('UT'): r for r in rc_filtered}
    titles = {}
    authors = {}
    years = {}
    journals = {}
    times_cited = {}
    for ut, rec in record_dict.items():
        titles[ut] = rec.get('TI', '')[:200]           # 标题，截断过长
        authors[ut] = '; '.join(rec.get('AU', []))     # 作者列表
        years[ut] = rec.get('PY', '')
        journals[ut] = rec.get('SO', '')
        times_cited[ut] = int(rec.get('TC', 0))

    nx.set_node_attributes(G, titles, 'title')
    nx.set_node_attributes(G, authors, 'authors')
    nx.set_node_attributes(G, years, 'year')
    nx.set_node_attributes(G, journals, 'journal')
    nx.set_node_attributes(G, times_cited, 'times_cited')
    nx.set_node_attributes(G, titles, 'label')  # VOSviewer 默认使用 label 作为节点标签

    # 删除 metaknowledge 添加的内部属性 'MK-ID'（非 GML 合法键名）
    for node, data in G.nodes(data=True):
        data.pop('MK-ID', None)  # 安全删除，若不存在则忽略
    for u, v, data in G.edges(data=True):
        data.pop('MK-ID', None)

    # 导出为 GML 格式
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\文章耦合"
    nx.write_gml(G, output_path)
    print(f"已导出文献耦合网络至: {output_path}")
    print("在 VOSviewer 中打开该文件后，可切换到 Overlay 视图，")
    print("选择 Color 为 times_cited 或 year 来根据被引次数或年份着色。")

if __name__ == "__main__":
    main()