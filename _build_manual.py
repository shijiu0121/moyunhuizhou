# -*- coding: utf-8 -*-
"""生成《墨蕴徽州——徽文化数字文创智造平台》产品说明书（初稿，Word 可编辑版）。

排版对齐去年《水影·知微》产品说明书：
- 封面：华文行楷42pt主标题 / 楷体15pt副标题 / 黑体24pt"产品说明书"
- 一级标题（总体介绍、（二）…）宋体14pt加粗；二级标题宋体12pt加粗
- 正文宋体小四(12pt)、1.5倍行距、首行缩进2字符
- 图注/表题：仿宋五号(10.5pt)居中（图注在图下方、表题在表上方）
- 表格统一三线表（上粗1.5pt、栏目线0.75pt、下粗1.5pt，无竖线），单元格宋体小五(9pt)
- 公式用 Word 原生公式对象（OMML），居中、右对齐编号
- 图片位置用虚线占位框标出（不生成图片）
- 页脚居中页码，首页无页码
- 遵守双盲评审：全文不出现院校/指导教师/单位名称
"""
import docx
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml

NS_M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

OUT = r'C:\Users\30915\Desktop\mojyun-huizhou\墨蕴徽州产品说明书.docx'

doc = Document()

# ------------------------------------------------------------------ 页面设置
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)
sec.left_margin = Cm(3.175)
sec.right_margin = Cm(3.175)
sec.header_distance = Cm(1.5)
sec.footer_distance = Cm(1.75)
sec.different_first_page_header_footer = True

# docGrid（与去年一致；先移除模板自带的 docGrid 避免重复）
sectPr = sec._sectPr
for el in sectPr.findall(qn('w:docGrid')):
    sectPr.remove(el)
dg = OxmlElement('w:docGrid')
dg.set(qn('w:type'), 'lines')
dg.set(qn('w:linePitch'), '312')
sectPr.append(dg)

# ---------------------------------------------------------------- Normal 样式
normal = doc.styles['Normal']
normal.font.name = '宋体'
normal.font.size = Pt(12)
rpr = normal.element.get_or_add_rPr()
rf = rpr.get_or_add_rFonts()
rf.set(qn('w:ascii'), '宋体')
rf.set(qn('w:hAnsi'), '宋体')
rf.set(qn('w:eastAsia'), '宋体')


# ------------------------------------------------------------------- 工具函数
def _set_run_font(run, font='宋体', size=12, bold=False, color=None):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.append(rf)
    rf.set(qn('w:ascii'), font)
    rf.set(qn('w:hAnsi'), font)
    rf.set(qn('w:eastAsia'), font)


def add_para(text='', font='宋体', size=12, bold=False, align=None,
             indent_chars=0, line=1.5, before=0, after=0, color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    if line:
        pf.line_spacing = line
    if align is not None:
        pf.alignment = align
    if before:
        pf.space_before = Pt(before)
    if after:
        pf.space_after = Pt(after)
    if indent_chars:
        ind = p._p.get_or_add_pPr().get_or_add_ind()
        ind.set(qn('w:firstLineChars'), str(indent_chars * 100))
        ind.set(qn('w:firstLine'), str(int(indent_chars * 240)))  # 12pt 字 2字符=480 twips
    if text:
        r = p.add_run(text)
        _set_run_font(r, font=font, size=size, bold=bold, color=color)
    return p


def h1(text):
    """一级标题：宋体14pt加粗"""
    return add_para(text, font='宋体', size=14, bold=True, line=1.5, before=12, after=6)


def h2(text):
    """二级标题：宋体12pt加粗"""
    return add_para(text, font='宋体', size=12, bold=True, line=1.5, before=6, after=3)


def body(text):
    """正文：宋体小四、1.5倍行距、首行缩进2字符"""
    return add_para(text, font='宋体', size=12, indent_chars=2, line=1.5)


def caption(text):
    """图注/表题：仿宋五号居中"""
    return add_para(text, font='仿宋', size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0)


def _set_table_borders(tbl, top_sz=12, header_sz=6, bottom_sz=12, dashed=False):
    """三线表：顶线/底线1.5pt，栏目线0.75pt，其余无；dashed 用于占位框。"""
    tblPr = tbl._tbl.tblPr
    for el in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(el)
    borders = OxmlElement('w:tblBorders')
    val = 'dashed' if dashed else 'single'
    color = '999999' if dashed else '000000'
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement('w:' + edge)
        if (edge == 'top' and not dashed) or (edge == 'bottom' and not dashed):
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), str(top_sz if edge == 'top' else bottom_sz))
            el.set(qn('w:color'), '000000')
        elif dashed:
            el.set(qn('w:val'), val)
            el.set(qn('w:sz'), '4')
            el.set(qn('w:color'), color)
        else:
            el.set(qn('w:val'), 'none')
            el.set(qn('w:sz'), '0')
            el.set(qn('w:color'), 'auto')
        el.set(qn('w:space'), '0')
        borders.append(el)
    tblPr.append(borders)
    if not dashed:
        # 表头行底边（栏目线）
        for cell in tbl.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            for el in tcPr.findall(qn('w:tcBorders')):
                tcPr.remove(el)
            tcB = OxmlElement('w:tcBorders')
            bottom = OxmlElement('w:bottom')
            bottom.set(qn('w:val'), 'single')
            bottom.set(qn('w:sz'), str(header_sz))
            bottom.set(qn('w:space'), '0')
            bottom.set(qn('w:color'), '000000')
            tcB.append(bottom)
            tcPr.append(tcB)


def three_line_table(headers, rows, col_widths=None, font_size=9):
    """生成三线表。headers: list[str]; rows: list[list[str]]"""
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    _set_table_borders(t)
    for j, htext in enumerate(headers):
        cell = t.cell(0, j)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(htext)
        _set_run_font(r, font='宋体', size=font_size, bold=True)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j > 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            _set_run_font(r, font='宋体', size=font_size)
    if col_widths:
        for j, w in enumerate(col_widths):
            for i in range(len(t.rows)):
                t.cell(i, j).width = Cm(w)
    return t


def placeholder_box(label):
    """图片占位框：1x1 虚线框，固定高度，居中提示文字。"""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_table_borders(t, dashed=True)
    tr = t.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trH = OxmlElement('w:trHeight')
    trH.set(qn('w:val'), str(int(6.5 * 567)))  # 约 6.5cm
    trH.set(qn('w:hRule'), 'atLeast')
    trPr.append(trH)
    cell = t.cell(0, 0)
    cell.width = Cm(14.0)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(label)
    _set_run_font(r, font='宋体', size=10.5, color=RGBColor(0x88, 0x88, 0x88))
    return t


def add_equation(math_xml, number):
    """插入 Word 原生公式（OMML），居中，右侧编号（1）（2）。"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.5
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    tw = 14.65  # 文本区宽度 cm
    pf.tab_stops.add_tab_stop(Cm(tw / 2), WD_TAB_ALIGNMENT.CENTER)
    pf.tab_stops.add_tab_stop(Cm(tw), WD_TAB_ALIGNMENT.RIGHT)
    r1 = p.add_run('\t')
    _set_run_font(r1, font='宋体', size=12)
    el = parse_xml(math_xml)
    p._p.append(el)
    r2 = p.add_run('\t（%d）' % number)
    _set_run_font(r2, font='宋体', size=12)
    return p


def _mr(t):
    """最小化 m:r 运行：仅含 m:t（Word 自动使用默认数学字体渲染）。"""
    return '<m:r><m:t>%s</m:t></m:r>' % t


def math_loRA():
    """W′ = W₀ + (α/r)·BA"""
    return (
        '<m:oMath xmlns:m="%s" xmlns:w="%s">'
        '<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>'
        '%s'  # =
        '<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>'
        '%s'  # +
        '<m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
        '<m:e><m:f><m:num>%s</m:num><m:den>%s</m:den></m:f></m:e></m:d>'
        '%s'  # BA
        '</m:oMath>'
    ) % (NS_M, NS_W, _mr('W'), _mr('′'), _mr('='), _mr('W'), _mr('0'), _mr('+'),
         _mr('α'), _mr('r'), _mr('BA'))


def math_cosine():
    """sim(q,d) = (q·d)/(‖q‖·‖d‖)"""
    return (
        '<m:oMath xmlns:m="%s" xmlns:w="%s">'
        '%s'  # sim
        '<m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
        '<m:e>%s</m:e></m:d>'
        '%s'  # =
        '<m:f>'
        '<m:num><m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
        '<m:e>%s</m:e></m:d></m:num>'
        '<m:den>%s</m:den>'
        '</m:f>'
        '</m:oMath>'
    ) % (NS_M, NS_W, _mr('sim'), _mr('q,d'), _mr('='), _mr('q·d'), _mr('‖q‖‖d‖'))


def add_page_number_footer():
    footer = sec.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' PAGE '
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'end')
    run._r.append(f1)
    run._r.append(instr)
    run._r.append(f2)
    _set_run_font(run, font='宋体', size=9)


# ================================================================ 封面
for _ in range(4):
    add_para('', line=1.0)
add_para('墨蕴徽州', font='华文行楷', size=42, bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0, after=6)
add_para('——徽文化数字文创智造平台', font='楷体', size=15,
         align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0)
for _ in range(3):
    add_para('', line=1.0)
add_para('产品说明书', font='黑体', size=24, bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, line=1.0)
for _ in range(6):
    add_para('', line=1.0)
# 分页进入正文
p = doc.add_paragraph()
p.add_run().add_break(WD_BREAK.PAGE)

# ================================================================ 总体介绍
h1('总体介绍')

h2('1. 项目背景与问题提出')
body('徽州文化是中华传统文化的重要组成部分，涵盖了徽派建筑、文房四宝、徽商文化、徽剧与黄梅戏、徽州三雕、新安画派、民俗饮食等众多门类，资源底蕴深厚。其中，宏村、西递等皖南古村落被列入世界文化遗产，徽墨、歙砚、徽州三雕等多项技艺列入国家级非物质文化遗产名录。然而，徽文化资源的传播与转化长期面临以下问题：')
body('一是传播形式较为单一。多数文化资源仍以实体场馆展示、图文展览和旅游观光为主，数字化呈现多为静态的图文页面，缺少能够让用户参与其中的互动形式，文化内容难以在年轻群体中形成持续吸引力。')
body('二是文创产品同质化严重。旅游文创市场中的产品大量采用通用模板，缺乏地域文化内核；而带有徽文化元素的个性化设计，从创意到设计稿通常需要专业设计师投入数天时间，定制成本高、周期长，普通用户几乎无法参与。')
body('三是通用人工智能工具对徽文化"水土不服"。近年文生图模型能够根据自然语言描述生成图像，但通用模型缺乏对马头墙、四水归堂、徽墨、三雕等徽文化元素的专门理解，生成结果常出现建筑形态失真、风格混杂等问题；通用对话模型对徽文化知识的回答也缺乏可靠依据，存在编造信息的风险。')
body('上述问题表明，亟需一套面向徽文化的、将文化理解、内容生成与文创转化结合起来的智能化工具，让用户能够低成本地"画出徽州、讲出徽州、造出徽州文创"。')

h2('2. 解决方案概述')
body('本项目研发了一套基于生成式人工智能（AIGC）的徽文化数字文创智造平台，围绕"画徽州、讲徽州、造文创"三个环节提供服务：一是通过自研的徽派风格 LoRA 模型，用户输入一句自然语言描述即可生成具有徽派建筑与水墨山水风格的数字画作；二是通过构建徽文化知识库并采用检索增强生成（RAG）技术，为用户提供有据可查的徽文化问答；三是将生成的画作一键套用明信片、海报、书签等模板，导出可直接打印的高清文创成品。')
body('平台由四个功能模块组成：徽州意象馆（文旅数字大屏）、AI 徽画工坊（徽派风格图像生成）、徽史问答官（徽文化知识问答）、文创印务局（文创成品合成与导出）。四个模块共用一个后端调度中心与图像生成引擎，形成从文化展示、内容生成到实物转化的完整服务链。')

h2('3. 系统架构图')
body('平台采用前后端分离的架构。前端为基于 Vue3 的单页应用，包含四个功能页面与一个文旅数字大屏，负责用户交互与结果展示；后端为基于 FastAPI 的调度中心，向下接驳三个核心服务：图像生成引擎、RAG 知识问答服务和文创合成服务。')
body('图像生成引擎采用可插拔设计，支持三种运行模式：本地模式在本机 GPU 上运行 SDXL 基础模型并叠加自训的徽派 LoRA 权重，可离线出图；远程模式通过 HTTP 调用远程 GPU 服务器上的生图服务；云 API 模式调用云生图平台接口作为备用。三种模式对外暴露统一的生成接口，切换无需修改业务代码。RAG 问答服务在本地完成知识切块、向量化与检索，再调用大模型生成回答。文创合成服务使用图像处理库将生成画作与排版模板合成最终成品。系统架构如图1-1所示。')
placeholder_box('（图片占位：图1-1 系统架构图——请替换为架构示意图或手绘框图）')
caption('图1-1 系统架构图')

h2('4. 产品预期效果')
body('本产品投入应用后，预期在以下几个方面产生明显效果。')
body('在降低创作门槛方面，用户无需具备美术设计基础，仅需用一句话描述画面，即可在数秒至数十秒内得到一幅徽派风格的画作，并可进一步制成明信片、海报等文创成品，使"人人可做徽州文创"成为可能。')
body('在提升文化准确性方面，通过针对徽文化元素专门微调的 LoRA 模型，生成画面的建筑形态与水墨风格更贴合徽文化特征；问答模块的回答均依据本地知识库检索结果生成并标注出处，降低了大模型编造信息的风险。')
body('在提高制作效率方面，从文字描述到文创成品导出的全流程可在分钟级内完成，相比传统人工设计（通常需要数天）效率显著提升，适合景区现场、展会等即时产出场景。')
body('在环境适应性方面，图像生成与知识检索均可在本地运行，即使现场网络不稳定，系统仍能完成主要的生成与问答演示，适合校赛、展会等演示环境。')

h2('5. 应用场景与总结')
body('在文旅景区与博物馆场景中，本产品可作为游客互动体验工具：游客现场输入描述即可生成徽派画作并制成明信片带走，也可通过问答模块了解景点背后的文化故事，提升游览的参与感和文化获得感。')
body('在学校教育与美育场景中，本产品可作为传统文化课程的实践工具，学生通过实际生成画作、提问探究，直观理解徽文化的审美特征与历史脉络，培养对传统文化的兴趣。')
body('在文创电商与企业定制场景中，本产品可快速产出创意样稿，支撑明信片、书签、海报等衍生品的打样与批量定制，缩短文创产品的开发周期。')
body('综上所述，本产品是一套集文化展示、智能生成与文创转化于一体的综合性平台，将"文化资源"转化为"可参与、可生成、可带走"的数字文创服务，为徽文化的保护、传播与活化利用提供了新的技术路径。')

# ================================================================ （二）产品设计
h1('（二）产品设计')
body('本系统围绕徽文化数字文创的核心需求，构建了从文化数据到文创成品的端到端方案。整体设计遵循"一个引擎、一套知识、多种出口"的思路：图像生成引擎与知识库是底层能力，四个功能模块分别承担展示、生成、问答与转化职能。各模块的功能定位与技术选型如表2-1所示。')
caption('表2-1 功能模块与技术选型总览')
three_line_table(
    ['模块', '核心功能', '关键技术'],
    [
        ['徽州意象馆', '文旅数字大屏，文化景点与非遗展示', 'Vue3 + ECharts 地图可视化'],
        ['AI 徽画工坊', '文字描述生成徽派风格画作', 'SDXL 基础模型 + 自训徽派 LoRA'],
        ['徽史问答官', '徽文化知识问答，回答附出处', '本地向量检索（RAG）+ 大模型生成'],
        ['文创印务局', '画作套模板合成文创成品', '图像处理模板排版合成'],
    ],
)
add_para('', line=1.0)

h2('1. 徽州意象馆——文旅数字大屏')
body('徽州意象馆是平台的展示层，面向文旅宣传与展览场景，在一屏之内总览徽州文化圈的整体面貌。大屏以安徽省地图为底，标注了黄山市、宣城市、池州市、安庆市、芜湖市、马鞍山市、六安市、滁州市八个城市的 43 处徽文化景点，景点清单与景区等级均经公开资料核实。景点按性质分为山水自然、徽州古村落、人文古迹与非遗、主题乐园与城市四类，在地图上以不同颜色区分。')
body('大屏同时展示国家级与省级非遗名录（含徽州三雕、徽墨制作技艺、歙砚制作技艺、徽州传统民居营造技艺、万安罗盘制作技艺等）、文化圈城市分布、游客画像、热词与资讯滚动条等看板内容，形成"景点—非遗—城市—数据"的多层次展示结构。')
body('在技术实现上，大屏采用 ECharts 的 registerMap 接口注册安徽省级地理数据，以散点与涟漪动画标注景点位置；整体按 1920×1080 设计，通过自适应缩放方案适配不同分辨率的显示屏。界面遵循徽州美学设计语言：宣纸米白底色、水墨晕染背景、朱砂与鎏金点缀，与平台整体视觉风格保持一致。需要说明的是，大屏中的游客量等统计指标目前为演示口径，正式应用中接入实时数据源。')
placeholder_box('（图片占位：图2-1 徽州意象馆大屏界面——请替换为运行截图）')
caption('图2-1 徽州意象馆大屏界面')

h2('2. AI 徽画工坊——徽派风格图像生成')
body('AI 徽画工坊是平台的核心生成模块。用户输入一句画面描述，选择风格与画幅，即可生成一幅徽派风格的数字画作。模块支持水墨、写实两种风格，1:1、3:4、4:5、9:16、16:9 五种画幅，单张与四宫格两种生成方式，并提供"徽派建筑、山水烟雨、器物文房、民俗人物"四类灵感提示词引导用户描述画面，生成结果自动存入历史记录，可回看与放大。')
body('模块的技术方案包含以下几个部分。')
body('（1）扩散模型与文生图原理。文生图模型属于扩散模型一类，其生成过程可理解为从纯噪声图像出发，在文本描述的引导下逐步去噪，最终还原为与描述相符的图像。模型在训练阶段学习了海量图文对中"文本—图像"的对应关系，因此能够理解自然语言描述并生成对应画面。然而，通用模型对徽文化这类专业领域的知识有限，直接生成的结果在建筑形制、风格韵味上往往不够准确，需要针对性地微调。')
body('（2）LoRA 低秩微调。对大型生成模型进行全量微调需要高昂的算力与存储开销，LoRA（低秩适配）方法提供了一种轻量方案：冻结预训练模型的原始权重，只训练一个低秩的增量矩阵。设预训练权重为 W₀，LoRA 将增量 ΔW 分解为两个低秩矩阵 B 与 A 的乘积，微调后的权重为：')
add_equation(math_loRA(), 1)
body('其中 r 为低秩矩阵的秩，α 为缩放系数。LoRA 的训练参数量远小于全量微调，且训练得到的权重文件体积小、便于分发与叠加，特别适合针对特定画风的定向训练。')
body('（3）自训徽派 LoRA。团队收集了公开授权图库中的徽派建筑、水墨山水等素材，经筛选、清洗与标注后，分别训练了两枚徽派 LoRA 权重：一枚以写实徽州古村落为主（突出马头墙、白墙黛瓦等建筑特征），一枚以水墨风格为主（突出墨韵、留白等绘画特征）。两枚权重可以同时加载并叠加使用。')
body('（4）双 LoRA 叠加与风格控制。模块通过设置两枚 LoRA 的叠加强度（adapter_weights）实现风格连续调节：水墨风格提高水墨权重的叠加强度，写实风格提高建筑权重的叠加强度，平衡风格则两者并重。三种风格的配比参数如表2-2所示。此外，生成过程设置了默认负向提示词，抑制人像、现代室内等与徽派主题不符的元素，提高出图成功率。')
caption('表2-2 双 LoRA 风格配比参数')
three_line_table(
    ['风格', '建筑 LoRA 强度', '水墨 LoRA 强度', '画面效果'],
    [
        ['水墨（ink）', '0.4', '1.2', '墨色浓重、留白较多，偏绘画感'],
        ['写实（photo）', '1.2', '0.4', '马头墙、白墙黛瓦更清晰，偏实景感'],
        ['平衡（balanced）', '1.2', '1.2', '建筑清晰且兼具水墨韵味'],
    ],
)
add_para('', line=1.0)
body('（5）可插拔生图引擎。为应对不同运行环境，生图服务抽象为统一接口，支持三种实现：本地模式（本机或演示机 GPU 运行 SDXL 与 LoRA，可离线生成）、远程模式（通过 HTTP 调用远程 GPU 服务器）、云 API 模式（调用云生图平台，作为备用方案）。通过配置即可切换，保证演示现场无论是否具备 GPU 或网络，都能完成生成演示。')
body('（6）生成稳定性设计。固定随机种子可复现同一描述对应的同一画面，便于前后对比与模板复用；四宫格生成采用排队方式逐格出图，避免显存瞬时压力过大；风格参数预设经过验证，保证现场演示的出图效果稳定。AI 徽画工坊界面如图2-2所示。')
placeholder_box('（图片占位：图2-2 AI 徽画工坊生成界面——请替换为运行截图）')
caption('图2-2 AI 徽画工坊生成界面')

h2('3. 徽史问答官——基于检索增强生成的徽文化问答')
body('徽史问答官是平台的知识问答模块。用户就徽文化提出问题，系统返回有据可查的回答，并在回答中标注所引用的资料来源。模块支持多会话管理，最多保留 20 个历史会话；根据用户问题的关键词自动推荐延伸追问，帮助用户深入了解相关内容。')
body('模块的技术方案包含以下几个部分。')
body('（1）知识库构建。团队整理并录入了徽派建筑、文房四宝、徽商文化、徽剧与黄梅戏、徽州三雕、民俗饮食、新安医学、新安画派等门类的徽文化专题资料六十余篇，来源均为公开可查的权威资料。原始文本按固定长度切块并保留重叠区间，避免上下文断裂，共构建约 900 条检索单元。')
body('（2）文本向量化与语义检索。计算机无法直接比较两段文字的语义，需要先将文本映射为向量（一组数值），使语义相近的文本对应的向量在空间中相互靠近。检索时，将用户问题同样映射为向量，再在知识库中找出与其最相近的若干条资料。这里使用余弦相似度衡量两个向量 q 与 d 的相近程度：')
add_equation(math_cosine(), 2)
body('余弦相似度的取值范围为 0 到 1，取值越接近 1 表示语义越接近。由于检索是在语义层面进行的，用户使用口语化表述（如"为什么叫四水归堂"）也能匹配到包含专业表述（如"天井汇水"）的相关资料。')
body('（3）本地向量化与向量库。大模型厂商的对话接口一般不提供文本向量化接口，因此平台采用本地部署的中文专用向量模型 bge-base-zh-v1.5 完成向量化，该模型体积适中、可用 CPU 运行，无需 GPU；向量库采用 ChromaDB，使用余弦距离组织向量并持久化存储，检索结果可复现。')
body('（4）大模型生成回答。问答流程为先检索后生成：系统检索出与问题最相关的若干条资料（默认 5 条），将其与问题一起组装为提示词，交给大模型（DeepSeek）生成回答。提示词中明确要求模型仅依据提供的资料作答，资料不足时如实说明，并在回答末尾标注用到了哪几条资料，从而保证回答内容可追溯、可核对。徽史问答官界面如图2-3所示。')
placeholder_box('（图片占位：图2-3 徽史问答官对话界面——请替换为运行截图）')
caption('图2-3 徽史问答官对话界面')

h2('4. 文创印务局——文创成品合成与导出')
body('文创印务局是平台的转化出口。用户选定一张已生成的画作，输入标题与副题，即可一键合成明信片、海报或书签等文创成品，并可下载高清 PNG 图片用于打印。模块支持"同一幅画换模板"：由于生成画作由随机种子唯一确定，用户切换模板或修改版式时，系统复用同一画面重新排版，无需重新生成，方便快速比较不同版式的效果。')
body('在技术实现上，文创合成采用"生成画作 + 图像处理排版"的方案：先将画作按比例缩放至模板的图画区域，再叠加标题、副题、装饰元素与落款，最终输出成品图像。排版遵循统一的徽州视觉语言——宣纸米白底色、砚墨字色、朱砂印章、鎏金描边，标题采用楷体类字体并降级处理，保证在不同系统环境下均能正常渲染。三种模板的规格与版式特点如表2-3所示。')
caption('表2-3 文创成品模板规格')
three_line_table(
    ['模板', '画布尺寸', '版式特点'],
    [
        ['明信片', '1240×1720（竖版 3:4）', '顶部图画区，中部标题，底部朱砂印章'],
        ['海报', '1024×1536（竖版 2:3）', '顶部标题与分隔线，中部主图，底部落款'],
        ['书签', '480×1500（竖条）', '顶部朱砂题签，中部图画，底部印章'],
    ],
)
add_para('', line=1.0)
body('文创印务局界面如图2-4所示。')
placeholder_box('（图片占位：图2-4 文创印务局导出界面——请替换为运行截图）')
caption('图2-4 文创印务局导出界面')

# ================================================================ （三）产品创新点
h1('（三）产品创新点')
body('本产品在技术实现、产品形态与工程实践三个层面形成了以下创新点。')
body('第一，自研徽派风格 LoRA 与双模型叠加控制。团队针对徽文化元素专门训练了两枚 LoRA 权重，使生成画面在建筑形制（马头墙、白墙黛瓦、四水归堂）与水墨韵味上明显优于通用文生图模型；同时通过叠加强度配比实现"水墨—写实"风格的连续调节，同一描述即可得到风格不同的多幅作品，这一"可调风格的双 LoRA 叠加"方案是通用绘画工具不具备的能力。')
body('第二，"生图—问答—文创"一体化产品形态。平台将图像生成、知识问答与文创转化打通为一条完整服务链：同一套底层能力，既支持游客现场生成画作，也支持文化讲解问答，还支持将作品直接制成可带走的文创成品。相比单一功能的 AI 绘画工具或文创电商，平台覆盖了文化消费从体验到转化的完整环节。')
body('第三，检索增强的可追溯问答。针对大模型回答不可控、易编造的问题，平台采用"本地知识库检索 + 大模型生成"的 RAG 方案：回答必须依据检索到的资料生成并标注来源，资料不足时如实说明。这一机制使知识问答可信、可核对，适合文化传播类场景对内容准确性的要求。')
body('第四，可插拔生图架构与离线演示能力。生图引擎对上层暴露统一接口，底层支持本地、远程、云 API 三种模式，配置即可切换。本地模式在无网络的条件下仍能完成生成演示，极大增强了产品在展会、课堂等现场环境的可用性，也降低了部署成本。')
body('第五，统一的徽州美学设计语言。平台将宣纸、水墨、朱砂、鎏金等徽州文化符号抽象为一套设计规范，贯穿文旅大屏、生成画作与文创成品，使数字产品与传统文化气质一致，形成可识别的品牌视觉特征。')

# ================================================================ （四）市场分析
h1('（四）市场分析')
body('当前，文化数字化与人工智能技术的结合正处于快速发展期，文旅文创市场对个性化、可参与的数字化产品需求日益增长。本产品面向徽文化传播与文创生产的具体痛点，具有明确的市场定位。')

h2('1. 痛点分析')
body('一是文创产品同质化。旅游文创市场产品趋同，大量使用通用模板与图案，缺乏地域文化辨识度，难以满足游客对"有文化、有特色"纪念品的需求。')
body('二是设计门槛与成本高。将文化元素转化为可用设计稿需要专业设计能力，个性化定制通常价格高、周期长，中小景区与个体商户难以承担，限制了文创产品的多样性。')
body('三是文化传播单向、参与感弱。文博与旅游场景的数字化内容多为静态图文，游客缺乏可参与的互动环节，文化内容难以形成记忆点与传播力。')
body('四是通用 AI 工具难以直接落地。通用文生图模型不懂徽文化元素，生成结果需要大量人工修正；通用问答模型缺乏本地知识依据，回答准确性无法保证。市场上的现成工具均未针对徽文化场景做专门适配。')

h2('2. 竞品对比')
body('本产品与市场上主要替代方案的对比情况如表4-1所示。')
caption('表4-1 竞品对比')
three_line_table(
    ['对比维度', '本系统', '传统文创生产', '通用 AI 绘画平台'],
    [
        ['制作成本', '低：软件即服务，按需生成', '高：设计费与开模打样成本高', '中：需订阅或按次付费，出图后仍需人工修图'],
        ['制作效率', '高：描述到成品分钟级完成', '低：设计到出货以天为单位', '中：出图快，但需反复调试与修图'],
        ['文化内涵与准确性', '强：徽派 LoRA 专训 + 知识库问答有据可查', '取决于设计师水平，质量不稳定', '弱：不了解徽文化元素，易出现元素错乱'],
        ['个性化与可定制', '强：人人可参与，一句话定制', '弱：定制成本高，门槛高', '中：可生成但难落地为实体文创'],
        ['版权与合规', '明确：训练素材为公开授权资料', '依委托约定', '不确定：生成内容的版权与商用边界模糊'],
    ],
    col_widths=[2.6, 4.2, 3.9, 3.9],
)
add_para('', line=1.0)
body('对比可见，本产品在成本、效率、文化准确性、可定制性与合规性五个维度上均具备差异化优势：相比传统文创生产，大幅降低门槛与周期；相比通用 AI 绘画平台，具备针对徽文化的专门能力与从画作到成品的完整转化链路，填补了"AI 生成 + 地域文化 + 文创落地"这一细分市场空白。')

h2('3. 应用示范设想')
body('在文旅景区与博物馆，可部署"AI 徽州文创体验点"：游客现场生成画作并制成明信片、书签等纪念品，问答模块同步提供文化讲解，形成"生成—了解—带走"的完整体验，增强景区互动性与二次传播。')
body('在校园与研学场景，可作为传统文化课程的教学工具：学生通过实际操作理解 AI 生成原理与徽文化内涵，平台同时为非遗技艺、建筑形制等教学内容提供可视化素材与互动问答。')
body('在文创电商与企业定制场景，可用于快速打样与批量生产：运营方输入主题描述即可批量生成系列化样稿，经筛选后进入定制生产，显著压缩文创产品从创意到上市的时间。')

h2('4. 商业模式与推广渠道')
body('本产品拟采用"基础服务 + 增值服务"相结合的商业模式：基础层面提供在线生成与问答功能，面向个人用户免费或低价开放，培养使用习惯；增值层面提供高清无水印导出、批量生成、模板定制与私有化部署等服务，面向景区、学校与企业收费。')
body('推广渠道方面，重点与文旅景区、博物馆等文化机构合作，以体验点形式落地并形成示范案例；与高校传统文化课程、创新创业教育机构合作进入教学场景；与文创电商平台合作提供生成能力与定制服务，逐步建立品牌认知与市场覆盖。')

# ================================================================ （五）团队介绍
h1('（五）团队介绍')
body('团队由两名成员组成，均为在校学生，具备完整的全栈开发能力，分工覆盖了平台从模型训练到前后端实现的全部环节。')
body('王昱晗：负责后端服务开发、徽文化知识库与 RAG 问答系统实现、生成模型与徽派 LoRA 的训练调优，以及技术文档撰写。')
body('陈树健：负责前端界面开发，包括四大功能模块与文旅数字大屏的实现与视觉设计，以及产品文档撰写。')

# 页脚页码
add_page_number_footer()

# 首页（封面）页脚留空，与去年一致（封面不显示页码）
fp = sec.first_page_footer
fp.is_linked_to_previous = False
for p in fp.paragraphs:
    p.text = ''

doc.save(OUT)
print('SAVED:', OUT)
