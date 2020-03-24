import json

rank = {}

# pageRank算法
import matplotlib.pyplot as plt
import networkx as nx
file = open('/Users/lww/PycharmProjects/WebSearchingSystem/Spider/pageGraph.json', 'r')
content = file.read()
graph = json.JSONDecoder(strict=False).decode(content)

G = nx.DiGraph()  # 创建有向图
G.add_edges_from(graph)



layout = nx.spring_layout(G)
plt.figure(1)
nx.draw(G, pos=layout, node_color='y')

pr = nx.pagerank(G, alpha=0.85)  # 阻尼因子d代表用户按照跳转链接来上网的概率0.85
# print(pr)

for url, pageRankValue in pr.items():
    rank[url] = pageRankValue

# print(len(pr.items()))

plt.figure(2)
nx.draw(G, pos=layout, node_size=[x * 6000 for x in pr.values()],node_color='m',with_labels=True)
plt.show()
# temp = sorted(rank.items(), key=lambda x: x[1], reverse=True)
# sorted_dict = {}
# for item in temp:
#     sorted_dict.setdefault(item[0], item[1])
#
# for key in sorted_dict.keys():
#     print(key, ':', sorted_dict[key])

# 保存计算出来的PageRank分值
# with open('PageRank.json', 'w') as f:
#     json.dump(sorted_dict, f, ensure_ascii=False)
#     print("保存成功")
#print(temp)