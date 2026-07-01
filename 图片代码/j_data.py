"""
- **PT** – Publication Type（文献类型，如 `J` 可能表示 Journal Article）
- **AU** – Author（作者，通常为缩写形式）
- **AF** – Author Full（作者全名，与 `AU` 对应，给出完整的姓和名）
- **TI** – Title（文献标题）
- **SO** – Source（来源，如期刊名称）
- **LA** – Language（语言）
- **DT** – Document Type（文献类型，如 `Review`）
- **ID** – Identifier（此处为关键词或标识符，常与主题词相关）
- **AB** – Abstract（摘要）
- **C1** – Author Affiliation（作者所属机构及地址）
- **C3** – Conference / Corporate / Contract 信息（此处显示为研究资助或合同号，也可能是作者所属公司的补充）
- **RP** – Reprint Author（通讯作者，即负责接收信件的作者）
- **EM** – Email（通讯作者的电子邮件）
- **RI** – Researcher ID（科研人员ID，如 Publons/Web of Science 的标识）
- **OI** – ORCID iD（开放研究者与贡献者身份识别码）
- **FU** – Funding（资助来源）
- **FX** – Funding Text（资助详情文本）
- **CR** – Cited References（引用的参考文献列表）
"""

import os
import metaknowledge as mk
from collections import Counter
from collections import defaultdict
import pandas as pd

def h(cite:list) -> int:
    cite.sort(reverse=True)
    for i in range(len(cite)):
        if cite[i] >= i+1:
            continue
        else:
            return i
    return len(cite)
def g(cite: list) -> int:
    if not cite:
        return 0
    cite.sort(reverse=True)
    total = 0
    for i, c in enumerate(cite, start=1):
        total += c
        if total < i * i:
            return i - 1
    return len(cite)
# ---------- 1. 读取所有数据 ----------
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

## ---------- 2. 初始化计数表格 ----------
dict_j = defaultdict(list)
dict_j_data = defaultdict(list) # 数量，贡献率，引用总数，h，g
# ----------- 3. 读取数据 ---------------
for rec in rc:
    j_name = rec.get("SO")
    j_cite = rec.get("TC")
    if j_name:
        dict_j[j_name].append(j_cite)


rows = []
for name, cite in dict_j.items():
    num = len(cite)
    l = f"{num / 4088 * 100:.2f}%"   # 贡献率
    sum_cite = sum(cite)
    h_cite = h(cite)
    g_cite = g(cite)
    rows.append({
        "journal": name,
        "NP": num,
        "contribution rate": l,
        "TC": sum_cite,
        "h-index": h_cite,
        "g-index": g_cite
    })

# 创建 DataFrame 并按发文量降序排序
df = pd.DataFrame(rows)
df_sorted = df.sort_values(by="NP", ascending=False)

# 保存到 CSV
df_sorted.to_csv(r"C:\Users\谢\Desktop\vscodepj\文献计量学\期刊情况.csv", index=False)


