"""
메인 윈도우 - PyQt5 UI 구성
데이터 수정 프로그램의 메인 사용자 인터페이스

Author: Claude
Created: 2025-11-27
Version: 1.0.0
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton, QLineEdit, QLabel,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QFileDialog, QMessageBox, QStatusBar, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MainWindow(QMainWindow):
    """
    메인 윈도우 클래스

    데이터 수정 프로그램의 전체 UI를 구성하고 관리합니다.
    5개의 주요 섹션으로 구성:
    1. 데이터 로드
    2. 단위 설정
    3. 데이터 범위 선택
    4. 수정 방법
    5. 결과 및 비교
    """

    def __init__(self):
        """메인 윈도우 초기화"""
        super().__init__()

        # Noto Sans 폰트 설정
        self.setup_fonts()

        # 윈도우 기본 설정
        self.setWindowTitle("데이터 수정 프로그램")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # UI 구성 요소 초기화
        self.init_ui()

        # 스타일시트 적용
        self.apply_stylesheet()

        # 상태 표시줄 설정
        self.statusBar().showMessage("준비 완료")

    def setup_fonts(self):
        """Noto Sans 폰트 설정"""
        from PyQt5.QtWidgets import QApplication

        # Noto Sans 폰트를 기본 폰트로 설정
        font = QFont("Noto Sans KR", 9)
        QApplication.setFont(font)

        # 폰트 객체 저장 (재사용)
        self.default_font = QFont("Noto Sans KR", 9)
        self.header_font = QFont("Noto Sans KR", 10, QFont.Bold)
        self.title_font = QFont("Noto Sans KR", 12, QFont.Bold)

    def init_ui(self):
        """UI 구성 요소 초기화 및 배치"""

        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃 (수직 배치)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 스크롤 영역 생성 (내용이 많을 경우 대비)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        # 스크롤 내용 위젯
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)

        # 섹션 1: 데이터 로드
        scroll_layout.addWidget(self.create_file_loader_section())

        # 섹션 2: 단위 설정
        scroll_layout.addWidget(self.create_unit_config_section())

        # 섹션 3: 데이터 범위 선택
        scroll_layout.addWidget(self.create_data_selection_section())

        # 섹션 4: 수정 방법
        scroll_layout.addWidget(self.create_modification_section())

        # 섹션 5: 결과 및 비교
        scroll_layout.addWidget(self.create_visualization_section())

        # 스크롤 영역 설정
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_file_loader_section(self):
        """
        섹션 1: 데이터 로드

        파일 선택 및 데이터 불러오기 기능을 제공하는 UI 섹션

        Returns:
            QGroupBox: 파일 로더 섹션 위젯
        """
        group_box = QGroupBox("1. 데이터 로드")
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # 파일 경로 표시 (읽기 전용)
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("파일을 선택하세요...")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setMinimumWidth(400)

        # 파일 선택 버튼
        self.browse_button = QPushButton("📁 파일 선택")
        self.browse_button.setFixedWidth(120)
        self.browse_button.clicked.connect(self.browse_file)

        # 불러오기 버튼
        self.load_button = QPushButton("📂 불러오기")
        self.load_button.setFixedWidth(120)
        self.load_button.setEnabled(False)  # 파일 선택 전까지 비활성화
        self.load_button.clicked.connect(self.load_file)

        # 레이아웃에 위젯 추가
        layout.addWidget(self.file_path_edit)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.load_button)

        group_box.setLayout(layout)
        return group_box

    def create_unit_config_section(self):
        """
        섹션 2: 단위 설정

        시간 단위 변환 설정 UI 섹션
        원본 단위와 목표 단위를 선택하고 변환 계수를 표시

        Returns:
            QGroupBox: 단위 설정 섹션 위젯
        """
        group_box = QGroupBox("2. 단위 설정")
        layout = QHBoxLayout()
        layout.setSpacing(15)

        # 원본 단위 선택
        original_label = QLabel("원본 단위:")
        self.original_unit_combo = QComboBox()
        self.original_unit_combo.addItems(["초", "분", "시간", "일"])
        self.original_unit_combo.setMinimumWidth(120)
        self.original_unit_combo.currentTextChanged.connect(self.update_conversion_factor)

        # 화살표 표시
        arrow_label = QLabel("→")
        arrow_label.setFont(QFont("맑은 고딕", 14, QFont.Bold))

        # 목표 단위 선택
        target_label = QLabel("목표 단위:")
        self.target_unit_combo = QComboBox()
        self.target_unit_combo.addItems(["초", "분", "시간", "일"])
        self.target_unit_combo.setCurrentIndex(1)  # 기본값: 분
        self.target_unit_combo.setMinimumWidth(120)
        self.target_unit_combo.currentTextChanged.connect(self.update_conversion_factor)

        # 변환 계수 표시
        self.conversion_label = QLabel("변환 계수: 0.0166667")
        self.conversion_label.setStyleSheet("color: #1976D2; font-weight: bold;")

        # 레이아웃에 위젯 추가
        layout.addWidget(original_label)
        layout.addWidget(self.original_unit_combo)
        layout.addWidget(arrow_label)
        layout.addWidget(target_label)
        layout.addWidget(self.target_unit_combo)
        layout.addStretch()
        layout.addWidget(self.conversion_label)

        group_box.setLayout(layout)
        return group_box

    def create_data_selection_section(self):
        """
        섹션 3: 데이터 범위 선택

        수정할 데이터의 열과 행 범위를 선택하는 UI 섹션

        Returns:
            QGroupBox: 데이터 범위 선택 섹션 위젯
        """
        group_box = QGroupBox("3. 데이터 범위 선택")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # 열 선택 영역
        column_layout = QHBoxLayout()
        column_label = QLabel("열 선택:")
        column_label.setMinimumWidth(80)

        # 열 선택 체크박스 (동적으로 생성될 예정)
        self.column_checkboxes = []
        self.column_checkbox_layout = QHBoxLayout()

        # 전체 선택 버튼
        self.select_all_columns_button = QPushButton("전체 선택")
        self.select_all_columns_button.setFixedWidth(100)
        self.select_all_columns_button.clicked.connect(self.select_all_columns)

        column_layout.addWidget(column_label)
        column_layout.addLayout(self.column_checkbox_layout)
        column_layout.addStretch()
        column_layout.addWidget(self.select_all_columns_button)

        # 행 범위 선택 영역
        row_layout = QHBoxLayout()
        row_label = QLabel("행 범위:")
        row_label.setMinimumWidth(80)

        # 시작 행
        start_label = QLabel("시작:")
        self.start_row_spin = QSpinBox()
        self.start_row_spin.setMinimum(1)
        self.start_row_spin.setMaximum(1000000)
        self.start_row_spin.setValue(1)
        self.start_row_spin.setFixedWidth(100)

        # 끝 행
        end_label = QLabel("끝:")
        self.end_row_spin = QSpinBox()
        self.end_row_spin.setMinimum(1)
        self.end_row_spin.setMaximum(1000000)
        self.end_row_spin.setValue(100)
        self.end_row_spin.setFixedWidth(100)

        # 전체 행 선택 버튼
        self.select_all_rows_button = QPushButton("전체")
        self.select_all_rows_button.setFixedWidth(80)
        self.select_all_rows_button.clicked.connect(self.select_all_rows)

        row_layout.addWidget(row_label)
        row_layout.addWidget(start_label)
        row_layout.addWidget(self.start_row_spin)
        row_layout.addWidget(end_label)
        row_layout.addWidget(self.end_row_spin)
        row_layout.addWidget(self.select_all_rows_button)
        row_layout.addStretch()

        # 메인 레이아웃에 추가
        main_layout.addLayout(column_layout)
        main_layout.addLayout(row_layout)

        group_box.setLayout(main_layout)
        return group_box

    def create_modification_section(self):
        """
        섹션 4: 수정 방법

        데이터 수정 방법 및 값을 설정하고 실행하는 UI 섹션
        - 업샘플링: 보간법 사용
        - 다운샘플링: 평균, 건너뛰기 등
        - 동일 단위: LPF, HPF 필터

        Returns:
            QGroupBox: 수정 방법 섹션 위젯
        """
        group_box = QGroupBox("4. 수정 방법")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # 수정 설정 영역 (첫 번째 줄)
        config_layout = QHBoxLayout()

        # 수정 방법 선택
        method_label = QLabel("방법:")
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "업샘플링 (보간법)",
            "다운샘플링 (축소)",
            "필터 적용 (동일 단위)"
        ])
        self.method_combo.setMinimumWidth(180)
        self.method_combo.currentTextChanged.connect(self.on_method_changed)

        config_layout.addWidget(method_label)
        config_layout.addWidget(self.method_combo)
        config_layout.addStretch()

        # 옵션 설정 영역 (두 번째 줄)
        option_layout = QHBoxLayout()

        # 업샘플링 옵션 (보간법)
        self.interpolation_label = QLabel("보간법:")
        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItems([
            "linear (선형)",
            "nearest (최근접)",
            "next (다음 값)",
            "previous (이전 값)",
            "pchip (Piecewise Cubic)",
            "cubic (3차 스플라인)",
            "v5cubic (MATLAB v5 3차)",
            "makima (Modified Akima)",
            "spline (스플라인)"
        ])
        self.interpolation_combo.setMinimumWidth(200)

        # 다운샘플링 옵션
        self.downsampling_label = QLabel("축소 방법:")
        self.downsampling_combo = QComboBox()
        self.downsampling_combo.addItems([
            "평균 (Average)",
            "건너뛰기 (Skip)",
            "최대값 (Maximum)",
            "최소값 (Minimum)",
            "중간값 (Median)"
        ])
        self.downsampling_combo.setMinimumWidth(150)
        self.downsampling_combo.setVisible(False)

        # 필터 옵션
        self.filter_label = QLabel("필터 종류:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "LPF (저역 통과)",
            "HPF (고역 통과)",
            "BPF (대역 통과)",
            "BSF (대역 저지)"
        ])
        self.filter_combo.setMinimumWidth(150)
        self.filter_combo.setVisible(False)

        # 컷오프 주파수 입력 (필터용)
        self.cutoff_label = QLabel("컷오프 주파수:")
        self.cutoff_spin = QDoubleSpinBox()
        self.cutoff_spin.setMinimum(0.001)
        self.cutoff_spin.setMaximum(1000.0)
        self.cutoff_spin.setValue(1.0)
        self.cutoff_spin.setDecimals(3)
        self.cutoff_spin.setSuffix(" Hz")
        self.cutoff_spin.setFixedWidth(150)
        self.cutoff_spin.setVisible(False)

        # 미리보기 버튼
        self.preview_button = QPushButton("👁️ 미리보기")
        self.preview_button.setFixedWidth(120)
        self.preview_button.clicked.connect(self.preview_modification)

        option_layout.addWidget(self.interpolation_label)
        option_layout.addWidget(self.interpolation_combo)
        option_layout.addWidget(self.downsampling_label)
        option_layout.addWidget(self.downsampling_combo)
        option_layout.addWidget(self.filter_label)
        option_layout.addWidget(self.filter_combo)
        option_layout.addWidget(self.cutoff_label)
        option_layout.addWidget(self.cutoff_spin)
        option_layout.addWidget(self.preview_button)
        option_layout.addStretch()

        # 실행 버튼 영역
        action_layout = QHBoxLayout()

        # 실행 버튼 (Primary)
        self.execute_button = QPushButton("▶️ 실행")
        self.execute_button.setFixedSize(120, 36)
        self.execute_button.setObjectName("primaryButton")
        self.execute_button.clicked.connect(self.execute_modification)

        # 초기화 버튼
        self.reset_button = QPushButton("🔄 초기화")
        self.reset_button.setFixedWidth(120)
        self.reset_button.clicked.connect(self.reset_data)

        # 되돌리기 버튼
        self.undo_button = QPushButton("↩️ 되돌리기")
        self.undo_button.setFixedWidth(120)
        self.undo_button.setEnabled(False)  # 초기에는 비활성화
        self.undo_button.clicked.connect(self.undo_modification)

        action_layout.addWidget(self.execute_button)
        action_layout.addWidget(self.reset_button)
        action_layout.addWidget(self.undo_button)
        action_layout.addStretch()

        # 메인 레이아웃에 추가
        main_layout.addLayout(config_layout)
        main_layout.addLayout(option_layout)
        main_layout.addLayout(action_layout)

        group_box.setLayout(main_layout)
        return group_box

    def create_visualization_section(self):
        """
        섹션 5: 결과 및 비교

        데이터 수정 결과를 그래프와 통계로 시각화하는 UI 섹션

        Returns:
            QGroupBox: 결과 및 비교 섹션 위젯
        """
        group_box = QGroupBox("5. 결과 및 비교")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Matplotlib 그래프 영역
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)

        # 초기 그래프 설정
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("데이터 비교 그래프")
        self.ax.set_xlabel("인덱스")
        self.ax.set_ylabel("값")
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()

        # 통계 정보 영역
        stats_layout = QHBoxLayout()

        self.stats_mean_label = QLabel("평균: -")
        self.stats_min_label = QLabel("최소: -")
        self.stats_max_label = QLabel("최대: -")
        self.stats_std_label = QLabel("표준편차: -")

        # 통계 레이블 스타일
        for label in [self.stats_mean_label, self.stats_min_label,
                     self.stats_max_label, self.stats_std_label]:
            label.setStyleSheet("font-weight: bold; padding: 5px;")

        stats_layout.addWidget(QLabel("통계 정보:"))
        stats_layout.addWidget(self.stats_mean_label)
        stats_layout.addWidget(self.stats_min_label)
        stats_layout.addWidget(self.stats_max_label)
        stats_layout.addWidget(self.stats_std_label)
        stats_layout.addStretch()

        # 저장 버튼 영역
        save_layout = QHBoxLayout()

        # 저장 버튼
        self.save_button = QPushButton("💾 저장")
        self.save_button.setFixedSize(120, 36)
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_data)

        # 그래프 내보내기 버튼
        self.export_graph_button = QPushButton("📊 그래프 내보내기")
        self.export_graph_button.setFixedWidth(150)
        self.export_graph_button.clicked.connect(self.export_graph)

        save_layout.addWidget(self.save_button)
        save_layout.addWidget(self.export_graph_button)
        save_layout.addStretch()

        # 메인 레이아웃에 추가
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(stats_layout)
        main_layout.addLayout(save_layout)

        group_box.setLayout(main_layout)
        return group_box

    # ============ 이벤트 핸들러 메서드 ============

    def browse_file(self):
        """파일 선택 대화상자 열기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "데이터 파일 선택",
            "",
            "Data Files (*.xlsx *.xls *.csv *.txt);;All Files (*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_button.setEnabled(True)
            self.statusBar().showMessage(f"파일 선택됨: {file_path}")

    def load_file(self):
        """선택된 파일 불러오기"""
        file_path = self.file_path_edit.text()

        if not file_path:
            QMessageBox.warning(self, "경고", "파일을 먼저 선택하세요.")
            return

        # TODO: 실제 파일 로드 로직 구현
        self.statusBar().showMessage("파일 로드 중...")
        QMessageBox.information(self, "정보", f"파일 로드 기능 구현 예정\n{file_path}")
        self.statusBar().showMessage("파일 로드 완료")

    def update_conversion_factor(self):
        """단위 변환 계수 업데이트"""
        original = self.original_unit_combo.currentText()
        target = self.target_unit_combo.currentText()

        # 변환 테이블 (초 기준)
        conversion_table = {
            '초': {'초': 1, '분': 1/60, '시간': 1/3600, '일': 1/86400},
            '분': {'초': 60, '분': 1, '시간': 1/60, '일': 1/1440},
            '시간': {'초': 3600, '분': 60, '시간': 1, '일': 1/24},
            '일': {'초': 86400, '분': 1440, '시간': 24, '일': 1}
        }

        factor = conversion_table[original][target]
        self.conversion_label.setText(f"변환 계수: {factor:.10f}")

    def select_all_columns(self):
        """모든 열 선택/해제"""
        # TODO: 체크박스 전체 선택 로직 구현
        QMessageBox.information(self, "정보", "전체 열 선택 기능 구현 예정")

    def select_all_rows(self):
        """모든 행 선택"""
        # TODO: 실제 데이터의 행 개수에 맞춰 설정
        self.start_row_spin.setValue(1)
        self.end_row_spin.setValue(self.end_row_spin.maximum())
        self.statusBar().showMessage("전체 행 선택됨")

    def on_method_changed(self, method):
        """
        수정 방법 변경 시 UI 업데이트

        - 업샘플링: 보간법 옵션 표시
        - 다운샘플링: 축소 방법 옵션 표시
        - 필터 적용: 필터 종류 및 컷오프 주파수 옵션 표시
        """
        # 모든 옵션 숨기기
        self.interpolation_label.setVisible(False)
        self.interpolation_combo.setVisible(False)
        self.downsampling_label.setVisible(False)
        self.downsampling_combo.setVisible(False)
        self.filter_label.setVisible(False)
        self.filter_combo.setVisible(False)
        self.cutoff_label.setVisible(False)
        self.cutoff_spin.setVisible(False)

        # 선택된 방법에 따라 해당 옵션만 표시
        if method == "업샘플링 (보간법)":
            self.interpolation_label.setVisible(True)
            self.interpolation_combo.setVisible(True)
            self.statusBar().showMessage("업샘플링: 데이터 포인트 증가 (보간법 사용)")

        elif method == "다운샘플링 (축소)":
            self.downsampling_label.setVisible(True)
            self.downsampling_combo.setVisible(True)
            self.statusBar().showMessage("다운샘플링: 데이터 포인트 감소 (평균, 건너뛰기 등)")

        elif method == "필터 적용 (동일 단위)":
            self.filter_label.setVisible(True)
            self.filter_combo.setVisible(True)
            self.cutoff_label.setVisible(True)
            self.cutoff_spin.setVisible(True)
            self.statusBar().showMessage("필터 적용: 신호 필터링 (LPF, HPF 등)")

    def preview_modification(self):
        """데이터 수정 미리보기"""
        # TODO: 미리보기 로직 구현
        QMessageBox.information(self, "미리보기", "수정 결과 미리보기 기능 구현 예정")

    def execute_modification(self):
        """데이터 수정 실행"""
        method = self.method_combo.currentText()

        # 선택된 방법에 따라 옵션 가져오기
        if method == "업샘플링 (보간법)":
            option = self.interpolation_combo.currentText()
            info_text = f"데이터 수정 실행\n방법: {method}\n보간법: {option}"
        elif method == "다운샘플링 (축소)":
            option = self.downsampling_combo.currentText()
            info_text = f"데이터 수정 실행\n방법: {method}\n축소 방법: {option}"
        elif method == "필터 적용 (동일 단위)":
            filter_type = self.filter_combo.currentText()
            cutoff = self.cutoff_spin.value()
            option = f"{filter_type}, 컷오프: {cutoff} Hz"
            info_text = f"데이터 수정 실행\n방법: {method}\n필터: {filter_type}\n컷오프: {cutoff} Hz"
        else:
            option = ""
            info_text = f"데이터 수정 실행\n방법: {method}"

        # TODO: 실제 데이터 수정 로직 구현
        self.statusBar().showMessage(f"데이터 처리 중... ({method})")
        QMessageBox.information(self, "실행", info_text)

        # 되돌리기 버튼 활성화
        self.undo_button.setEnabled(True)
        self.statusBar().showMessage("데이터 수정 완료")

    def reset_data(self):
        """데이터 초기화"""
        reply = QMessageBox.question(
            self,
            "확인",
            "원본 데이터로 초기화하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # TODO: 데이터 초기화 로직 구현
            self.statusBar().showMessage("데이터 초기화됨")
            self.undo_button.setEnabled(False)

    def undo_modification(self):
        """수정 되돌리기"""
        # TODO: 되돌리기 로직 구현
        QMessageBox.information(self, "되돌리기", "이전 상태로 되돌리기 기능 구현 예정")
        self.statusBar().showMessage("수정 되돌림")

    def save_data(self):
        """수정된 데이터 저장"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "데이터 저장",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            # TODO: 실제 저장 로직 구현
            self.statusBar().showMessage(f"저장 중: {file_path}")
            QMessageBox.information(self, "저장", f"데이터 저장 완료\n{file_path}")
            self.statusBar().showMessage("저장 완료")

    def export_graph(self):
        """그래프 이미지로 내보내기"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "그래프 내보내기",
            "",
            "PNG Image (*.png);;PDF Document (*.pdf);;All Files (*)"
        )

        if file_path:
            # TODO: 그래프 저장 로직 구현
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "내보내기", f"그래프 저장 완료\n{file_path}")
            self.statusBar().showMessage("그래프 내보내기 완료")

    def apply_stylesheet(self):
        """애플리케이션 스타일시트 적용 (Noto Sans KR 폰트 사용)"""
        stylesheet = """
            /* 전체 윈도우 스타일 */
            QMainWindow {
                background-color: #FAFAFA;
                font-family: 'Noto Sans KR', sans-serif;
            }

            /* GroupBox 스타일 */
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-family: 'Noto Sans KR', sans-serif;
                font-weight: bold;
                font-size: 10pt;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1976D2;
            }

            /* 버튼 스타일 */
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 9pt;
                min-height: 28px;
            }

            QPushButton:hover {
                background-color: #1976D2;
            }

            QPushButton:pressed {
                background-color: #0D47A1;
            }

            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #FFFFFF;
            }

            /* Primary 버튼 스타일 */
            QPushButton#primaryButton {
                background-color: #1976D2;
                font-weight: bold;
                font-size: 10pt;
            }

            QPushButton#primaryButton:hover {
                background-color: #0D47A1;
            }

            /* 입력 필드 스타일 */
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-height: 22px;
                font-family: 'Noto Sans KR', sans-serif;
                font-size: 9pt;
            }

            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #2196F3;
            }

            QLineEdit:read-only {
                background-color: #F5F5F5;
                color: #757575;
            }

            /* ComboBox 스타일 */
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }

            /* 체크박스 스타일 */
            QCheckBox {
                spacing: 5px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #BDBDBD;
                border-radius: 3px;
                background-color: white;
            }

            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }

            /* 레이블 스타일 */
            QLabel {
                color: #424242;
                font-family: 'Noto Sans KR', sans-serif;
                font-size: 9pt;
            }

            /* 상태 표시줄 스타일 */
            QStatusBar {
                background-color: #F5F5F5;
                border-top: 1px solid #E0E0E0;
                color: #757575;
            }

            /* 스크롤바 스타일 */
            QScrollBar:vertical {
                border: none;
                background-color: #F5F5F5;
                width: 12px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background-color: #BDBDBD;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #9E9E9E;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """

        self.setStyleSheet(stylesheet)


if __name__ == '__main__':
    # 테스트 실행
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
