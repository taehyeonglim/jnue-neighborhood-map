# 우리 동네 탐험대

전주교육대학교전주부설초등학교 4학년을 위한 40분 사회 수업 자료입니다. 2022 개정 사회과 교육과정의 [4사05-01], [4사05-02]와 연결하여 방위와 기호·범례로 우리 학교 주변을 살펴봅니다.

## 수업 자료

교사용 수업 화면은 `docs/index.html`입니다. 웹 화면에서 학생 학습자료, 학생 활동지, 교사용 지도안·정답, 전체 세트 PDF를 내려받을 수 있습니다. 공개 웹사이트에서 정답 자료도 접근할 수 있으므로 학생에게 활동지 링크를 따로 안내할 때 이 점을 고려해 주세요.

지도는 공공기관 위치 정보와 OpenStreetMap 위치 자료를 바탕으로 직접 제작한 학습용 약도입니다. 거리를 재거나 길찾기에 사용하지 않습니다. 실제 위치 관계가 변하지 않도록 주요 지점의 좌표를 함께 관리합니다.

## 로컬에서 확인하기

프로젝트 폴더에서 `python -m http.server 8000 --directory docs`를 실행한 다음 `http://localhost:8000/`을 엽니다. 로컬 파일을 직접 열기보다 HTTP 서버를 이용하세요.

## PDF 재생성

Python 3.10 이상과 `reportlab`, `svglib`, `pypdf`가 필요합니다. 설치 후 프로젝트 폴더에서 `python scripts/generate_pdfs.py`를 실행하면 `docs/assets/pdf/`의 PDF 네 개가 갱신됩니다. 공통 지도·문항 데이터를 수정한 뒤에는 PDF를 다시 생성하고 각 페이지를 확인하세요.

## 출처와 글꼴

- 교육과정: 교육부 고시 제2022-33호 [별책 7] 사회과 교육과정, `[4사05-01]`, `[4사05-02]`. MCP `korean-elementary-learning-map-mcp`로 조회했습니다.
- 학교: [전주교육대학교전주부설초등학교 오시는 길](https://school.jbedu.kr/jjbs/M010208/index.do).
- 지역 시설: [공공데이터포털 전국전동휠체어급속충전기표준데이터](https://www.data.go.kr/data/15034533/standard.do)의 주민센터 위치, [전주시 완산도서관 안내](https://tour.jeonju.go.kr/board/view.jeonju?boardId=BBS_0000003&contentsSid=1&dataSid=16680&paging=ok&startPage=1).
- 지도 위치: © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).
- 글꼴: Noto Sans KR, SIL Open Font License 1.1. 자세한 내용은 `docs/assets/fonts/`에 있는 라이선스를 확인하세요.
