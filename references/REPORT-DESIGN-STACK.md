# 보고서 디자인 스택 & 레퍼런스

앞으로 HTML 보고서 만들 때 참고/활용할 스킬 모음.

---

## 1. Supanova Design Skill (메인 베이스)
- 경로: `references/supanova-design-skill/`
- 용도: 전체 프리미엄 레이아웃/디자인 스타일 베이스
- 특징: 한국어 타이포, Pretendard, 카드형, Tailwind CDN, standalone HTML
- 우선 적용 기준: `taste-skill` + `soft-skill` + `output-skill` 조합

## 2. visualize (careerhackeralex)
- 경로: `references/visualize/`
- 용도: 프리미엄 HTML 시각화 (슬라이드, 대시보드, 인포그래픽)
- 특징: 다크/라이트 테마, PNG/PDF 내보내기, Chart.js, 자연어 → HTML
- 활용 포인트: KPI 카드, 대시보드형 섹션, 프레젠테이션 슬라이드 구조

## 3. mviz (matsonj)
- 경로: `references/mviz/`
- 용도: 데이터 중심 차트/보고서, AI가 쓰기 편한 차트 빌더
- 특징: ECharts 기반, 16컬럼 그리드, 높은 data-ink ratio, JSON spec → 차트
- 활용 포인트: 시장 규모 차트, 시나리오 막대, 시계열, 비교 테이블

## 4. visual-explainer (nicobailon)
- 경로: `references/visual-explainer/`
- 용도: 다이어그램, diff 리뷰, 플로우 차트, 아키텍처 설명
- 특징: Mermaid, CSS Grid, Chart.js, HTML 테이블 자동 라우팅
- 활용 포인트: 가치사슬 다이어그램, 프로세스 플로우, 규제 타임라인

## 5. AntV Chart Visualization Skills
- 경로: `references/chart-visualization-skills/`
- 용도: 26가지 이상의 인텔리전트 차트 생성, SVG 인포그래픽
- 특징: G2/G6/L7 기반, 그래프/지리/통계 시각화
- 활용 포인트: 복잡한 경쟁 지도, 데이터 밀도가 높은 분석 섹션

## 6. baoyu-skills (JimLiu)
- 경로: `references/baoyu-skills/`
- 용도: 보고서 생성, 마크다운 → 슬라이드/인포그래픽 변환
- 특징: npx 기반, HTML 인포그래픽/보고서 특화

---

## 보고서 생성 원칙 (claw 기준)

1. **베이스**: Supanova taste-skill + soft-skill + output-skill 스타일 적용
2. **차트**: mviz 또는 ECharts 인라인으로 데이터 차트 구성
3. **다이어그램**: Mermaid 또는 SVG 인라인으로 가치사슬/타임라인 구성
4. **레이아웃**: 16컬럼 그리드, 카드형 섹션, 다크 히어로 + 라이트 바디
5. **폰트**: Pretendard (한국어 최우선), Tailwind CDN
6. **PDF 대응**: @media print 필수, 배경 보존, 페이지 분리 안정화
7. **완성도**: 플레이스홀더 금지, 아이콘(Iconify Solar), 실제 데이터/추정 수치 포함

---

마지막 업데이트: 2026-03-26
