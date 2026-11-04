"""从问答原文生成阅读网络；共同提及表示文本关联，不推断历史关系。"""
from hashlib import sha256
from itertools import combinations

from .knowledge import load_knowledge_entries

# 展示分类按标题匹配；兜底主题容纳历史人物及尚未归类的新资料。
TOPICS = [
    ("architecture", "建筑聚落", ("建筑", "宅居", "民宅", "牌坊", "祠堂")),
    ("commerce", "徽商往事", ("徽商", "海商")),
    ("stationery", "文房四宝", ("徽墨", "歙砚", "宣纸", "宣笔")),
    ("opera", "梨园声腔", ("徽剧", "徽班", "戏曲", "戏台")),
    ("folk", "民俗风物", ("民俗", "习俗", "徽菜", "茶道", "茶会", "庙会")),
    ("craft", "雕刻盆景", ("雕刻", "砖雕", "盆景", "篆刻")),
    ("scholarship", "书画学术", ("理学", "朴学", "画派", "画坛", "黄宾虹", "碑园")),
    ("medicine", "新安医学", ("医学", "名药", "御医")),
    ("history", "历史人文", ()),
]

# 只做显式词语匹配，不把年代、通用地名等高频词当成关联证据。
KEYWORDS = (
    "徽商", "贾而好儒", "盐商", "胡雪岩", "马头墙", "天井", "祠堂", "牌坊",
    "宏村", "西递", "潜口", "三雕", "木雕", "砖雕", "石雕", "徽墨", "歙砚",
    "宣纸", "宣笔", "徽剧", "徽班", "京剧", "目连戏", "徽菜", "茶道", "庙会",
    "朱熹", "新安理学", "朴学", "戴震", "新安画派", "黄宾虹", "渐江", "篆刻",
    "徽派版画", "徽派盆景", "梅花", "新安医学", "汪机", "程灵洗",
)


def build_knowledge_graph() -> dict:
    articles = []
    for entry in load_knowledge_entries():
        topic = next((key for key, _, words in TOPICS if any(word in entry["title"] for word in words)), "history")
        articles.append({
            "id": "article-" + sha256(entry["source"].encode("utf-8")).hexdigest()[:16],
            "name": entry["title"],
            "kind": "article",
            "topic": topic,
            "source": entry["source"],
            "text": entry["text"],
            "keywords": [word for word in KEYWORDS if word in entry["text"]],
        })

    topics = [
        {"id": key, "name": name, "count": sum(a["topic"] == key for a in articles)}
        for key, name, _ in TOPICS
    ]
    topics = [topic for topic in topics if topic["count"]]
    nodes = [{"id": "huizhou", "name": "徽州文脉", "kind": "root"}] if articles else []
    links = []
    for topic in topics:
        nodes.append({"id": "topic-" + topic["id"], "name": topic["name"], "kind": "topic", "topic": topic["id"]})
        links.append({"source": "huizhou", "target": "topic-" + topic["id"], "kind": "topic"})
    nodes.extend(articles)
    for article in articles:
        links.append({"source": "topic-" + article["topic"], "target": article["id"], "kind": "contains"})

    # 以共享词的 Jaccard 比例排序，优先保留紧密关联；每篇至多两条共现边。
    candidates = []
    for left, right in combinations(articles, 2):
        left_words, right_words = set(left["keywords"]), set(right["keywords"])
        shared = left_words & right_words
        if len(shared) >= 2:
            score = len(shared) / len(left_words | right_words)
            candidates.append((score, len(shared), left["id"], right["id"], sorted(shared)))
    degree = {a["id"]: 0 for a in articles}
    for _, _, source, target, words in sorted(candidates, reverse=True):
        if degree[source] < 2 and degree[target] < 2:
            links.append({"source": source, "target": target, "kind": "related", "keywords": words})
            degree[source] += 1
            degree[target] += 1

    return {
        "nodes": nodes,
        "links": links,
        "topics": topics,
        "stats": {
            "articles": len(articles),
            "topics": len(topics),
            "relations": sum(link["kind"] == "related" for link in links),
        },
    }
