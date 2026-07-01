import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def standardize_country(country):
    """
    标准化国家名称，将美国相关变体统一为 "United States"。
    策略：
    1. 去除首尾空格，转为大写用于检测。
    2. 如果字符串以 "USA" 结尾（忽略大小写），则为美国。
    3. 如果字符串中包含 " USA "（前后有空格或结尾），也为美国。
    4. 精确匹配常见美国变体。
    """
    if not country:
        return country
    original = country
    country_clean = country.strip()
    country_upper = country_clean.upper()
    
    # 检测是否以 "USA" 结尾
    if country_upper.endswith('USA'):
        return "United States"
    
    # 检测是否包含 " USA " 作为单词（前后有空格或位于开头/结尾）
    if re.search(r'\bUSA\b', country_upper):
        return "United States"
    
    # 精确匹配常见美国变体
    us_variants = {"USA", "U.S.A.", "UNITED STATES", "UNITED STATES OF AMERICA", "US", "U.S."}
    if country_upper in us_variants:
        return "United States"
    
    # 其他国家原样返回
    return country_clean

def extract_country_from_address(addr):
    """从地址字符串中提取国家名称（取最后一个逗号后部分），然后标准化"""
    if not addr:
        return None
    parts = addr.split(',')
    country = parts[-1].strip()
    if not country:
        return None
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

    # 调试：收集所有原始提取的国家（用于验证）
    raw_countries = []

    # 构建国家耦合网络
    ref_to_countries = defaultdict(set)   # 参考文献 -> 引用它的国家集合
    country_pub_count = Counter()         # 国家发文数
    country_total_cites = Counter()       # 国家所有文章的被引次数之和

    for record in rc_filtered:
        # 提取国家（已标准化）
        c1 = record.get('C1')
        countries = extract_countries_from_c1(c1)
        if not countries:
            continue

        # 记录原始国家（用于调试）
        raw_countries.extend(countries)

        # 提取参考文献
        refs = record.get('CR')
        if not refs:
            continue
        ref_strings = [str(ref) for ref in refs]

        # 更新国家发文数和总被引
        tc = int(record.get('TC', 0))
        for country in countries:
            country_pub_count[country] += 1
            country_total_cites[country] += tc

        # 为每篇参考文献添加这些国家
        for ref_str in ref_strings:
            ref_to_countries[ref_str].update(countries)

    # 调试：打印部分原始国家和标准化后的国家
    print("\n=== 调试：前30个标准化后的国家（去重） ===")
    unique_countries = sorted(set(raw_countries))
    for i, c in enumerate(unique_countries[:30]):
        print(f"{i+1}. {c}")

    # 计算国家耦合边权重
    edge_weight = defaultdict(int)
    for ref, countries in ref_to_countries.items():
        country_list = list(countries)
        if len(country_list) < 2:
            continue
        for i in range(len(country_list)):
            for j in range(i+1, len(country_list)):
                c1, c2 = country_list[i], country_list[j]
                if c1 < c2:
                    edge_weight[(c1, c2)] += 1
                else:
                    edge_weight[(c2, c1)] += 1

    # 构建 networkx 图
    G = nx.Graph()
    for country in country_pub_count:
        avg_cites = country_total_cites[country] / country_pub_count[country] if country_pub_count[country] > 0 else 0
        G.add_node(country,
                   pub_count=country_pub_count[country],
                   total_cites=country_total_cites[country],
                   avg_cites=avg_cites,
                   label=country)
    for (c1, c2), weight in edge_weight.items():
        G.add_edge(c1, c2, weight=weight)

    print(f"\n国家耦合网络（标准化后） - 节点数: {G.number_of_nodes()}, 边数: {G.number_of_edges()}")

    # 删除可能含非法字符的属性
    for node, data in G.nodes(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]
    for u, v, data in G.edges(data=True):
        for key in list(data.keys()):
            if '-' in key:
                del data[key]

    # 导出 GML
    output_path = r"C:\Users\谢\Desktop\vscodepj\文献计量学\vos图片\国家链接.gml"
    nx.write_gml(G, output_path)
    print(f"已导出国家耦合网络至: {output_path}")
    print("在 VOSviewer 中打开后，可使用 Overlay 视图按发文量(pub_count)、总被引(total_cites)或平均被引(avg_cites)着色。")

if __name__ == "__main__":
    main()