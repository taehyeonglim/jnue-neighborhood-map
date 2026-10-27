"""Check printable page counts, embedded Korean glyphs and shared map missions."""
import json
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4

root = Path(__file__).resolve().parents[1]
assets = root / 'docs' / 'assets'
data = json.loads((assets / 'lesson.json').read_text(encoding='utf-8'))
pdfs = assets / 'pdf'
page_counts = {'student-learning.pdf': 2, 'student-worksheet.pdf': 2,
               'teacher-guide.pdf': 2, 'complete-set.pdf': 6}
readers = {name: PdfReader(pdfs / name) for name in page_counts}

for name, expected in page_counts.items():
    reader = readers[name]
    assert len(reader.pages) == expected, f'{name}: unexpected page count'
    for number, page in enumerate(reader.pages, start=1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        assert abs(width - A4[0]) < 1 and abs(height - A4[1]) < 1, f'{name}:{number} is not A4'
        embedded = False
        for ref in page['/Resources']['/Font'].values():
            item = ref.get_object()
            descriptor = item.get('/FontDescriptor')
            descriptor = descriptor.get_object() if descriptor else None
            if ('NotoSansKR' in str(item.get('/BaseFont')) and descriptor and
                    any(descriptor.get(key) for key in ('/FontFile', '/FontFile2', '/FontFile3'))):
                embedded = True
        assert embedded, f'{name}:{number}: Korean font not embedded'
    print(f'{name}: {expected} A4 pages with embedded Korean font')

learning_text = readers['student-learning.pdf'].pages[1].extract_text()
worksheet_text = readers['student-worksheet.pdf'].pages[1].extract_text()
teacher_text = readers['teacher-guide.pdf'].pages[1].extract_text()
for text in ('우리 동네 지도', '완산도서관', '동서학동 주민센터', '서서학동 주민센터', '기호와 범례'):
    assert text in learning_text and text in worksheet_text, f'map label missing: {text}'
for mission in data['missions'][:2]:
    assert mission['question'] in worksheet_text, 'worksheet question differs from source data'
    assert f'{mission["answer"]}.' in teacher_text, 'teacher answer differs from source data'
assert '북쪽을 기준으로 빈칸에 동, 서, 남' in readers['student-worksheet.pdf'].pages[0].extract_text()

expected_texts = []
for name in ('student-learning.pdf', 'student-worksheet.pdf', 'teacher-guide.pdf'):
    expected_texts += [p.extract_text() for p in readers[name].pages]
assert [p.extract_text() for p in readers['complete-set.pdf'].pages] == expected_texts, 'combined set differs'
print('Shared map labels, mission questions/answers and the combined set verified.')
