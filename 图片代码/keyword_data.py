import networkx as nx
import metaknowledge as mk
import os
import re
from collections import defaultdict, Counter
from itertools import islice
import numpy as np
from tqdm import tqdm


emerging_tech_wos_dict = {
    "Diffusion Models": {
        "sub_techniques": [
            "Denoising Diffusion Probabilistic Models",
            "DDPM",
            "Score-Based Generative Models",
            "SGM",
            "Stochastic Differential Equations",
            "SDE",
            "Latent Diffusion Models",
            "LDM",
            "Diffusion for 3D Molecule Generation",
            "GeoDiff",
            "EDM",
            "DiffDock"
        ],
        "wos_search_terms": [
            "diffusion model",
            "denoising diffusion",
            "score-based model",
            "diffusion probabilistic",
            "latent diffusion",
            "diffusion generative",
            "DiffDock",
            "GeoDiff"
        ]
    },
    "Geometric Deep Learning": {
        "sub_techniques": [
            "Graph Neural Networks",
            "GNN",
            "Equivariant Networks",
            "ENN",
            "Geodesic CNNs",
            "Spectral Networks",
            "SE(3)-Transformers",
            "Tensor Field Networks"
        ],
        "wos_search_terms": [
            "geometric deep learning",
            "geometric learning",
            "3D deep learning",
            "manifold learning",
            "geometric convolution",
            "graph geometry"
        ]
    },
    "Equivariant Networks": {
        "sub_techniques": [
            "SE(3)-Equivariant Networks",
            "E(3)-Equivariant Networks",
            "Equivariant Graph Neural Networks",
            "EGNN",
            "Tensor Field Networks",
            "TFN",
            "Cormorant",
            "Neural Equivariant Interatomic Potentials",
            "NequIP",
            "SchNet"
        ],
        "wos_search_terms": [
            "equivariant network",
            "SE(3)-equivariant",
            "E(3)-equivariant",
            "equivariant graph neural network",
            "EGNN",
            "Tensor Field Network",
            "NequIP",
            "group equivariant"
        ]
    },
    "Graph Neural Networks": {
        "sub_techniques": [
            "Graph Convolutional Networks",
            "GCN",
            "Graph Attention Networks",
            "GAT",
            "GraphSAGE",
            "Message Passing Neural Networks",
            "MPNN",
            "Gated Graph Neural Networks",
            "GGNN",
            "Graph Isomorphism Networks",
            "GIN"
        ],
        "wos_search_terms": [
            "graph neural network",
            "GNN",
            "graph convolutional",
            "GCN",
            "graph attention",
            "message passing neural network",
            "MPNN",
            "graph representation learning"
        ]
    },
    "Graph Attention Networks": {
        "sub_techniques": [
            "GAT",
            "GATv2",
            "Multi-head Attention GAT",
            "Edge-Featured GAT",
            "Heterogeneous GAT",
            "HAN"
        ],
        "wos_search_terms": [
            "graph attention network",
            "GAT",
            "graph attention mechanism",
            "attention-based GNN",
            "multi-head graph attention"
        ]
    },
    "Transformer": {
        "sub_techniques": [
            "BERT",
            "Generative Pre-trained Transformer",
            "GPT",
            "Vision Transformer",
            "ViT",
            "Molecular Transformer",
            "Protein Transformer",
            "ESM",
            "ProtTrans",
            "Performer",
            "Linformer"
        ],
        "wos_search_terms": [
            "transformer model",
            "attention mechanism",
            "self-attention",
            "BERT",
            "GPT",
            "molecular transformer",
            "protein language model"
        ]
    },
    "Multimodal Learning": {
        "sub_techniques": [
            "Multimodal Transformers",
            "Contrastive Language-Image Pretraining",
            "CLIP",
            "Multimodal VAEs",
            "Early Fusion",
            "Late Fusion",
            "Cross-modal Attention"
        ],
        "wos_search_terms": [
            "multimodal learning",
            "multi-modal",
            "cross-modal",
            "multimodal fusion",
            "contrastive language-image",
            "CLIP",
            "multimodal representation"
        ]
    },
    "Protein Language Models": {
        "sub_techniques": [
            "ESM-1b",
            "ESM-2",
            "ESM-3",
            "ProtBERT",
            "ProtTrans",
            "T5-Prot",
            "Ankh",
            "ProGen"
        ],
        "wos_search_terms": [
            "protein language model",
            "protein BERT",
            "ProtBERT",
            "ESM-2",
            "ESMFold",
            "protein transformer",
            "ProtTrans",
            "protein sequence embedding"
        ]
    },
    "Large Language Models": {
        "sub_techniques": [
            "GPT-3",
            "GPT-4",
            "LLaMA",
            "PaLM",
            "Claude",
            "Mixtral",
            "Low-Rank Adaptation",
            "LoRA",
            "QLoRA",
            "Prompt Engineering"
        ],
        "wos_search_terms": [
            "large language model",
            "LLM",
            "GPT-4",
            "ChatGPT",
            "generative pre-trained transformer",
            "foundation model",
            "prompt engineering",
            "instruction tuning"
        ]
    },
    "AI Agent": {
        "sub_techniques": [
            "Autonomous Agent",
            "Multi-Agent System",
            "MAS",
            "ReAct Framework",
            "Tool-Augmented LLMs",
            "LLM-based Planner"
        ],
        "wos_search_terms": [
            "AI agent",
            "intelligent agent",
            "autonomous agent",
            "multi-agent system",
            "LLM agent",
            "ReAct",
            "tool learning",
            "agentic workflow"
        ]
    },
    "Reinforcement Learning": {
        "sub_techniques": [
            "Deep Q-Network",
            "DQN",
            "Policy Gradient",
            "Actor-Critic",
            "A2C",
            "A3C",
            "Proximal Policy Optimization",
            "PPO",
            "Monte Carlo Tree Search",
            "MCTS",
            "REINVENT"
        ],
        "wos_search_terms": [
            "reinforcement learning",
            "deep reinforcement learning",
            "policy gradient",
            "Q-learning",
            "actor-critic",
            "PPO",
            "RL",
            "multi-armed bandit"
        ]
    },
    "Few-Shot Learning": {
        "sub_techniques": [
            "Prototypical Networks",
            "Matching Networks",
            "Model-Agnostic Meta-Learning",
            "MAML",
            "Siamese Networks",
            "Relation Networks"
        ],
        "wos_search_terms": [
            "few-shot learning",
            "low-shot learning",
            "zero-shot learning",
            "prototypical network",
            "matching network",
            "meta-learning"
        ]
    },
    "Meta-Learning": {
        "sub_techniques": [
            "MAML",
            "Reptile",
            "Optimization-based Meta-Learning",
            "Metric-based Meta-Learning",
            "Black-box Meta-Learning"
        ],
        "wos_search_terms": [
            "meta-learning",
            "learning to learn",
            "MAML",
            "model-agnostic meta-learning",
            "few-shot meta-learning"
        ]
    },
    "Federated Learning": {
        "sub_techniques": [
            "Federated Averaging",
            "FedAvg",
            "Differential Privacy Federated Learning",
            "Vertical Federated Learning",
            "Horizontal Federated Learning",
            "Federated Transfer Learning",
            "Secure Aggregation"
        ],
        "wos_search_terms": [
            "federated learning",
            "FL",
            "federated averaging",
            "FedAvg",
            "distributed learning",
            "privacy-preserving machine learning"
        ]
    },
    "Explainable AI": {
        "sub_techniques": [
            "SHapley Additive exPlanations",
            "SHAP",
            "Local Interpretable Model-agnostic Explanations",
            "LIME",
            "Integrated Gradients",
            "Attention Visualization",
            "Gradient-weighted Class Activation Mapping",
            "Grad-CAM",
            "Counterfactual Explanations"
        ],
        "wos_search_terms": [
            "explainable AI",
            "XAI",
            "interpretable machine learning",
            "SHAP",
            "LIME",
            "feature attribution",
            "model interpretability",
            "saliency map"
        ]
    }
}

word = "Diffusion Models, Geometric Deep Learning, Equivariant Networks, Graph Neural Networks, Graph Attention Networks, Transformer, Multimodal Learning, Protein Language Models, Large Language Models, AI Agent, Reinforcement Learning, Few-Shot Learning, Meta-Learning, Federated Learning, Explainable AI"
word = word.split(",")
word = list(map(lambda x:x.strip(),word))  # 保持原始大小写，用于字典查找
word = Counter(word)

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

# 初始化年份统计数据字典：2010-2025年，每个年份一个Counter
year_range = range(2010, 2026)  # 2010到2025（包含2025）
year_stats = {year: Counter() for year in year_range}

# 直接处理每条记录，同时获取年份和摘要
for rec in tqdm(rc):
    # 获取发表年份
    py = rec.get("PY")
    if not py:
        continue  # 如果没有发表年份，跳过
    
    # 处理年份数据，可能是字符串或列表
    if isinstance(py, list):
        py = py[0] if py else ""
    
    try:
        year = int(py)
    except (ValueError, TypeError):
        continue  # 年份格式错误，跳过
    
    # 只统计2010-2025年的记录
    if year < 2010 or year > 2025:
        continue
    
    # 获取摘要
    ab = rec.get("AB")
    if not ab:
        continue
    
    # 将摘要转换为小写以便不区分大小写匹配
    ab_lower = ab.lower()
    
    # 检查该记录匹配哪些技术类别
    matched_categories = set()
    for v in word.keys():
        if v in emerging_tech_wos_dict.keys():
            l = emerging_tech_wos_dict[v]["sub_techniques"]
            # 计算匹配的子技术术语数量
            sub_tech_count = 0
            # 检查子技术术语
            for k in l:
                # 将术语转换为小写进行匹配
                if k.lower() in ab_lower:
                    sub_tech_count += 1
            
            # 只有当至少有两个子技术术语出现在摘要中时，才认为匹配
            if sub_tech_count >= 2:
                matched_categories.add(v)
            
            # 检查wos_search_terms的匹配（只在没有满足子技术条件时检查）
            elif sub_tech_count < 2:
                l = emerging_tech_wos_dict[v]["wos_search_terms"]
                for c in l:
                    # 将搜索词转换为小写进行匹配
                    c_lower = c.lower()
                    if c_lower in ab_lower:
                        # 如果搜索词出现在摘要中，认为匹配
                        matched_categories.add(v)
                        break  # 找到一个匹配就足够
    
    # 为该年份的每个匹配技术类别计数
    for category in matched_categories:
        year_stats[year][category] += 1

# 重新组织数据：以技术类别为key，每个技术类别对应一个年份计数字典
tech_year_stats = {}
year_range_list = list(year_range)  # 转换为列表以便使用

# 初始化所有技术类别的字典
for tech in word.keys():
    tech_year_stats[tech] = {year: 0 for year in year_range_list}

# 填充数据
for year in year_range:
    for tech, count in year_stats[year].items():
        if tech in tech_year_stats:
            tech_year_stats[tech][year] = count

# 创建只包含有数据的技术类别的字典（过滤掉全为0的条目）
filtered_tech_year_stats = {}
total_stats = {}
for tech in tech_year_stats.keys():
    total_count = sum(tech_year_stats[tech].values())
    if total_count > 0:
        filtered_tech_year_stats[tech] = tech_year_stats[tech]
        total_stats[tech] = total_count

# 输出年份统计字典（以技术类别为key）
print("\n=== 年份统计字典（技术类别 -> 年份 -> 计数）===")
# 构建一个干净的字典字符串
year_stats_dict_str = "{"
for i, tech in enumerate(sorted(filtered_tech_year_stats.keys())):
    year_stats_dict_str += f'"{tech}": {filtered_tech_year_stats[tech]}'
    if i < len(filtered_tech_year_stats) - 1:
        year_stats_dict_str += ", "
year_stats_dict_str += "}"
print(year_stats_dict_str)

# 输出总数字典
print("\n=== 总发表数量字典 ===")
total_stats_dict_str = "{"
for i, tech in enumerate(sorted(total_stats.keys())):
    total_stats_dict_str += f'"{tech}": {total_stats[tech]}'
    if i < len(total_stats) - 1:
        total_stats_dict_str += ", "
total_stats_dict_str += "}"
print(total_stats_dict_str)

# 同时输出易于阅读的格式
print("\n=== 各技术类别详细统计 ===")
for tech in sorted(filtered_tech_year_stats.keys()):
    print(f'\n{tech}:')
    print(f'  年份分布: {filtered_tech_year_stats[tech]}')
    print(f'  总数: {total_stats[tech]}')

# 导出CSV文件
import csv

# 导出年份统计CSV（宽格式：每行一个技术类别，每列一个年份，年份从2025到2010递减）
csv_filename = "tech_year_stats.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # 写入表头：技术类别 + 各年份（从2025到2010）+ 总数
    reversed_years = list(reversed(year_range_list))  # 从2025到2010
    header = ["Technology"] + [str(year) for year in reversed_years] + ["Total"]
    writer.writerow(header)
    
    # 写入数据行
    for tech in sorted(filtered_tech_year_stats.keys()):
        row = [tech]
        for year in reversed_years:
            row.append(filtered_tech_year_stats[tech][year])
        row.append(total_stats[tech])
        writer.writerow(row)

print(f"\n=== CSV文件已生成 ===")
print(f"文件名: {csv_filename}")
print(f"行数: {len(filtered_tech_year_stats) + 1} (包含表头)")
print(f"列数: {len(year_range_list) + 2} (技术类别 + {len(year_range_list)}年 + 总数)")

# 导出总数CSV
total_csv_filename = "tech_total_stats.csv"
with open(total_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Technology", "Total_Publications"])
    for tech in sorted(total_stats.keys()):
        writer.writerow([tech, total_stats[tech]])

print(f"总数文件: {total_csv_filename}")




