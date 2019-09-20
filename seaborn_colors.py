import seaborn as sns

# 50 colors
pal = sns.color_palette('deep', 50)
print(pal.as_hex())

pal2 = sns.color_palette('bright', 20)
print(pal2.as_hex())
