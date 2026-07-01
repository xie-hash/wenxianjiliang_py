import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ================== 0. 字体配置 ==================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ================== 1. 读取数据（UTF-8 with BOM） ==================
df = pd.read_csv('文献计量学/csv数据源/关键词爆发检测.csv', encoding='utf-8-sig')

# ================== 2. 数据处理 ==================
df = df.sort_values('爆发强度', ascending=False).reset_index(drop=True)

n = len(df)
print(f"共有 {n} 个关键词")

# ================== 3. 画布布局 ==================
fig = plt.figure(figsize=(16, 10))

ax1 = fig.add_axes([0.02, 0.08, 0.30, 0.85])
ax2 = fig.add_axes([0.34, 0.08, 0.64, 0.85])

y_pos = np.arange(n)
bar_h = 0.4

all_begin = df['爆发开始年份'].min()
all_end = df['爆发结束年份'].max()
t0, t1 = all_begin - 1, all_end + 1
if t0 > 2004:
    t0 = 2004

COLOR_NORMAL = "#7FCDCD"

# ================== 计算强度归一化 ==================
min_s = df['爆发强度'].min()
max_s = df['爆发强度'].max()
range_s = max_s - min_s if max_s > min_s else 1

# ================== 4. 右侧时间条（渐变） ==================
for i, row in df.iterrows():
    y = y_pos[i]
    ax2.barh(y, t1 - t0, left=t0, height=bar_h,
             color=COLOR_NORMAL, edgecolor='none', alpha=0.9)

    begin = row['爆发开始年份']
    end = row['爆发结束年份']
    strength = row['爆发强度']
    # 强度归一化到 [0, 1]
    norm = (strength - min_s) / range_s
    # 浅红 -> 深红渐变
    r = 0.8 - norm * 0.3
    g = 0.2 - norm * 0.2
    b = 0.2 - norm * 0.2
    color = (r, g, b)
    ax2.barh(y, end - begin, left=begin, height=bar_h,
             color=color, edgecolor='none', alpha=0.95)

ax2.set_xlim(t0 - 0.5, t1 + 0.5)
ax2.set_ylim(-0.6, n + 1.2)
ax2.set_yticks([])
xticks = range(int(t0), int(t1) + 1, 2)
ax2.set_xticks(xticks)
ax2.tick_params(axis='x', labelsize=11)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.xaxis.tick_top()
ax2.xaxis.set_label_position('top')

title_text = f"{t0} - {t1}"
ax2.text((t0 + t1) / 2, n + 0.6, title_text, fontsize=13, fontweight='bold',
         va='center', ha='center')

# ================== 5. 左侧表格 ==================
ax1.set_xlim(0, 1)
ax1.set_ylim(-0.6, n + 1.2)
ax1.axis('off')

headers = ["Keyword", "Strength", "Start", "End", "Records"]
col_x = [0.02, 0.48, 0.64, 0.78, 0.93]
header_y = n + 0.6

for h, x in zip(headers, col_x):
    align = 'left' if x == col_x[0] else 'center'
    ax1.text(x, header_y, h, fontsize=11, fontweight='bold', va='center', ha=align)

ax1.plot([0, 1], [header_y - 0.35, header_y - 0.35], color='black', linewidth=1.2)

for i, row in df.iterrows():
    y = y_pos[i]
    name = row['关键词']
    fontsize = 9 if len(name) > 20 else 10
    ax1.text(col_x[0], y, name, fontsize=fontsize, va='center', ha='left')
    ax1.text(col_x[1], y, f"{row['爆发强度']:.2f}", fontsize=10, va='center', ha='center')
    ax1.text(col_x[2], y, str(row['爆发开始年份']), fontsize=10, va='center', ha='center')
    ax1.text(col_x[3], y, str(row['爆发结束年份']), fontsize=10, va='center', ha='center')
    ax1.text(col_x[4], y, str(row['关键词总记录数']), fontsize=10, va='center', ha='center')

# ================== 6. 保存 ==================
output_path = '文献计量学/定稿图片/关键词爆发时间线.png'
plt.savefig(output_path, dpi=200, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"图片已保存到: {output_path}")
plt.show()
