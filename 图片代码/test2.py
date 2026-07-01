import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ================== 1. 构造示例数据（你只需替换这部分） ==================
data = {
    "Keywords": [
        "fragment", "heavy chain antibody", "escherichia coli", "carcinoembryonic antigen",
        "antibody fragment", "cancer therapy", "growth factor receptor", "light chain",
        "in vivo", "mice", "quantum dot", "breast cancer", "crystal structure",
        "selection", "intrabody", "living cell", "fusion protein", "angiogenesis",
        "molecule", "t cell"
    ],
    "Year": [2004]*20,
    "Strength": [17.24, 5.76, 5.04, 3.3, 4.77, 7.07, 6.42, 4.22, 5.9, 6.71,
                  6.56, 5.02, 4.7, 3.8, 3.23, 4.47, 3.6, 4.04, 3.48, 4.5],
    "Begin": [2004, 2004, 2004, 2004, 2008, 2009, 2009, 2009, 2010, 2011,
              2012, 2012, 2012, 2012, 2013, 2014, 2015, 2016, 2016, 2018],
    "End":   [2013, 2017, 2017, 2010, 2017, 2015, 2017, 2012, 2012, 2015,
              2017, 2016, 2016, 2014, 2017, 2016, 2018, 2020, 2018, 2019]
}

df = pd.read_csv("C:\\Users\\谢\\Desktop\\vscodepj\\文献计量学\\csv数据源\\参考文献爆发00-19,15csv.csv", encoding="gbk")
df = df.rename(columns={"参考文献标识": "Keywords", "参考文献出版年份": "Year", "爆发强度": "Strength", "爆发开始年份": "Begin", "爆发结束年份": "End"})
# 按 Strength 降序排列（也可按原图顺序，去掉排序即可）
print(df.head(10))
df = df[["Keywords", "Year", "Strength", "Begin", "End"]]
df = df.sort_values("Strength", ascending=False).reset_index(drop=True)

# ================== 2. 画布布局（再次加宽左侧） ==================
fig = plt.figure(figsize=(14, 10))

# 【调整】左侧 0.34，右侧从 0.38 开始，宽度 0.60
ax1 = fig.add_axes([0.02, 0.08, 0.34, 0.85])
ax2 = fig.add_axes([0.38, 0.08, 0.60, 0.85])

n = len(df)
y_pos = np.arange(n)
bar_h = 0.4
t0, t1 = 2004, 2023

COLOR_BURST = "#D62728"
COLOR_NORMAL = "#7FCDCD"

# ================== 3. 右侧时间条（不变） ==================
for i, row in df.iterrows():
    y = y_pos[i]
    ax2.barh(y, t1 - t0, left=t0, height=bar_h,
             color=COLOR_NORMAL, edgecolor='none', alpha=0.9)
    ax2.barh(y, row["End"] - row["Begin"], left=row["Begin"], height=bar_h,
             color=COLOR_BURST, edgecolor='none', alpha=0.95)

ax2.set_xlim(2003.5, 2023.5)
ax2.set_ylim(-0.6, n + 1.2)
ax2.set_yticks([])
ax2.set_xticks(range(2004, 2024, 2))
ax2.tick_params(axis='x', labelsize=11)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.xaxis.tick_top()
ax2.xaxis.set_label_position('top')
ax2.text(2013.5, n + 0.6, "2004 - 2023", fontsize=13, fontweight='bold',
         va='center', ha='center')

# ================== 4. 左侧文字表格（重点调整） ==================
ax1.set_xlim(0, 1)
ax1.set_ylim(-0.6, n + 1.2)
ax1.axis('off')

headers = ["Keywords", "Year", "Strength", "Begin", "End"]

# 【核心调整】列间距进一步拉大
# 0.02(左对齐) | 0.46 | 0.63 | 0.78 | 0.93
# 这样相邻列间距 >= 0.15，文字不会重叠
col_x = [0.02, 0.46, 0.63, 0.78, 0.93]
header_y = n + 0.6

# 画表头：Keywords 左对齐，其余居中
for h, x in zip(headers, col_x):
    align = 'left' if x == col_x[0] else 'center'
    ax1.text(x, header_y, h, fontsize=11, fontweight='bold', va='center', ha=align)

# 分隔线
ax1.plot([0, 1], [header_y - 0.35, header_y - 0.35], color='black', linewidth=1.2)

# 画数据行
for i, row in df.iterrows():
    y = y_pos[i]
    ax1.text(col_x[0], y, row["Keywords"], fontsize=10, va='center', ha='left')
    ax1.text(col_x[1], y, str(row["Year"]), fontsize=10, va='center', ha='center')
    ax1.text(col_x[2], y, f"{row['Strength']:.2f}", fontsize=10, va='center', ha='center')
    ax1.text(col_x[3], y, str(row["Begin"]), fontsize=10, va='center', ha='center')
    ax1.text(col_x[4], y, str(row["End"]), fontsize=10, va='center', ha='center')


plt.show()
print("表头间距已彻底拉开！")