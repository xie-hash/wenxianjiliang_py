import os
import re
import metaknowledge as mk
from collections import defaultdict
import pandas as pd
import numpy as np

# ---------- 定义 h 指数和 g 指数函数 ----------
def h_index(citations: list) -> int:
    citations.sort(reverse=True)
    for i, c in enumerate(citations, start=1):
        if c < i:
            return i - 1
    return len(citations)

def g_index(citations: list) -> int:
    if not citations:
        return 0
    citations.sort(reverse=True)
    total = 0
    for i, c in enumerate(citations, start=1):
        total += c
        if total < i * i:
            return i - 1
    return len(citations)


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

print(f"\n总记录数: {len(rc)}")

author_data = {}

for rec in rc:
    full_name = rec.get("AF")
    Tx_Au = rec.get("RP")
    OI = rec.get("OI")
    citend = rec.get("TC")
    PY = rec.get("PY")
    if Tx_Au:
        Tx_Au = [name.split("(corresponding author)")[0].strip() for name in Tx_Au.split(";")]
        full_name.extend(Tx_Au)
        Oi = {}
        if type(OI) == type([1]):
            for i in OI:
                k = [n for n in i.split(",") if n]
                if len(k)==2:
                    name = k[0]
                    oi = k[1]
                    Oi[name] = oi
            for name in Oi.keys():
                l = [n for n in full_name if name in n ]
                if l:
                    if Oi[name] not in author_data.keys():
                        author_data[Oi[name]] = {
                            "TC" : [citend],
                            "py" : [PY],
                            "au_name" : l[0]
                            }
                    else:
                        author_data[Oi[name]]["TC"].append(citend)
                        author_data[Oi[name]]["py"].append(PY)
                else:
                    continue

result = []
for i in author_data.items():
    cit = i[1]["TC"]
    year = min(i[1]["py"])
    try:
        h = h_index(cit)
        g = g_index(cit)
        if year != 2026:
            m = round(h/(2026-year),2)
        else:
            continue
    except Exception as e:
        print(f"我的错误是{e}")
    result.append({
        "author full name" : " ".join(i[1]["au_name"].split(",")),
        "TP":len(cit),
        "TC":sum(cit),
        "TC/TP":round(sum(cit)/len(cit),2),
        "h-index":h,
        "g-index":g,
        "m-index":m,
        "PY":year
    })
result_TC = sorted(result,key= lambda x : x["TC"],reverse=True)[:10]
result_TP = sorted(result,key= lambda x : x["TP"],reverse=True)[:10]
result = pd.DataFrame(result_TC)
result.to_csv(r"C:\Users\谢\Desktop\vscodepj\文献计量学\作者情况_被引量.csv", index=False)
result = pd.DataFrame(result_TP)
result.to_csv(r"C:\Users\谢\Desktop\vscodepj\文献计量学\作者情况_发文量.csv", index=False)
