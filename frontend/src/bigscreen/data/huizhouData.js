// =====================================================================
// 徽州文旅数据（前端演示用）
// ---------------------------------------------------------------------
// 【数据口径说明 —— 请务必阅读】
// 1. 景点清单/等级：2026-08 通过公开网络检索（政府文旅官网/百科/旅游平台）整理核实。
// 2. 经纬度：为人工核对的近似值（精确到小数点后两位，供地图展示定位，非测量级精度）。
// 3. 游客量 value / 底部指标 / 热词 / 非遗名录：均为【示例演示数据】，不代表真实统计。
// 4. 正式比赛口径：数据采集阶段将逐条核对并接入后端 API 实时数据。
// 完整来源留档见 docs/数据来源清单.md
// =====================================================================

// ---------------- 景点类别（用于地图彩点配色） ----------------
// nature=山水自然(青绿)  village=徽州古村落(朱砂)  culture=人文古迹/非遗(鎏金)  leisure=主题乐园/城市(桥木褐)
export const CATEGORY_COLORS = {
  nature: '#3e7d68',
  village: '#a03a2e',
  culture: '#b08a4a',
  leisure: '#6a4735',
}

// ---------------- 徽州文化圈 8 市（地图暖色圈定） ----------------
export const HUIZHOU_CIRCLE_CITIES = [
  '黄山市', '宣城市', '池州市', '安庆市',
  '芜湖市', '马鞍山市', '六安市', '滁州市',
]

// ---------------- 景点数据（43 处，按市分类） ----------------
// lng/lat 为近似经纬度；value 为示例游客量（万人次/年）；level 为景区等级或属性
export const CULTURE_SITES = [
  // ===== 黄山市（徽州核心） =====
  { name: '黄山风景区', city: '黄山市', county: '黄山区', lat: 30.12, lng: 118.16, value: 320, level: '5A', cat: 'nature', desc: '天下第一奇山 · 世界自然与文化双遗产' },
  { name: '宏村', city: '黄山市', county: '黟县', lat: 30.00, lng: 117.99, value: 185, level: '5A·世遗', cat: 'village', desc: '画里乡村 · 世界文化遗产' },
  { name: '西递', city: '黄山市', county: '黟县', lat: 29.91, lng: 117.96, value: 152, level: '5A·世遗', cat: 'village', desc: '明清民居博物馆 · 世界文化遗产' },
  { name: '徽州古城', city: '黄山市', county: '歙县', lat: 29.87, lng: 118.42, value: 96, level: '5A', cat: 'culture', desc: '中国四大古城之一 · 渔梁坝在侧' },
  { name: '屯溪老街', city: '黄山市', county: '屯溪区', lat: 29.71, lng: 118.34, value: 128, level: '4A', cat: 'culture', desc: '流动的清明上河图 · 徽商发源地' },
  { name: '呈坎', city: '黄山市', county: '徽州区', lat: 29.86, lng: 118.26, value: 74, level: '5A', cat: 'village', desc: '中国风水第一村 · 太极八卦布局' },
  { name: '棠樾牌坊群·鲍家花园', city: '黄山市', county: '歙县', lat: 29.89, lng: 118.43, value: 58, level: '5A', cat: 'culture', desc: '徽州牌坊文化的集中代表' },
  { name: '齐云山', city: '黄山市', county: '休宁县', lat: 29.80, lng: 118.05, value: 39, level: '4A', cat: 'nature', desc: '江南第一仙都 · 中国四大道教名山' },

  // ===== 宣城市 =====
  { name: '龙川景区', city: '宣城市', county: '绩溪县', lat: 30.07, lng: 118.60, value: 61, level: '5A', cat: 'village', desc: '胡氏宗祠被誉为「江南第一祠」' },
  { name: '敬亭山', city: '宣城市', county: '宣州区', lat: 30.97, lng: 118.75, value: 42, level: '4A', cat: 'nature', desc: '江南诗山 · 相看两不厌唯有敬亭山' },
  { name: '桃花潭', city: '宣城市', county: '泾县', lat: 30.48, lng: 118.36, value: 46, level: '4A', cat: 'culture', desc: '桃花潭水深千尺 · 不及汪伦送我情' },
  { name: '查济古镇', city: '宣城市', county: '泾县', lat: 30.43, lng: 118.36, value: 38, level: '4A', cat: 'village', desc: '中华写生第一村 · 现存最大明清古村' },
  { name: '徽杭古道', city: '宣城市', county: '绩溪县', lat: 30.30, lng: 118.75, value: 30, level: '4A', cat: 'nature', desc: '中国第一古道 · 徽商走出去的路' },

  // ===== 池州市 =====
  { name: '九华山', city: '池州市', county: '青阳县', lat: 30.48, lng: 117.78, value: 210, level: '5A', cat: 'nature', desc: '中国四大佛教名山 · 地藏菩萨道场' },
  { name: '杏花村', city: '池州市', county: '贵池区', lat: 30.66, lng: 117.48, value: 33, level: '4A', cat: 'culture', desc: '牧童遥指杏花村 · 1300 年诗村' },
  { name: '升金湖', city: '池州市', county: '东至县', lat: 30.35, lng: 116.98, value: 15, level: '国家级保护区', cat: 'nature', desc: '中国鹤湖 · 珍稀水禽天堂' },
  { name: '牯牛降', city: '池州市', county: '石台县', lat: 30.02, lng: 117.47, value: 27, level: '4A', cat: 'nature', desc: '华东最后一片原始森林' },
  { name: '大王洞', city: '池州市', county: '贵池区', lat: 30.55, lng: 117.45, value: 18, level: '4A', cat: 'nature', desc: '华东第一洞 · 喀斯特溶洞奇观' },

  // ===== 安庆市 =====
  { name: '天柱山', city: '安庆市', county: '潜山市', lat: 30.72, lng: 116.45, value: 88, level: '5A', cat: 'nature', desc: '古南岳 · 奇峰怪石云海幽洞' },
  { name: '迎江寺·振风塔', city: '安庆市', county: '迎江区', lat: 30.51, lng: 117.06, value: 20, level: '国家级文保', cat: 'culture', desc: '万里长江第一塔' },
  { name: '花亭湖', city: '安庆市', county: '太湖县', lat: 30.42, lng: 116.33, value: 24, level: '4A', cat: 'nature', desc: '大别山南麓 · 千岛之湖' },
  { name: '小孤山', city: '安庆市', county: '宿松县', lat: 29.98, lng: 116.35, value: 11, level: '省级名胜', cat: 'nature', desc: '长江绝岛 · 江上小蓬莱' },
  { name: '菱湖风景区', city: '安庆市', county: '迎江区', lat: 30.53, lng: 117.05, value: 16, level: '4A', cat: 'leisure', desc: '安庆城市绿心' },

  // ===== 芜湖市 =====
  { name: '方特旅游区', city: '芜湖市', county: '鸠江区', lat: 31.35, lng: 118.43, value: 260, level: '5A', cat: 'leisure', desc: '四大主题园区 · 东方神画' },
  { name: '鸠兹古镇', city: '芜湖市', county: '鸠江区', lat: 31.34, lng: 118.42, value: 44, level: '4A', cat: 'village', desc: '2500 年徽派古镇 · 徽商文化' },
  { name: '马仁奇峰', city: '芜湖市', county: '繁昌区', lat: 31.08, lng: 118.18, value: 36, level: '4A', cat: 'nature', desc: '皖南张家界 · 江滨小黄山' },
  { name: '赭山公园', city: '芜湖市', county: '镜湖区', lat: 31.34, lng: 118.37, value: 30, level: '4A', cat: 'leisure', desc: '赭塔晴岚 · 城市绿洲' },
  { name: '天门山', city: '芜湖市', county: '鸠江区', lat: 31.42, lng: 118.42, value: 12, level: '—', cat: 'nature', desc: '天门中断楚江开 · 李白诗境' },

  // ===== 马鞍山市 =====
  { name: '采石矶', city: '马鞍山市', county: '雨山区', lat: 31.65, lng: 118.50, value: 52, level: '5A', cat: 'nature', desc: '长江三矶 · 诗仙李白捉月处' },
  { name: '褒禅山', city: '马鞍山市', county: '含山县', lat: 31.70, lng: 118.15, value: 22, level: '4A', cat: 'culture', desc: '游褒禅山记 · 华阳洞天' },
  { name: '霸王祠', city: '马鞍山市', county: '和县', lat: 31.75, lng: 118.35, value: 14, level: '3A', cat: 'culture', desc: '西楚霸王项羽祠 · 乌江自刎处' },
  { name: '太湖山', city: '马鞍山市', county: '含山县', lat: 31.60, lng: 118.08, value: 10, level: '4A', cat: 'nature', desc: '江北小九华 · 原始次生林' },
  { name: '李白文化园', city: '马鞍山市', county: '当涂县', lat: 31.55, lng: 118.45, value: 13, level: '4A', cat: 'culture', desc: '诗仙终老长眠之地' },

  // ===== 六安市 =====
  { name: '天堂寨', city: '六安市', county: '金寨县', lat: 31.20, lng: 115.75, value: 96, level: '5A', cat: 'nature', desc: '大别山第二高峰 · 华东原始森林' },
  { name: '万佛湖', city: '六安市', county: '舒城县', lat: 31.30, lng: 116.72, value: 62, level: '5A', cat: 'nature', desc: '安徽千岛湖 · 世界第一人工土石坝' },
  { name: '皖西大裂谷', city: '六安市', county: '金安区', lat: 31.62, lng: 116.48, value: 26, level: '4A', cat: 'nature', desc: '侏罗纪 V 形大裂谷 · 三道闸' },
  { name: '大别山主峰·白马尖', city: '六安市', county: '霍山县', lat: 31.10, lng: 116.25, value: 21, level: '4A', cat: 'nature', desc: '大别山最高峰 · 海拔 1777 米' },
  { name: '燕子河大峡谷', city: '六安市', county: '金寨县', lat: 31.28, lng: 115.90, value: 19, level: '4A', cat: 'nature', desc: '天坑奇观 · 飞瀑流泉' },

  // ===== 滁州市 =====
  { name: '琅琊山·醉翁亭', city: '滁州市', county: '琅琊区', lat: 32.28, lng: 118.31, value: 55, level: '4A', cat: 'culture', desc: '醉翁亭记 · 全国四大名亭之首' },
  { name: '明中都遗址', city: '滁州市', county: '凤阳县', lat: 32.85, lng: 117.56, value: 28, level: '国家考古遗址公园', cat: 'culture', desc: '大明第一座都城 · 故宫之蓝本' },
  { name: '狼巷迷谷', city: '滁州市', county: '凤阳县', lat: 32.80, lng: 117.52, value: 17, level: '4A', cat: 'nature', desc: '天然喀斯特迷宫' },
  { name: '韭山洞', city: '滁州市', county: '凤阳县', lat: 32.82, lng: 117.55, value: 14, level: '4A', cat: 'nature', desc: '江北第一洞 · 五亿年溶洞' },
  { name: '小岗村', city: '滁州市', county: '凤阳县', lat: 32.85, lng: 117.62, value: 31, level: '4A', cat: 'culture', desc: '中国农村改革第一村 · 大包干' },
]

// ---------------- 徽州文化圈外 8 市：简略标注（示例，粗略定位） ----------------
// 有详有略：圈内 8 市做详细景点彩点（上文 CULTURE_SITES），圈外 8 市各标注 1 处文化点位/特产，
// 地图上以淡墨灰点 + 小字呈现，不做游客量等详细数据。
export const OTHER_CITY_SITES = [
  { name: '三河古镇', city: '合肥市', county: '肥西县', lat: 31.52, lng: 117.25, tag: '5A·水乡古镇' },
  { name: '涂山', city: '蚌埠市', county: '禹会区', lat: 32.93, lng: 117.36, tag: '禹会诸侯之地' },
  { name: '寿县古城', city: '淮南市', county: '寿县', lat: 32.57, lng: 116.78, tag: '国家历史文化名城' },
  { name: '临涣古镇', city: '淮北市', county: '濉溪县', lat: 33.70, lng: 116.55, tag: '千年茶镇' },
  { name: '铜官山', city: '铜陵市', county: '铜官区', lat: 30.95, lng: 117.82, tag: '千年铜都' },
  { name: '颍州西湖', city: '阜阳市', county: '颍州区', lat: 32.87, lng: 115.80, tag: '欧公诗境' },
  { name: '皇藏峪', city: '宿州市', county: '萧县', lat: 34.05, lng: 117.05, tag: '国家森林公园' },
  { name: '花戏楼', city: '亳州市', county: '谯城区', lat: 33.87, lng: 115.78, tag: '砖雕艺术国宝' },
]

// ---------------- 目的地游客量排行 TOP8（示例口径，万人次/年） ----------------
export const SITE_RANKING = [
  { label: '黄山风景区', value: 320.5 },
  { label: '方特旅游区', value: 260.0 },
  { label: '九华山', value: 210.0 },
  { label: '宏村', value: 185.0 },
  { label: '西递', value: 152.3 },
  { label: '屯溪老街', value: 128.6 },
  { label: '天堂寨', value: 96.0 },
  { label: '天柱山', value: 88.0 },
]

// ---------------- 游客画像（示例） ----------------
export const VISITOR_AGE = [
  { name: '18-25', value: 38 },
  { name: '26-35', value: 34 },
  { name: '36-50', value: 20 },
  { name: '50+', value: 8 },
]
export const VISITOR_SOURCE = [
  { name: '省内', value: 42 },
  { name: '长三角', value: 36 },
  { name: '京津翼', value: 9 },
  { name: '珠三角', value: 7 },
  { name: '其他', value: 6 },
]

// ---------------- 实时热词（示例） ----------------
export const HOT_WORDS = [
  '马头墙', '四水归堂', '徽墨', '歙砚', '徽商', '文房四宝', '棠樾牌坊',
  '古村落', '徽派建筑', '新安画派', '徽州三雕', '万安罗盘', '黄山毛峰', '徽剧',
]

// ---------------- 徽州非遗名录（示例） ----------------
export const HERITAGE_LIST = [
  { name: '徽剧', level: '国家级', type: '传统戏剧' },
  { name: '徽州三雕（木/石/砖）', level: '国家级', type: '传统美术' },
  { name: '徽墨制作技艺', level: '国家级', type: '传统技艺' },
  { name: '歙砚制作技艺', level: '国家级', type: '传统技艺' },
  { name: '徽州传统民居营造技艺', level: '国家级', type: '传统技艺' },
  { name: '徽派盆景技艺', level: '国家级', type: '传统美术' },
  { name: '徽州漆器髹饰技艺', level: '国家级', type: '传统技艺' },
  { name: '万安罗盘制作技艺', level: '国家级', type: '传统技艺' },
  { name: '徽州竹编', level: '省级', type: '传统美术' },
  { name: '徽州目连戏', level: '国家级', type: '传统戏剧' },
]

// ---------------- 文创品类（示例） ----------------
export const CRAFT_CATEGORIES = [
  { name: '明信片', count: 12 },
  { name: '水墨海报', count: 8 },
  { name: '书签', count: 15 },
  { name: '帆布包', count: 6 },
  { name: '青花茶杯', count: 5 },
  { name: '绢面折扇', count: 4 },
  { name: '丝巾', count: 3 },
  { name: '徽章', count: 10 },
  { name: '卷轴画', count: 7 },
  { name: '屏风摆件', count: 2 },
]

// ---------------- 底部核心指标（示例口径） ----------------
export const FOOTER_STATS = [
  { title: '文旅综合收入', value: 91.2, unit: '亿元', icon: '徽' },
  { title: '年累计访客', value: 560.4, unit: '万人次', icon: '旅' },
  { title: 'AI 作品生成', value: 8.9, unit: '万次', icon: 'AI' },
  { title: '文创衍生品', value: 12.6, unit: '万件', icon: '文' },
]

// ---------------- 头部滚动资讯（示例） ----------------
export const NEWS_TICKER = [
  '宏村、西递于 2000 年列入世界文化遗产，是中国首批古村落类世界遗产',
  '徽州传统民居营造技艺列入国家级非物质文化遗产名录',
  '黄山市打造「创意黄山 · 美在徽州」城市品牌，发力文旅数字文创',
  '徽墨、歙砚并称「文房四宝之宝」，被誉为徽州文化的活化石',
  '徽商足迹遍布全国，「贾而好儒」的儒商文化影响深远',
  '新安画派以「师法自然、格调高雅」著称，是安徽画坛的一面旗帜',
  '徽州文书档案入选《世界记忆亚太地区名录》',
  '皖南国际文化旅游示范区建设加速推进，徽州文旅大屏数据持续更新',
]

// ---------------- 数据声明 ----------------
export const DATA_NOTE = '示例演示数据 · 景点清单及等级经公开资料核实 · 游客量等统计为示例口径，正式数据接入阶段核入'
