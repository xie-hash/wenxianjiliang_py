import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

# ================== 0. 字体配置 ==================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ================== 辅助函数 ==================
def extract_author_year(ref_id):
    """从参考文献标识中提取 '作者, 年份'，如 'Hess B, 2008'"""
    parts = ref_id.split(',')
    if len(parts) >= 2:
        author = parts[0].strip()
        year = parts[1].strip()
        if year.isdigit():
            return f"{author}, {year}"
    return ref_id[:40]

def extract_doi(ref_example):
    """从参考文献原始示例中提取 DOI 号"""
    match = re.search(r'DOI\s+\[?([^\]]+)\]?', ref_example)
    if match:
        doi = match.group(1).strip()
        if ',' in doi:
            doi = doi.split(',')[0].strip()
        doi = doi.rstrip(',.;')
        if len(doi) > 45:
            doi = doi[:42] + '...'
        return doi
    return ''

# ================== 计算归一化范围 ==================
def get_strength_range(df):
    """获取全局强度最小最大值"""
    return df['爆发强度'].min(), df['爆发强度'].max()

# ================== 颜色映射函数 ==================
def strength_to_color(strength, min_s, max_s):
    """将爆发强度映射为渐变色，强度越高颜色越深"""
    range_s = max_s - min_s if max_s > min_s else 1
    norm = (strength - min_s) / range_s  # 0~1
    # 浅红 (0.8,0.2,0.2) -> 深红 (0.5,0,0)
    r = 0.8 - norm * 0.3
    g = 0.2 - norm * 0.2
    b = 0.2 - norm * 0.2
    return (r, g, b)

def draw_ref_burst_chart(csv_path, output_path, title_prefix):
    """绘制参考文献爆发时间线图"""
    
    df = pd.read_csv(csv_path, encoding='gbk')
    df = df.sort_values('爆发强度', ascending=False).head(15).reset_index(drop=True)
    
    n = len(df)
    print(f"{title_prefix}: 共 {n} 条参考文献")
    
    ref_names = []
    doi_list = []
    for _, row in df.iterrows():
        ref_names.append(extract_author_year(row['参考文献标识']))
        doi_list.append(extract_doi(row['参考文献原始示例']))
    
    # 计算全局强度范围
    min_s, max_s = get_strength_range(df)
    
    fig = plt.figure(figsize=(18, 10))
    ax1 = fig.add_axes([0.02, 0.08, 0.44, 0.85])
    ax2 = fig.add_axes([0.48, 0.08, 0.50, 0.85])
    
    y_pos = np.arange(n)
    bar_h = 0.4
    
    all_begin = df['爆发开始年份'].min()
    all_end = df['爆发结束年份'].max()
    t0 = min(all_begin - 1, 2000)
    t1 = all_end + 1
    
    COLOR_NORMAL = "#72C9C9"
    
    # ====== 5. 右侧时间条（渐变） ======
    for i, row in df.iterrows():
        y = y_pos[i]
        ax2.barh(y, t1 - t0, left=t0, height=bar_h,
                 color=COLOR_NORMAL, edgecolor='none', alpha=0.9)
        
        begin = row['爆发开始年份']
        end = row['爆发结束年份']
        strength = row['爆发强度']
        color = strength_to_color(strength, min_s, max_s)
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
    
    # ====== 6. 左侧表格 ======
    ax1.set_xlim(0, 1)
    ax1.set_ylim(-0.6, n + 1.2)
    ax1.axis('off')
    
    headers = ["Reference", "Strength", "Start", "End", "Citations"]
    col_x = [0.02, 0.62, 0.76, 0.86, 0.96]
    header_y = n + 0.6
    
    for h, x in zip(headers, col_x):
        align = 'left' if x == col_x[0] else 'center'
        ax1.text(x, header_y, h, fontsize=11, fontweight='bold', va='center', ha=align)
    
    ax1.plot([0, 1], [header_y - 0.35, header_y - 0.35], color='black', linewidth=1.2)
    
    for i, row in df.iterrows():
        y = y_pos[i]
        ref_name = ref_names[i]
        doi = doi_list[i]
        
        ax1.text(col_x[0], y + 0.12, ref_name, fontsize=10, fontweight='bold',
                 va='center', ha='left')
        if doi:
            ax1.text(col_x[0], y - 0.12, doi, fontsize=7.5, color='gray',
                     va='center', ha='left')
        ax1.text(col_x[1], y, f"{row['爆发强度']:.2f}", fontsize=10,
                 va='center', ha='center')
        ax1.text(col_x[2], y, str(int(row['爆发开始年份'])), fontsize=10,
                 va='center', ha='center')
        ax1.text(col_x[3], y, str(int(row['爆发结束年份'])), fontsize=10,
                 va='center', ha='center')
        ax1.text(col_x[4], y, str(row['参考文献总被引']), fontsize=10,
                 va='center', ha='center')
    
    plt.savefig(output_path, dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"图片已保存到: {output_path}")
    plt.close()


# ================== 主程序 ==================
draw_ref_burst_chart(
    csv_path='文献计量学/csv数据源/参考文献爆发00-19,15csv.csv',
    output_path='文献计量学/定稿图片/参考文献爆发00-19.png',
    title_prefix='2000-2019'
)

draw_ref_burst_chart(
    csv_path='文献计量学/csv数据源/爆发20-25,15.csv',
    output_path='文献计量学/定稿图片/参考文献爆发20-25.png',
    title_prefix='2020-2025'
)

print("两张图全部生成完成！")
