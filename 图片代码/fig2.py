
import os
import re
from collections import defaultdict
import pandas as pd
import metaknowledge as mk
import numpy as np
# ---------- 1. 文件路径配置 ----------
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

# ---------- 2. 读取所有数据 ----------
rc = mk.RecordCollection()
for f in list_file:
    if os.path.exists(f):
        rc += mk.RecordCollection(f)
        print(f"已加载 {f}，当前总记录数: {len(rc)}")
    else:
        print(f"文件不存在: {f}")

print(f"\n总记录数: {len(rc)}")

words_dic = defaultdict(list)

for rec in rc:
    words = rec.get("DE",'')
    py = int(rec.get("PY"))
    if type(py) != int:
        print("类型出错")
    if py == 2000:
        print(f"我找到了2000年的文献{words}")
    if py:
        for word in words:
            if word:
                words_dic[word].append(py)
            else:
                continue
    else:
        continue
word_result = []
for i,v in words_dic.items():
    word_name = i
    
    fre = np.array(v)
    
    word__w = [("name",word_name)]
    
   
    for i in range(2000,2027):
        freq = sum(np.where(fre==i))
        
        l = (f"{i}",len(freq))
       
        word__w.append(l)
       
  
    word__w.append(("num",len(v)))
  
    word__w = dict(word__w)
  
    word_result.append(word__w)


word_result = sorted(word_result,key= lambda x: x["num"],reverse=True)
word_result = pd.DataFrame(word_result[0:40])
word_result.to_csv(r"C:\Users\谢\Desktop\vscodepj\文献计量学\关键词分部.csv", index=False)


    
    
    

    