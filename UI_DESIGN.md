# UI Design Specification - PyQt5 기반

## 1. 전체 레이아웃 구조

```
┌────────────────────────────────────────────────────────────────┐
│  데이터 수정 프로그램                                [─][□][×]  │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. 데이터 로드                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ [파일 선택]  C:\path\to\file.xlsx           [불러오기] │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  2. 단위 설정                                            │  │
│  │  ┌───────────────────┐      ┌───────────────────┐        │  │
│  │  │ 원본 단위: [초 ▼] │  →  │ 목표 단위: [분 ▼] │        │  │
│  │  └───────────────────┘      └───────────────────┘        │  │
│  │  변환 계수: 0.0166667                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  3. 데이터 범위 선택                                     │  │
│  │  열 선택: [☑ 열1] [☐ 열2] [☑ 열3] [전체 선택]            │  │
│  │  행 범위: 시작 [1    ] ~ 끝 [100  ] [전체]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  4. 수정 방법                                            │  │
│  │  방법: [곱하기 ▼]  값: [60      ]  [미리보기]             │  │
│  │  [실행]  [초기화]  [되돌리기]                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  5. 결과 및 비교                                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  [전후 비교 그래프]                                │  │  │
│  │  │                                                    │  │  │
│  │  │  (Line Chart / Bar Chart / Scatter Plot)          │  │  │
│  │  │                                                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  통계 정보:                                              │  │
│  │  평균: 123.45  최소: 10.00  최대: 500.00  표준편차: 45.67 │  │
│  │                                                          │  │
│  │  [저장]  [그래프 내보내기]                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  상태표시줄: 준비 완료                                          │
└────────────────────────────────────────────────────────────────┘
```

## 2. 컬러 스킴

### Primary Colors
- **Primary Blue**: #2196F3 (버튼, 강조 요소)
- **Primary Dark**: #1976D2 (헤더, 활성 상태)
- **Primary Light**: #BBDEFB (배경 강조)

### Secondary Colors
- **Gray Dark**: #424242 (텍스트)
- **Gray Medium**: #757575 (보조 텍스트)
- **Gray Light**: #E0E0E0 (테두리, 구분선)

### Status Colors
- **Success Green**: #4CAF50 (성공 메시지)
- **Warning Orange**: #FF9800 (경고)
- **Error Red**: #F44336 (오류)
- **Info Blue**: #2196F3 (정보)

### Background Colors
- **Window Background**: #FAFAFA
- **Panel Background**: #FFFFFF
- **Hover Background**: #F5F5F5

## 3. 위젯 구성

### Section 1: 파일 로더
- **QGroupBox**: "1. 데이터 로드"
- **QLineEdit**: 파일 경로 표시 (읽기 전용)
- **QPushButton**: "파일 선택" (파일 대화상자 열기)
- **QPushButton**: "불러오기" (데이터 로드 실행)

### Section 2: 단위 설정
- **QGroupBox**: "2. 단위 설정"
- **QComboBox**: 원본 단위 (초, 분, 시간, 일)
- **QLabel**: "→" (화살표 표시)
- **QComboBox**: 목표 단위 (초, 분, 시간, 일)
- **QLabel**: 변환 계수 표시

### Section 3: 데이터 범위 선택
- **QGroupBox**: "3. 데이터 범위 선택"
- **QCheckBox[]**: 열 선택 체크박스들
- **QPushButton**: "전체 선택"
- **QSpinBox**: 시작 행
- **QSpinBox**: 끝 행
- **QPushButton**: "전체" (모든 행 선택)

### Section 4: 수정 방법
- **QGroupBox**: "4. 수정 방법"
- **QComboBox**: 수정 방법 선택
  - 업샘플링 (보간법)
  - 다운샘플링 (축소)
  - 필터 적용 (동일 단위)

#### 업샘플링 옵션 (단위가 작아질 경우)
- **QComboBox**: 보간법 선택
  - linear (선형)
  - nearest (최근접)
  - next (다음 값)
  - previous (이전 값)
  - pchip (Piecewise Cubic)
  - cubic (3차 스플라인)
  - v5cubic (MATLAB v5 3차)
  - makima (Modified Akima)
  - spline (스플라인)

#### 다운샘플링 옵션 (단위가 커질 경우)
- **QComboBox**: 축소 방법 선택
  - 평균 (Average)
  - 건너뛰기 (Skip)
  - 최대값 (Maximum)
  - 최소값 (Minimum)
  - 중간값 (Median)

#### 필터 옵션 (단위 동일)
- **QComboBox**: 필터 종류 선택
  - LPF (저역 통과)
  - HPF (고역 통과)
  - BPF (대역 통과)
  - BSF (대역 저지)
- **QDoubleSpinBox**: 컷오프 주파수 (Hz)

#### 실행 버튼
- **QPushButton**: "미리보기"
- **QPushButton**: "실행"
- **QPushButton**: "초기화"
- **QPushButton**: "되돌리기"

### Section 5: 결과 및 비교
- **QGroupBox**: "5. 결과 및 비교"
- **MatplotlibWidget**: 그래프 표시 영역
- **QLabel[]**: 통계 정보 표시 (평균, 최소, 최대, 표준편차)
- **QPushButton**: "저장"
- **QPushButton**: "그래프 내보내기"

## 4. 폰트 설정

### Noto Sans KR 폰트
- **Primary Font**: "Noto Sans KR", 9pt
- **Header Font**: "Noto Sans KR", 10pt, Bold
- **Title Font**: "Noto Sans KR", 12pt, Bold
- **Monospace Font**: "Consolas", 9pt (파일 경로 등, 선택적)

## 5. 간격 및 여백

- **Window Padding**: 15px
- **Section Spacing**: 10px
- **Widget Spacing**: 5px
- **Button Padding**: 8px (vertical), 16px (horizontal)
- **GroupBox Padding**: 10px

## 6. 위젯 크기

### Buttons
- **Standard Button**: height 32px, min-width 80px
- **Icon Button**: 32x32px
- **Primary Button**: height 36px (강조 버튼)

### Input Fields
- **LineEdit/SpinBox**: height 28px
- **ComboBox**: height 28px
- **CheckBox**: height 20px

### Panels
- **GroupBox Title**: height 30px
- **Status Bar**: height 24px

## 7. 아이콘 사용

### 파일 작업
- 📁 파일 선택
- 📂 불러오기
- 💾 저장
- 📊 그래프 내보내기

### 작업 실행
- ▶️ 실행
- 🔄 초기화
- ↩️ 되돌리기
- 👁️ 미리보기

## 8. 상태 표시

### 프로그레스 표시
- **QProgressBar**: 파일 로드 중, 데이터 처리 중

### 상태 메시지
- **QStatusBar**: 하단 상태 표시줄
  - "준비 완료"
  - "파일 로드 중..."
  - "데이터 처리 중..."
  - "저장 완료"

## 9. 반응형 동작

### 창 크기 조절
- **Minimum Size**: 1000x700
- **Default Size**: 1200x800
- **Resizable**: True

### 레이아웃 동작
- 그래프 영역: 세로 방향으로 확장 우선
- 입력 영역: 고정 높이 유지
- 가로 폭: 모든 위젯 균등 확장

## 10. 사용자 상호작용 피드백

### Hover Effects
- 버튼: 배경색 변경 (#F5F5F5)
- 링크: 언더라인 표시

### Click Effects
- 버튼: pressed 상태 시각 효과
- 체크박스: 애니메이션

### Disabled State
- 투명도: 50%
- 색상: Gray (#BDBDBD)

## 11. 에러 및 경고 표시

### Message Box Types
- **QMessageBox.Information**: 정보 메시지
- **QMessageBox.Warning**: 경고 메시지
- **QMessageBox.Critical**: 오류 메시지
- **QMessageBox.Question**: 확인 대화상자

### Inline Validation
- 입력 필드 테두리: 빨간색 (#F44336)
- 경고 아이콘: ⚠️
- 툴팁: 오류 설명 표시

---

**Document Version**: 1.1
**Created**: 2025-11-27
**Last Updated**: 2025-11-27
**UI Framework**: PyQt5
**Font**: Noto Sans KR

## 변경 이력

### v1.1 (2025-11-27)
- 폰트를 Noto Sans KR로 변경
- 수정 방법을 3가지 카테고리로 분류:
  - 업샘플링: 9가지 보간법 지원
  - 다운샘플링: 5가지 축소 방법 지원
  - 필터 적용: 4가지 필터 종류 지원 (LPF, HPF, BPF, BSF)
- 동적 UI: 선택한 방법에 따라 해당 옵션만 표시

### v1.0 (2025-11-27)
- 초기 UI 디자인
