import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter

def extract_corresponding_author(rp_field):
    """从 RP 字段提取通讯作者名"""
    if not rp_field:
        return None
    if isinstance(rp_field, list):
        rp_field = rp_field[0] if rp_field else ''
    match = re.search(r'([^,]+?)\s*\(reprint author\)', rp_field)
    return match.group(1).strip() if match else None

def extract_organizations(c1_field):
    """从 C1 字段提取机构名"""
    if not c1_field:
        return []
    if isinstance(c1_field, str):
        addr_list = c1_field.split(';')
    else:
        addr_list = c1_field
    orgs = []
    for addr in addr_list:
        addr = addr.strip()
        parts = addr.split(',')
        if parts:
            orgs.append(parts[0].strip())
    return list(set(orgs))

def extract_journals_from_refs(refs):
    """从参考文献列表中提取期刊名（取第三个逗号部分）"""
    journals = []
    for ref in refs:
        # 如果 ref 不是字符串（可能是 Citation 对象），转为字符串
        if not isinstance(ref, str):
            ref = str(ref)
        parts = ref.split(',')
        if len(parts) >= 3:
            journals.append(parts[2].strip())
    return list(set(journals))

def compute_author_tls(rc_filtered):
    """作者共现网络 TLS（仅第一/通讯作者）"""
    edge_weight = defaultdict(int)
    for record in rc_filtered:
        authors = record.get('AU')
        if not authors:
            continue
        first = authors[0]
        corr = extract_corresponding_author(record.get('RP'))
        selected = {first}
        if corr and corr != first:
            selected.add(corr)
        auth_list = list(selected)
        if len(auth_list) < 2:
            continue
        for i in range(len(auth_list)):
            for j in range(i+1, len(auth_list)):
                a1, a2 = auth_list[i], auth_list[j]
                if a1 < a2:
                    edge_weight[(a1, a2)] += 1
                else:
                    edge_weight[(a2, a1)] += 1
    tls = defaultdict(int)
    for (a1, a2), w in edge_weight.items():
        tls[a1] += w
        tls[a2] += w
    return dict(tls)

def compute_org_tls(rc_filtered):
    """机构合作网络 TLS"""
    edge_weight = defaultdict(int)
    for record in rc_filtered:
        c1 = record.get('C1')
        if not c1:
            continue
        orgs = extract_organizations(c1)
        if len(orgs) < 2:
            continue
        for i in range(len(orgs)):
            for j in range(i+1, len(orgs)):
                o1, o2 = orgs[i], orgs[j]
                if o1 < o2:
                    edge_weight[(o1, o2)] += 1
                else:
                    edge_weight[(o2, o1)] += 1
    tls = defaultdict(int)
    for (o1, o2), w in edge_weight.items():
        tls[o1] += w
        tls[o2] += w
    return dict(tls)

def compute_journal_tls(rc_filtered):
    """期刊共被引网络 TLS"""
    edge_weight = defaultdict(int)
    for record in rc_filtered:
        refs = record.get('CR')
        if not refs:
            continue
        journals = extract_journals_from_refs(refs)
        if len(journals) < 2:
            continue
        for i in range(len(journals)):
            for j in range(i+1, len(journals)):
                j1, j2 = journals[i], journals[j]
                if j1 < j2:
                    edge_weight[(j1, j2)] += 1
                else:
                    edge_weight[(j2, j1)] += 1
    tls = defaultdict(int)
    for (j1, j2), w in edge_weight.items():
        tls[j1] += w
        tls[j2] += w
    return dict(tls)

def compute_keyword_tls(rc_filtered):
    """关键词共现网络 TLS（合并 DE 和 ID）"""
    edge_weight = defaultdict(int)
    for record in rc_filtered:
        de = record.get('DE', [])
        id_ = record.get('ID', [])
        keywords = list(set(de + id_))
        if len(keywords) < 2:
            continue
        for i in range(len(keywords)):
            for j in range(i+1, len(keywords)):
                k1, k2 = keywords[i], keywords[j]
                if k1 < k2:
                    edge_weight[(k1, k2)] += 1
                else:
                    edge_weight[(k2, k1)] += 1
    tls = defaultdict(int)
    for (k1, k2), w in edge_weight.items():
        tls[k1] += w
        tls[k2] += w
    return dict(tls)

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

    valid_records = [r for r in rc if int(r.get('TC', 0)) >= 30]
    print(f"满足被引≥30的记录数: {len(valid_records)}")
    if not valid_records:
        print("没有满足条件的记录，程序退出。")
        return {}, {}, {}, {}

    rc_filtered = mk.RecordCollection(valid_records)

    author_tls = compute_author_tls(rc_filtered)
    org_tls = compute_org_tls(rc_filtered)
    journal_tls = compute_journal_tls(rc_filtered)
    keyword_tls = compute_keyword_tls(rc_filtered)

    # 可选：打印前10项查看结果
    print("\n=== 作者共现网络 TLS（第一/通讯作者）前10 ===")
    for author, tls in sorted(author_tls.items(), key=lambda x: -x[1])[:10]:
        print(f"{author}: {tls}")

    print("\n=== 机构合作网络 TLS 前10 ===")
    for org, tls in sorted(org_tls.items(), key=lambda x: -x[1])[:10]:
        print(f"{org}: {tls}")

    print("\n=== 期刊共被引网络 TLS 前10 ===")
    for journal, tls in sorted(journal_tls.items(), key=lambda x: -x[1])[:10]:
        print(f"{journal}: {tls}")

    print("\n=== 关键词共现网络 TLS 前10 ===")
    for kw, tls in sorted(keyword_tls.items(), key=lambda x: -x[1])[:10]:
        print(f"{kw}: {tls}")

    return author_tls, org_tls, journal_tls, keyword_tls

if __name__ == "__main__":
    author_tls, org_tls, journal_tls, keyword_tls = main()