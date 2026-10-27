"""Generate the printable, A4 lesson pack from the same map and content as the site.

Run from anywhere: python scripts/generate_pdfs.py
Dependencies: reportlab, svglib, pypdf. The public Noto font and map live in docs/assets.
"""
from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF, shapes
from svglib.svglib import svg2rlg


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs' / 'assets'
OUTPUT = ASSETS / 'pdf'
DATA_PATH = ASSETS / 'lesson.json'
MAP_PATH = ASSETS / 'neighborhood-map.svg'
FONT_PATH = ASSETS / 'fonts' / 'NotoSansKR.ttf'
FONT = 'NotoSansKR'
WIDTH, HEIGHT = A4
MARGIN = 43
INNER = WIDTH - 2 * MARGIN
INK = colors.HexColor('#183D47')
MUTED = colors.HexColor('#506971')
MINT = colors.HexColor('#DFF4EA')
GREEN = colors.HexColor('#1A715D')
YELLOW = colors.HexColor('#FCE9A8')
CREAM = colors.HexColor('#FFF9E8')
LINE = colors.HexColor('#A8BEB6')


def font(size):
    return (FONT, size)


def txt(c, x, y, s, size=12, color=INK):
    c.setFillColor(color)
    c.setFont(*font(size))
    c.drawString(x, y, str(s))


def center(c, x, y, s, size=12, color=INK):
    c.setFillColor(color)
    c.setFont(*font(size))
    c.drawCentredString(x, y, str(s))


def para(c, x, y, text, width, size=11, leading=17, color=INK):
    """Draw text with deterministic width wrapping; return next baseline."""
    for part in text.split('\n'):
        if not part:
            y -= leading
            continue
        line = ''
        for word in part.split(' '):
            candidate = f'{line} {word}'.strip()
            if line and pdfmetrics.stringWidth(candidate, FONT, size) > width:
                txt(c, x, y, line, size, color)
                y -= leading
                line = word
            else:
                line = candidate
        if line:
            txt(c, x, y, line, size, color)
            y -= leading
    return y


def rounded(c, x, y, w, h, fill, stroke=None, radius=12):
    c.setLineWidth(.8)
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=bool(stroke))


def line(c, x1, y1, x2, y2, color=LINE, width=.8):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def section(c, y, number, title, tag=None):
    rounded(c, MARGIN, y - 3, 25, 25, GREEN, radius=8)
    center(c, MARGIN + 12.5, y + 4, number, 10, colors.white)
    txt(c, MARGIN + 35, y + 3, title, 15)
    if tag:
        c.setFont(*font(9))
        w = pdfmetrics.stringWidth(tag, FONT, 9) + 16
        rounded(c, WIDTH - MARGIN - w, y, w, 18, YELLOW, radius=9)
        center(c, WIDTH - MARGIN - w / 2, y + 5, tag, 9)
    return y - 27


def header(c, kind, title, page, subtitle=''):
    c.setTitle(f'우리 동네 탐험대 | {kind}')
    c.setAuthor('우리 동네 탐험대 수업 자료')
    rounded(c, MARGIN, HEIGHT - 69, 108, 22, MINT, radius=11)
    center(c, MARGIN + 54, HEIGHT - 62, kind, 10, GREEN)
    txt(c, MARGIN, HEIGHT - 107, title, 23)
    if subtitle:
        txt(c, MARGIN, HEIGHT - 129, subtitle, 10.5, MUTED)
    line(c, MARGIN, HEIGHT - 143, WIDTH - MARGIN, HEIGHT - 143)


def footer(c, page):
    line(c, MARGIN, 47, WIDTH - MARGIN, 47)
    txt(c, MARGIN, 34, '전주교육대학교전주부설초등학교  |  4학년 사회  |  우리 동네 탐험대', 8.5, MUTED)
    c.setFont(*font(8.5))
    c.setFillColor(MUTED)
    c.drawRightString(WIDTH - MARGIN, 34, str(page))


def legend_symbol(c, x, y, category, size=16):
    """The same flag/book/house glyphs used on the shared map."""
    c.setStrokeColor(INK)
    c.setFillColor(colors.white)
    c.setLineWidth(1)
    c.circle(x + size / 2, y + size / 2, size / 2, stroke=1, fill=1)
    if category == 'school':
        c.line(x + size * .38, y + size * .22, x + size * .38, y + size * .78)
        p = c.beginPath()
        p.moveTo(x + size * .38, y + size * .77)
        p.lineTo(x + size * .72, y + size * .65)
        p.lineTo(x + size * .38, y + size * .53)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
    elif category == 'library':
        c.line(x + size * .5, y + size * .25, x + size * .5, y + size * .7)
        c.line(x + size * .25, y + size * .32, x + size * .25, y + size * .7)
        c.line(x + size * .75, y + size * .32, x + size * .75, y + size * .7)
        c.line(x + size * .25, y + size * .7, x + size * .5, y + size * .62)
        c.line(x + size * .75, y + size * .7, x + size * .5, y + size * .62)
        c.line(x + size * .25, y + size * .32, x + size * .5, y + size * .25)
        c.line(x + size * .75, y + size * .32, x + size * .5, y + size * .25)
    else:
        p = c.beginPath()
        p.moveTo(x + size * .22, y + size * .48)
        p.lineTo(x + size * .5, y + size * .75)
        p.lineTo(x + size * .78, y + size * .48)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.rect(x + size * .29, y + size * .24, size * .42, size * .25, stroke=1, fill=0)
        c.line(x + size * .5, y + size * .24, x + size * .5, y + size * .38)


def compass(c, cx, cy, size=85, answers=True):
    c.saveState()
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.circle(cx, cy, size * .32, stroke=1, fill=0)
    c.line(cx, cy - size * .6, cx, cy + size * .6)
    c.line(cx - size * .6, cy, cx + size * .6, cy)
    for dx, dy, angle in [(0, .6, 90), (.6, 0, 0), (0, -.6, -90), (-.6, 0, 180)]:
        import math
        a = math.radians(angle)
        x, y = cx + dx * size, cy + dy * size
        for sign in [-1, 1]:
            b = a + sign * .58
            c.line(x, y, x - 9 * math.cos(b), y - 9 * math.sin(b))
    rounded(c, cx - 15, cy - 8, 30, 16, colors.white, radius=5)
    center(c, cx, cy - 3, '기준', 8, GREEN)
    for dx, dy, label in [(0,.76,'북'),(.80,0,'동'),(0,-.82,'남'),(-.80,0,'서')]:
        x, y = cx + dx * size, cy + dy * size
        if answers:
            center(c, x, y - 4, label, 14)
        else:
            rounded(c, x - 17, y - 11, 34, 22, colors.white, LINE, 5)
            if label == '북':
                center(c, x, y - 4, label, 11, GREEN)
    c.restoreState()


def draw_map(c, x, y, max_w, max_h):
    drawing = svg2rlg(str(MAP_PATH))
    if drawing is None or not drawing.width or not drawing.height:
        raise ValueError(f'Could not render SVG map: {MAP_PATH}')
    # svglib resolves SVG font-family before it knows our registered TTF and
    # otherwise silently substitutes Helvetica, which cannot render Korean.
    def use_shared_font(node):
        if isinstance(node, shapes.String):
            node.fontName = FONT
        for child in getattr(node, 'contents', []):
            use_shared_font(child)
    use_shared_font(drawing)
    scale = min(max_w / drawing.width, max_h / drawing.height)
    c.saveState()
    c.translate(x + (max_w - drawing.width * scale) / 2,
                y + (max_h - drawing.height * scale) / 2)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()


def sources(c, y):
    txt(c, MARGIN + 2, y, '위치 자료: 학교 공식 위치 안내 · 공공데이터포털 · OpenStreetMap', 8.5, MUTED)
    txt(c, MARGIN + 2, y - 13, 'school.jbedu.kr/jjbs/M010208/index.do', 8, MUTED)
    txt(c, MARGIN + 2, y - 26, 'data.go.kr/data/15034533/standard.do', 8, MUTED)
    txt(c, MARGIN + 2, y - 39, '© OpenStreetMap contributors  |  openstreetmap.org/copyright', 8, MUTED)
    c.linkURL('https://school.jbedu.kr/jjbs/M010208/index.do', (MARGIN, y - 15, 300, y - 4), relative=0)
    c.linkURL('https://www.data.go.kr/data/15034533/standard.do', (MARGIN, y - 28, 300, y - 17), relative=0)
    c.linkURL('https://www.openstreetmap.org/copyright', (MARGIN, y - 42, 360, y - 30), relative=0)


def learning(c, data):
    header(c, '학생 학습자료', '지도와 친해지는 시간', 1, '우리 동네 탐험대  ·  방위와 기호로 동네를 읽어요')
    y = HEIGHT - 175
    rounded(c, MARGIN, y - 72, INNER, 75, CREAM)
    txt(c, MARGIN + 17, y - 20, '오늘의 탐험 목표', 13, GREEN)
    para(c, MARGIN + 17, y - 43, '방위표와 범례를 이용하여 우리 동네 지도에서 장소를 찾고 위치를 설명할 수 있어요.', INNER - 34, 12, 17)
    y -= 112
    y = section(c, y, '01', '방위: 어디에 있을까요?')
    compass(c, MARGIN + 100, y - 98, 82, True)
    txt(c, MARGIN + 208, y - 30, '북쪽을 먼저 찾아요.', 13, GREEN)
    para(c, MARGIN + 208, y - 55, '방위표에서 북쪽은 위, 남쪽은 아래, 동쪽은 오른쪽, 서쪽은 왼쪽이에요.', 270, 11, 18)
    para(c, MARGIN + 208, y - 113, '장소의 위치를 말할 때는 어디를 기준으로 하는지도 함께 말해요.', 270, 11, 18)
    y -= 202
    y = section(c, y, '02', '기호와 범례: 그림의 뜻을 찾아요')
    para(c, MARGIN + 1, y - 1, '기호는 장소를 간단하게 나타낸 그림이고, 범례는 그 기호의 뜻을 모아 놓은 약속이에요.', INNER - 5, 11, 18)
    rounded(c, MARGIN, y - 91, INNER, 53, MINT)
    for x, category, label in [(MARGIN + 20, 'school', '학교'), (MARGIN + 175, 'library', '도서관'), (MARGIN + 325, 'community', '주민센터')]:
        legend_symbol(c, x, y - 74, category)
        txt(c, x + 25, y - 71, label, 12)
    txt(c, MARGIN + 2, y - 117, '※ 이 자료에서 약속한 기호예요. 다른 지도에서는 범례를 다시 확인해요.', 9.5, MUTED)
    footer(c, 1)
    c.showPage()

    header(c, '학생 학습자료', '우리 동네 지도', 2, '학교 주변의 실제 위치를 살펴보는 탐험 지도')
    txt(c, MARGIN, HEIGHT - 171, '먼저 방위표와 범례를 보고 학교를 찾아보세요.', 12, GREEN)
    draw_map(c, MARGIN, HEIGHT - 556, INNER, 365)
    para(c, MARGIN, HEIGHT - 577, '이 지도는 실제 학교 주변을 단순하게 나타낸 학습용 지도예요. 정확한 거리와 길찾기에는 사용하지 않아요.', INNER, 10, 15, MUTED)
    rounded(c, MARGIN, HEIGHT - 662, INNER, 52, CREAM)
    txt(c, MARGIN + 15, HEIGHT - 630, '탐험 질문', 11, GREEN)
    txt(c, MARGIN + 15, HEIGHT - 649, '우리 학교를 기준으로 도서관은 어느 쪽에 있을까요?', 11)
    sources(c, 112)
    footer(c, 2)
    c.showPage()


def worksheet(c, data):
    header(c, '학생 활동지', '나도 지도 탐험가!', 1, '생각을 쓰고, 짝과 이야기를 나누어요')
    txt(c, MARGIN, HEIGHT - 170, '날짜:                       반:                  이름:', 11, MUTED)
    y = HEIGHT - 206
    y = section(c, y, '01', '방위표를 완성해요')
    txt(c, MARGIN, y - 8, '북쪽을 기준으로 빈칸에 동, 서, 남을 알맞게 써 보세요.', 11)
    compass(c, WIDTH / 2, y - 110, 83, False)
    line(c, MARGIN, y - 205, WIDTH - MARGIN, y - 205)
    y -= 236
    y = section(c, y, '02', '기호와 뜻을 이어요')
    txt(c, MARGIN, y - 8, '각 기호를 보고 알맞은 뜻과 선으로 이어 보세요.', 11)
    ys = [y - 56, y - 100, y - 144]
    for pos, category, n in zip(ys, ['school', 'library', 'community'], ['가', '나', '다']):
        txt(c, MARGIN + 17, pos, n, 11)
        legend_symbol(c, MARGIN + 47, pos - 3, category)
        c.circle(MARGIN + 116, pos + 4, 2, stroke=1, fill=0)
    for pos, word in zip(ys, ['주민센터', '학교', '도서관']):
        c.circle(WIDTH - MARGIN - 183, pos + 4, 2, stroke=1, fill=0)
        txt(c, WIDTH - MARGIN - 165, pos, word, 11)
    rounded(c, MARGIN, 85, INNER, 38, CREAM)
    txt(c, MARGIN + 14, 99, '힌트: 학습자료의 범례를 살펴보세요.', 10.5, GREEN)
    footer(c, 1)
    c.showPage()

    header(c, '학생 활동지', '우리 동네 지도 미션', 2, '아래 지도와 학습자료를 함께 보며 풀어요')
    draw_map(c, MARGIN, HEIGHT - 450, INNER, 282)
    txt(c, MARGIN, HEIGHT - 464, '학습용 약도 · 북쪽이 위 · 정확한 거리와 길찾기에는 사용하지 않아요', 8.5, MUTED)
    missions = data['missions']
    y = HEIGHT - 493
    for i, item in enumerate(missions[:2], start=3):
        txt(c, MARGIN, y, f'{i:02d}  {item["question"]}', 11)
        choices = item['choices']
        if isinstance(choices, list):
            rendered = '         '.join(str(choice) for choice in choices)
        else:
            rendered = str(choices)
        txt(c, MARGIN + 32, y - 23, f'(  {rendered}  )', 11)
        y -= 68
    txt(c, MARGIN, y, '05  답을 고를 때 무엇을 기준으로 비교했나요?', 11)
    line(c, MARGIN + 30, y - 26, WIDTH - MARGIN, y - 26)
    line(c, MARGIN + 30, y - 50, WIDTH - MARGIN, y - 50)
    y -= 78
    txt(c, MARGIN, y, '06  오늘 나는 방위표와 범례를 활용해 장소를 찾을 수 있어요.', 10.5)
    txt(c, MARGIN + 30, y - 22, '□ 스스로 할 수 있어요       □ 조금 더 연습할래요', 10.5)
    footer(c, 2)
    c.showPage()


def teacher(c, data):
    header(c, '교사용 지도안', '우리 동네 탐험대 수업', 1, '4학년 사회  ·  1차시 40분  ·  교사 화면 + 종이 활동지')
    y = HEIGHT - 168
    rounded(c, MARGIN, y - 88, INNER, 90, MINT)
    txt(c, MARGIN + 15, y - 21, '학습 목표', 12, GREEN)
    para(c, MARGIN + 15, y - 43, '방위표와 범례를 이용하여 우리 동네 지도에서 장소를 찾고 위치를 설명할 수 있다.', INNER - 30, 11, 17)
    txt(c, MARGIN + 15, y - 73, '관련 성취기준: [4사05-01]  [4사05-02]', 10, MUTED)
    y -= 120
    y = section(c, y, '01', '40분 수업 흐름')
    rows = [
        ('도입', '5분', '우리 학교에 처음 온 친구에게 동네를 소개하는 상황 제시. 목표 확인.'),
        ('방위', '8분', '북쪽을 기준으로 동서남북 살펴보기. 활동지 01번 완성.'),
        ('범례', '7분', '기호와 범례를 살펴보고 학교·도서관·주민센터 기호 연결.'),
        ('지도 미션', '15분', '실제 학교 주변 약도에서 장소를 찾고 활동지 03~05번 해결. 짝과 비교.'),
        ('마무리', '5분', '확인 문제 3개와 활동지 06번. 방위나 범례 사용법 한 문장으로 말하기.'),
    ]
    x_label = MARGIN + 11
    for j, (name, mins, body) in enumerate(rows):
        top = y - j * 54
        if j % 2 == 0:
            rounded(c, MARGIN, top - 47, INNER, 49, colors.HexColor('#F4F8F4'), radius=5)
        txt(c, x_label, top - 17, name, 11, GREEN)
        txt(c, x_label + 75, top - 17, mins, 10, MUTED)
        para(c, x_label + 116, top - 16, body, INNER - 140, 9.7, 15)
    y -= 287
    rounded(c, MARGIN, y - 64, INNER, 66, CREAM)
    txt(c, MARGIN + 13, y - 20, '준비물', 11, GREEN)
    para(c, MARGIN + 13, y - 40, '교사 화면, 학생 학습자료와 활동지 각 1부, 필기도구. 학습용 지도는 실제 길찾기에 사용하지 않는다.', INNER - 26, 10, 15)
    footer(c, 1)
    c.showPage()

    header(c, '교사용 정답·해설', '함께 확인해요', 2, '학생에게 먼저 생각할 시간을 주고 정답을 공개해 주세요')
    y = HEIGHT - 177
    y = section(c, y, '02', '활동지 정답과 지도 포인트')
    notes = [
        ('01', '방위표: 위 북, 오른쪽 동, 아래 남, 왼쪽 서.'),
        ('02', '가 학교, 나 도서관, 다 주민센터. 이 수업에서 약속한 기호임을 확인.'),
        ('03', f'{data["missions"][0]["answer"]}. 학교와 도서관의 좌우 위치를 비교한다.'),
        ('04', f'{data["missions"][1]["answer"]}. 도서관과 서서학동 주민센터의 위아래 위치를 비교한다.'),
        ('05', '예: 학교(또는 도서관)를 기준으로 삼고, 방위표와 장소의 위치를 비교했어요.'),
        ('06', '스스로 할 수 있는지 돌아보고 필요한 연습을 선택한다.'),
    ]
    for num, body in notes:
        txt(c, MARGIN + 5, y, num, 10, GREEN)
        y = para(c, MARGIN + 35, y, body, INNER - 42, 10, 15) - 7
    y -= 13
    y = section(c, y, '03', '수업 중 살펴볼 점')
    items = [
        '방위는 기준 장소를 먼저 정한 뒤 동서 또는 남북을 비교하게 한다.',
        '‘북쪽이 위’는 이 지도에서의 약속이며, 모든 지도에 무조건 적용하지 않는다.',
        '기호의 뜻이 헷갈리면 색뿐 아니라 모양과 범례 글자를 함께 보게 한다.',
        '도움 발문: “학교를 손가락으로 짚어 볼까요? 도서관은 학교의 왼쪽일까요?”',
        '평가: 방위표에서 네 방향을 찾고, 범례로 기호 하나를 설명하며, 기준 장소와 방향을 말할 수 있는지 관찰한다.',
    ]
    for item in items:
        txt(c, MARGIN + 2, y, '·', 12, GREEN)
        y = para(c, MARGIN + 16, y, item, INNER - 20, 9.8, 15) - 6
    sources(c, 104)
    footer(c, 2)
    c.showPage()


def main():
    for path in (DATA_PATH, MAP_PATH, FONT_PATH):
        if not path.is_file():
            raise FileNotFoundError(f'Required shared asset missing: {path}')
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    if len(data.get('missions', [])) < 2:
        raise ValueError('lesson.json must include the two shared map missions')
    pdfmetrics.registerFont(TTFont(FONT, str(FONT_PATH)))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    documents = [
        ('student-learning.pdf', learning),
        ('student-worksheet.pdf', worksheet),
        ('teacher-guide.pdf', teacher),
    ]
    for filename, render in documents:
        c = canvas.Canvas(str(OUTPUT / filename), pagesize=A4, pageCompression=1)
        render(c, data)
        c.save()
        count = len(PdfReader(OUTPUT / filename).pages)
        if count != 2:
            raise AssertionError(f'{filename} has {count} pages, expected 2')
        print(f'{filename}: {count} pages')
    writer = PdfWriter()
    for filename, _ in documents:
        writer.append(str(OUTPUT / filename))
    with (OUTPUT / 'complete-set.pdf').open('wb') as target:
        writer.write(target)
    print(f'complete-set.pdf: {len(PdfReader(OUTPUT / "complete-set.pdf").pages)} pages')


if __name__ == '__main__':
    main()
