#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Search Strategy Visualization - SVG, B&W, Elegant Academic Style
Structured according to user's specific classification needs.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.lines as mlines

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def draw_search_strategy(output_path='search_strategy.svg'):
    """Black & white, elegant, academic search strategy tree."""
    
    fig, ax = plt.subplots(1, 1, figsize=(9.5, 15.5))
    ax.set_xlim(0, 9.5)
    ax.set_ylim(0, 15.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # ---- Utility functions ----
    def box(ax, x, y, text, w, h, fs=8, lw=0.6, shade=False, bold=False, align='center'):
        """Draw a rounded rectangle with text."""
        fc = '#F7F7F7' if shade else 'white'
        ec = 'black'
        lw_ = 0.8 if shade else lw
        box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                             boxstyle='round,pad=0.08',
                             facecolor=fc, edgecolor=ec, linewidth=lw_, zorder=2)
        ax.add_patch(box)
        fw = 'bold' if bold else 'normal'
        ax.text(x, y, text, ha=align, va='center', fontsize=fs,
                color='black', fontweight=fw, zorder=3)

    def vline(ax, x, y1, y2, lw=0.5):
        ax.plot([x, x], [y1, y2], color='black', linewidth=lw, zorder=1)

    def hline(ax, y, x1, x2, lw=0.5):
        ax.plot([x1, x2], [y, y], color='black', linewidth=lw, zorder=1)

    def dot(ax, x, y, r=0.03):
        ax.scatter([x], [y], s=8, c='black', zorder=4)

    # ============================================================
    # TITLE
    # ============================================================
    title_y = 15.1
    ax.text(4.75, title_y, 'Literature Search Strategy', ha='center', va='center',
            fontsize=14, fontweight='bold', color='black')
    # underline
    hline(ax, title_y - 0.3, 3.2, 6.3, lw=1.2)

    # ============================================================
    # DIMENSION 1: Technical Methodology
    # ============================================================
    dim1_y = 13.8
    box(ax, 2.0, dim1_y, 'Dimension One : Technical Methodology', 7.8, 0.55,
        fs=9.5, shade=True, bold=True)

    # Desc label
    ax.text(4.75, dim1_y - 0.6, 'Multiple subcategories connected by "OR" — representing various computational approaches',
            ha='center', va='center', fontsize=7, color='#444444', fontstyle='italic')

    # --- Category 1: AI & Machine Learning ---
    cat1_x, cat1_y = 1.2, 12.0
    
    # Connector: dim1 -> cat1
    vline(ax, 2.0, dim1_y - 0.275, 12.35, lw=0.6)
    hline(ax, 12.35, 1.0, 3.0, lw=0.6)
    vline(ax, 1.2, 12.35, 12.3, lw=0.6)
    
    box(ax, cat1_x, cat1_y, '1. Artificial Intelligence & Machine Learning', 4.8, 0.5,
        fs=8, shade=True, bold=False)
    
    kw1 = ['"artificial\nintelligence"', '"machine\nlearning"', '"deep\nlearning"', '"neural\nnetwork"']
    kx1 = [-0.1, 0.8, 1.7, 2.6]
    kw1_y = 10.8
    kx_adj1 = [x + 0.3 for x in kx1]  # shift right slightly
    
    vline(ax, cat1_x, cat1_y - 0.25, 11.15, lw=0.5)
    hline(ax, 11.15, kx_adj1[0], kx_adj1[-1], lw=0.5)
    for i, k in enumerate(kx_adj1):
        vline(ax, k, 11.15, kw1_y + 0.2, lw=0.4)
        box(ax, k, kw1_y, kw1[i], 1.1, 0.45, fs=5.5, lw=0.4)
        if i < len(kx_adj1) - 1:
            ox = (kx_adj1[i] + kx_adj1[i+1]) / 2
            ax.text(ox, 11.15 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')

    # --- Category 2: Computational Simulation & Molecular Modeling ---
    cat2_x, cat2_y = 3.2, 9.2
    
    vline(ax, 2.0, dim1_y - 0.275, 12.35, lw=0.6)
    # Already have hline at 12.35
    vline(ax, 3.2, 12.35, 9.5, lw=0.6)
    
    box(ax, cat2_x, cat2_y, '2. Classical Computational Simulation & Molecular Modeling', 5.5, 0.5,
        fs=8, shade=True, bold=False)
    
    # Sub-label for general simulation
    sub2_y = 8.2
    ax.text(0.7, sub2_y + 0.25, 'General simulation:', ha='center', va='center',
            fontsize=6, fontstyle='italic', color='#333333')
    kw2_1 = ['"computational\nmodel*"', '"in silico"', '"computer\nsimulation"']
    kx2_1 = [-0.2, 0.7, 1.6]
    kx_adj2_1 = [x + 0.45 for x in kx2_1]
    
    vline(ax, cat2_x, cat2_y - 0.25, 8.55, lw=0.5)
    hline(ax, 8.55, kx_adj2_1[0], kx_adj2_1[-1], lw=0.5)
    for i, k in enumerate(kx_adj2_1):
        vline(ax, k, 8.55, sub2_y + 0.2, lw=0.4)
        box(ax, k, sub2_y, kw2_1[i], 1.1, 0.45, fs=5.5, lw=0.4)
        if i < len(kx_adj2_1) - 1:
            ox = (kx_adj2_1[i] + kx_adj2_1[i+1]) / 2
            ax.text(ox, 8.55 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')
    
    # Sub-label for structural simulation
    sub2b_y = 7.2
    ax.text(2.2, sub2b_y + 0.25, 'Structural simulation:', ha='center', va='center',
            fontsize=6, fontstyle='italic', color='#333333')
    kw2_2 = ['"molecular\ndocking"\n(molecular docking)', '"molecular\ndynamics"\n(molecular dynamics)']
    kx2_2 = [2.0, 3.4]
    
    hline(ax, 7.55, kx2_2[0], kx2_2[-1], lw=0.5)
    for i, k in enumerate(kx2_2):
        vline(ax, k, 7.55, sub2b_y + 0.2, lw=0.4)
        box(ax, k, sub2b_y, kw2_2[i], 1.6, 0.6, fs=5.5, lw=0.4)
        if i < len(kx2_2) - 1:
            ox = (kx2_2[i] + kx2_2[i+1]) / 2
            ax.text(ox, 7.55 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')
    
    # connector between general and structural
    vline(ax, cat2_x, cat2_y - 0.25, 8.55, lw=0.5)
    vline(ax, cat2_x, sub2_y - 0.225, 7.55, lw=0.4)

    # --- Category 3: Informatics & QSAR ---
    cat3_x, cat3_y = 5.4, 12.0
    
    vline(ax, 2.0, dim1_y - 0.275, 12.35, lw=0.6)
    # hline already at 12.35
    vline(ax, 5.4, 12.35, 12.3, lw=0.6)
    
    box(ax, cat3_x, cat3_y, '3. Informatics & QSAR', 4.5, 0.5,
        fs=8, shade=True, bold=False)
    
    # Sub-label for discipline layer
    sub3_y = 10.8
    ax.text(4.3, sub3_y + 0.25, 'Discipline layer:', ha='center', va='center',
            fontsize=6, fontstyle='italic', color='#333333')
    kw3_1 = ['"cheminformat*"\n(chemical informatics)', '"bioinformat*"\n(bioinformatics)', '"pharmacoinformat*"\n(pharmaceutical informatics)']
    kx3_1 = [3.4, 4.8, 6.2]
    
    vline(ax, cat3_x, cat3_y - 0.25, 11.15, lw=0.5)
    hline(ax, 11.15, kx3_1[0], kx3_1[-1], lw=0.5)
    for i, k in enumerate(kx3_1):
        vline(ax, k, 11.15, sub3_y + 0.2, lw=0.4)
        box(ax, k, sub3_y, kw3_1[i], 1.5, 0.6, fs=5.5, lw=0.4)
        if i < len(kx3_1) - 1:
            ox = (kx3_1[i] + kx3_1[i+1]) / 2
            ax.text(ox, 11.15 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')
    
    # Sub-label for model layer
    sub3b_y = 9.8
    ax.text(4.3, sub3b_y + 0.25, 'Model layer:', ha='center', va='center',
            fontsize=6, fontstyle='italic', color='#333333')
    kw3_2 = ['"quantitative\nstructure-activity\nrelationship"', '"QSAR"']
    kx3_2 = [4.0, 5.4]
    
    vline(ax, cat3_x, sub3_y - 0.3, 10.15, lw=0.4)
    hline(ax, 10.15, kx3_2[0], kx3_2[-1], lw=0.5)
    for i, k in enumerate(kx3_2):
        vline(ax, k, 10.15, sub3b_y + 0.2, lw=0.4)
        box(ax, k, sub3b_y, kw3_2[i], 1.6, 0.6, fs=5.5, lw=0.4)
        if i < len(kx3_2) - 1:
            ox = (kx3_2[i] + kx3_2[i+1]) / 2
            ax.text(ox, 10.15 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')

    # --- Category 4: Network & Systems Biology / Repurposing ---
    cat4_x, cat4_y = 7.6, 12.0
    
    vline(ax, 2.0, dim1_y - 0.275, 12.35, lw=0.6)
    # hline already at 12.35
    vline(ax, 7.6, 12.35, 12.3, lw=0.6)
    
    box(ax, cat4_x, cat4_y, '4. Network & Systems Biology / Repurposing Strategies', 5.2, 0.5,
        fs=8, shade=True, bold=False)
    
    # Sub-label system level
    sub4_y = 10.8
    ax.text(6.5, sub4_y + 0.25, 'System-level:', ha='center', va='center',
            fontsize=6, fontstyle='italic', color='#333333')
    kw4_1 = ['"network\npharmacology"\n(network pharmacology)', '"systems\nbiology"\n(systems biology)']
    kx4_1 = [5.9, 7.3]
    
    vline(ax, cat4_x, cat4_y - 0.25, 11.15, lw=0.5)
    hline(ax, 11.15, kx4_1[0], kx4_1[-1], lw=0.5)
    for i, k in enumerate(kx4_1):
        vline(ax, k, 11.15, sub4_y + 0.2, lw=0.4)
        box(ax, k, sub4_y, kw4_1[i], 1.6, 0.6, fs=5.5, lw=0.4)
        if i < len(kx4_1) - 1:
            ox = (kx4_1[i] + kx4_1[i+1]) / 2
            ax.text(ox, 11.15 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')
    
    # Sub-label strategy level
    sub4b_y = 9.8
    ax.text(6.5, sub4b_y + 0.25, 'Strategy-level:', ha='center', va='center',
            fontsize=6, fontstyle='italic', color='#333333')
    kw4_2 = ['"drug\nrepurposing"\n(drug repurposing)', '"virtual\nscreening"\n(virtual screening)']
    kx4_2 = [6.2, 7.8]
    
    vline(ax, cat4_x, sub4_y - 0.3, 10.15, lw=0.4)
    hline(ax, 10.15, kx4_2[0], kx4_2[-1], lw=0.5)
    for i, k in enumerate(kx4_2):
        vline(ax, k, 10.15, sub4b_y + 0.2, lw=0.4)
        box(ax, k, sub4b_y, kw4_2[i], 1.6, 0.6, fs=5.5, lw=0.4)
        if i < len(kx4_2) - 1:
            ox = (kx4_2[i] + kx4_2[i+1]) / 2
            ax.text(ox, 10.15 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')

    # ---- "OR" connecting all 4 categories ----
    # Place OR labels between categories on the horizontal line at y=12.35
    ax.text(2.2, 12.25, 'OR', ha='center', va='bottom', fontsize=5.5,
            color='#555555', fontweight='bold')
    ax.text(4.3, 12.25, 'OR', ha='center', va='bottom', fontsize=5.5,
            color='#555555', fontweight='bold')
    ax.text(6.5, 12.25, 'OR', ha='center', va='bottom', fontsize=5.5,
            color='#555555', fontweight='bold')

    # ============================================================
    # DIMENSION 2: Application Domain
    # ============================================================
    dim2_y = 6.0
    box(ax, 2.0, dim2_y, 'Dimension Two : Application Domain', 7.8, 0.55,
        fs=9.5, shade=True, bold=True)
    
    ax.text(4.75, dim2_y - 0.6, 'Connected by "AND" — specifying the research focus area',
            ha='center', va='center', fontsize=7, color='#444444', fontstyle='italic')
    
    # AND connector from Dim1 to Dim2
    # vertical line from bottom of Dim1 area to Dim2
    # Dim1 area ends around y=6.8 (lowest keywords), Dim2 starts at y=6.0
    # Add a vertical line from dim1_y (=13.8) continuous down...
    # Actually let me just place a separate AND indicator
    
    # ===== Connecting Dim1 and Dim2 =====
    # Draw a vertical connector on the left side
    vline(ax, 0.35, 7.5, 6.3, lw=0.8)
    ax.text(0.35, 6.9, 'AND', ha='center', va='center', fontsize=8,
            fontweight='bold', color='black',
            bbox=dict(boxstyle='circle,pad=0.2', facecolor='white', edgecolor='black', lw=0.8))

    # Left side of Dim2: Antiviral
    sub_anti_x, sub_anti_y = 1.3, 4.5
    and_y_d2 = 5.65
    vline(ax, 2.0, dim2_y - 0.275, and_y_d2, lw=0.6)
    hline(ax, and_y_d2, 1.3, 7.3, lw=0.6)
    vline(ax, 1.3, and_y_d2, sub_anti_y + 0.3, lw=0.6)
    vline(ax, 7.3, and_y_d2, 4.8, lw=0.6)
    
    ax.text(4.3, and_y_d2 + 0.1, 'AND', ha='center', va='bottom', fontsize=5.5,
            color='#555555', fontweight='bold')
    
    box(ax, sub_anti_x, sub_anti_y, 'Antiviral\n(antiviral)', 2.2, 0.5,
        fs=7.5, shade=True, bold=False)
    
    kw_anti = ['"antiviral"', '"virucidal"', '"anti-viral"']
    kx_anti = [-0.2, 0.8, 1.8]
    kx_anti_adj = [x + 0.5 for x in kx_anti]
    kw_anti_y = 3.4
    
    vline(ax, sub_anti_x, sub_anti_y - 0.25, 3.75, lw=0.5)
    hline(ax, 3.75, kx_anti_adj[0], kx_anti_adj[-1], lw=0.5)
    for i, k in enumerate(kx_anti_adj):
        vline(ax, k, 3.75, kw_anti_y + 0.2, lw=0.4)
        box(ax, k, kw_anti_y, kw_anti[i], 1.1, 0.4, fs=5.5, lw=0.4)
        if i < len(kx_anti_adj) - 1:
            ox = (kx_anti_adj[i] + kx_anti_adj[i+1]) / 2
            ax.text(ox, 3.75 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')

    # Right side of Dim2: Drug Discovery & Development
    sub_drug_x, sub_drug_y = 7.3, 4.5
    # vline already drawn
    
    box(ax, sub_drug_x, sub_drug_y, 'Drug Discovery & Development\n(drug discovery & development)', 3.5, 0.5,
        fs=7.5, shade=True, bold=False)
    
    kw_drug = ['"drug\ndiscovery"', '"drug\ndesign"', '"lead\noptimization"',
               '"vaccine\ndesign"', '"epitope\nprediction"', '"drug\ndevelopment"', '"therapeutic*"']
    kx_drug = [4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2]
    kx_drug_adj = [x - 2.2 for x in kx_drug]  # shift to center around 7.3
    
    kw_drug_y = 3.4
    
    vline(ax, sub_drug_x, sub_drug_y - 0.25, 3.75, lw=0.5)
    hline(ax, 3.75, kx_drug_adj[0], kx_drug_adj[-1], lw=0.5)
    for i, k in enumerate(kx_drug_adj):
        vline(ax, k, 3.75, kw_drug_y + 0.2, lw=0.4)
        box(ax, k, kw_drug_y, kw_drug[i], 1.1, 0.4, fs=5.5, lw=0.4)
        if i < len(kx_drug_adj) - 1:
            ox = (kx_drug_adj[i] + kx_drug_adj[i+1]) / 2
            ax.text(ox, 3.75 + 0.1, 'OR', ha='center', va='bottom',
                    fontsize=4.5, color='#666666')

    # ============================================================
    # OVERALL AND connector between Dimension 1 and 2
    # ============================================================
    # Put an AND box on the left side connecting everything
    # (already done above)

    # ============================================================
    # BOTTOM LEGEND
    # ============================================================
    legend_y = 1.2
    hline(ax, legend_y + 0.6, 1.5, 8.0, lw=0.4)
    
    legend_items = [
        ('OR', 'Links alternative/optional terms within the same category'),
        ('AND', 'Connects different required dimensions/categories'),
    ]
    for i, (op, desc) in enumerate(legend_items):
        x_pos = 2.0 + i * 3.8
        ax.text(x_pos - 0.4, legend_y, op, ha='center', va='center', fontsize=7,
                fontweight='bold', color='black',
                bbox=dict(boxstyle='circle,pad=0.15', facecolor='white', edgecolor='black', lw=0.6))
        ax.text(x_pos + 0.5, legend_y, desc, ha='left', va='center', fontsize=6,
                color='#444444')

    # ---- Footnote ----
    ax.text(4.75, 0.3, 'Figure X. Boolean search strategy for systematic literature retrieval on computational antiviral drug discovery.',
            ha='center', va='center', fontsize=7.5, color='#444444', fontstyle='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.3)
    print(f"Saved to {output_path}")
    plt.close()


if __name__ == '__main__':
    draw_search_strategy('search_strategy.svg')
    draw_search_strategy('search_strategy.pdf')
    draw_search_strategy('search_strategy.png')
    print("Done!")
