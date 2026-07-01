import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def normalize_journal(journal):
    """标准化期刊名称：去除首尾空格、合并内部多空格"""
    if not journal:
        return ""
    journal = journal.strip()
    journal = re.sub(r'\s+', ' ', journal)
    return journal

def extract_journal(record):
    """从 SO 字段提取期刊名称"""
    so = record.get('SO')
    if not so:
        return None
    if isinstance(so, str):
        return normalize_journal(so)
    # 有时 SO 可能是列表，取第一个
    return normalize_journal(so[0]) if so else None

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

    # 构建期刊耦合网络（基于参考文献的共引关系）
    # 1. 统计每个期刊的发文数（作为来源期刊的出现次数）
    journal_pub_count = Counter()
    # 2. 记录每条记录的期刊及其参考文献列表
    ref_to_journals = defaultdict(set)   # 参考文献 -> 引用它的期刊集合
    # 3. 同时记录每条记录对应的期刊
    for record in rc_filtered:
        journal = extract_journal(record)
        if not journal:
            continue
        journal_pub_count[journal] += 1

        # 提取参考文献
        refs = record.get('CR')
        if not refs:
            continue
        ref_strings = [str(ref) for ref in refs]

        # 为每篇参考文献添加该期刊
        for ref_str in ref_strings:
            ref_to_journals[ref_str].add(journal)

    # 计算期刊耦合边权重（两期刊共同引用的参考文献数量）
    edge_weight = defaultdict(int)
    for ref, journals in ref_to_journals.items():
        journal_list = list(journals)
        if len(journal_list) < 2:
            continue
        for i in range(len(journal_list)):
            for j in range(i+1, len(journal_list)):
                j1, j2 = journal_list[i], journal_list[j]
                if j1 < j2:
                    edge_weight[(j1, j2)] += 1
                else:
                    edge_weight[(j2, j1)] += 1

    # 构建 NetworkX 图
    G = nx.Graph()
    for journal, pub_cnt in journal_pub_count.items():
        G.add_node(journal, pub_count=pub_cnt, label=journal)
    for (j1, j2), weight in edge_weight.items():
        G.add_edge(j1, j2, weight=weight)

    print(f"期刊耦合网络 - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

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
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\期刊链接.gml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nx.write_gml(G, output_path)
    print(f"已导出期刊耦合网络至: {output_path}")
    print("在 VOSviewer 中打开后，可使用 Overlay 视图按 pub_count（期刊发文数）着色，节点大小即代表发文量。")

if __name__ == "__main__":
    main()