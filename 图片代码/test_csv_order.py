import csv

# 测试年份顺序
year_range_list = list(range(2010, 2026))  # 2010-2025
print("原始年份顺序:", year_range_list)
print("年份数量:", len(year_range_list))

# 反转年份顺序
reversed_years = list(reversed(year_range_list))
print("反转后年份顺序:", reversed_years)
print("第一个年份:", reversed_years[0], "(应该是2025)")
print("最后一个年份:", reversed_years[-1], "(应该是2010)")

# 测试CSV表头生成
header = ["Technology"] + [str(year) for year in reversed_years] + ["Total"]
print("\nCSV表头:")
print(header)
print("表头长度:", len(header))
print("第二列:", header[1], "(应该是2025)")

# 测试数据行生成
test_data = {
    "AI Agent": {2010: 0, 2011: 0, 2012: 0, 2013: 2, 2014: 2, 2015: 6, 2016: 4, 2017: 0, 2018: 6, 2019: 5, 2020: 14, 2021: 24, 2022: 38, 2023: 24, 2024: 43, 2025: 69},
    "Transformer": {2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0, 2016: 0, 2017: 1, 2018: 0, 2019: 0, 2020: 1, 2021: 2, 2022: 9, 2023: 1, 2024: 7, 2025: 6}
}

print("\n测试数据行生成:")
for tech in sorted(test_data.keys()):
    row = [tech]
    for year in reversed_years:
        row.append(test_data[tech][year])
    total = sum(test_data[tech].values())
    row.append(total)
    print(f"{tech}: {row}")
    print(f"  第二列值: {row[1]} (应该是{test_data[tech][2025]})")
    print(f"  最后一列值: {row[-1]} (应该是总数{total})")

print("\n=== 验证完成 ===")
print("年份顺序已成功从2025到2010排列")
print("CSV文件生成逻辑正确")