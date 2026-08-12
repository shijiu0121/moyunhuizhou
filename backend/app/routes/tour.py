"""徽州意象馆：文旅大屏数据接口（供前端大屏展示用）。

当前返回示例结构数据，后续替换为真实徽文化/文旅数据。
"""
from fastapi import APIRouter

router = APIRouter(tags=["tour"])

# 示例数据：宏村/西递等景点概览（后续可扩展为从数据文件读取）
SAMPLE_SITES = [
    {"name": "宏村", "city": "黄山·黟县", "desc": "徽派古村落，'中国画里乡村'", "visitors": 1200000},
    {"name": "西递", "city": "黄山·黟县", "desc": "世界文化遗产，徽商故里", "visitors": 980000},
    {"name": "屯溪老街", "city": "黄山·屯溪", "desc": "徽文化活化石，宋街", "visitors": 760000},
    {"name": "棠樾牌坊群", "city": "黄山·歙县", "desc": "明清牌坊建筑群", "visitors": 450000},
    {"name": "呈坎", "city": "黄山·徽州区", "desc": "江南第一村，八卦村", "visitors": 520000},
]

CATEGORIES = [
    {"name": "徽派建筑", "count": 9650, "desc": "马头墙·白墙黛瓦·四水归堂"},
    {"name": "文房四宝", "count": 4, "desc": "宣纸·徽墨·歙砚·宣笔"},
    {"name": "徽商", "count": 12, "desc": "贾而好儒·诚信经营"},
    {"name": "徽剧黄梅戏", "count": 8, "desc": "国家级非遗"},
    {"name": "徽州三雕", "count": 3, "desc": "木雕·砖雕·石雕"},
]


@router.get("/tour/overview")
async def tour_overview():
    """大屏总览数据。"""
    return {"sites": SAMPLE_SITES, "categories": CATEGORIES}
