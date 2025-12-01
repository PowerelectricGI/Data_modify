"""
메인 윈도우 - PyQt5 UI 구성
데이터 수정 프로그램의 메인 사용자 인터페이스 (SCADA 스타일)
.ui 파일을 로드하여 사용

Author: Claude
Created: 2025-11-27
Version: 1.0.0
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QCheckBox,
    QVBoxLayout, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QLabel, QTextEdit,
    QGroupBox, QListWidget, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
try:
    from scipy.interpolate import interp1d, PchipInterpolator, Akima1DInterpolator, CubicSpline
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class TableViewDialog(QDialog):
    """데이터 테이블을 보여주는 팝업 다이얼로그"""
    
    def __init__(self, parent=None, data=None, headers=None):
        super().__init__(parent)
        self.setWindowTitle("Data Table View")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # 다크 테마 스타일
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QTableWidget {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                gridline-color: #3C3C3C;
                color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #007ACC;
            }
            QHeaderView::section {
                background-color: #333337;
                color: #E0E0E0;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #3C3C3C;
                border-right: 1px solid #3C3C3C;
                font-weight: bold;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 테이블 위젯
        self.table = QTableWidget()
        
        # 데이터가 있으면 표시
        if data is not None and headers is not None:
            self.table.setColumnCount(len(headers))
            self.table.setRowCount(len(data))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # 데이터 채우기 (최대 1000행까지만 표시하여 성능 최적화)
            max_rows = min(len(data), 1000)
            for row in range(max_rows):
                for col, value in enumerate(data[row]):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        
        layout.addWidget(self.table)
        
        # 닫기 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)


class MethodInfoDialog(QDialog):
    """수정 방법 설명을 보여주는 팝업 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modification Methods Information")
        self.setMinimumSize(650, 600)
        self.resize(700, 650)
        
        # 다크 테마 스타일
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 0;
            }
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3C3C3C;
                color: #E0E0E0;
                font-size: 12px;
                padding: 10px;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("📖 Modification Methods Description")
        layout.addWidget(title)
        
        # 설명 텍스트
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <style>
            h2 { color: #007ACC; margin-top: 20px; margin-bottom: 10px; }
            h3 { color: #00CED1; margin-top: 15px; margin-bottom: 5px; }
            p { color: #E0E0E0; margin: 5px 0; line-height: 1.4; }
            .category { color: #FFA500; font-weight: bold; }
        </style>
        
        <h2>📐 기본 연산 (Basic Operations)</h2>
        
        <h3>Multiplication (곱하기)</h3>
        <p>선택한 데이터에 지정된 값을 곱합니다. 예: 값이 2이면 모든 데이터가 2배가 됩니다.</p>
        
        <h3>Division (나누기)</h3>
        <p>선택한 데이터를 지정된 값으로 나눕니다. 예: 값이 2이면 모든 데이터가 절반이 됩니다.</p>
        
        <h3>Addition (더하기)</h3>
        <p>선택한 데이터에 지정된 값을 더합니다. 예: 값이 10이면 모든 데이터에 10이 추가됩니다.</p>
        
        <h3>Subtraction (빼기)</h3>
        <p>선택한 데이터에서 지정된 값을 뺍니다. 예: 값이 5이면 모든 데이터에서 5가 감소됩니다.</p>
        
        <h2>📈 업샘플링 (Upsampling) - 단위가 작아질 때</h2>
        <p class="category">원본 단위 > 목표 단위 (예: 1분 → 10초)</p>
        
        <h3>Linear (선형 보간)</h3>
        <p>두 점 사이를 직선으로 연결하여 보간. 가장 기본적인 방법.</p>
        
        <h3>Nearest (최근접)</h3>
        <p>가장 가까운 데이터 포인트의 값을 사용.</p>
        
        <h3>Next / Previous (다음/이전 값)</h3>
        <p>다음 또는 이전 데이터 포인트의 값을 사용.</p>
        
        <h3>PCHIP (구간별 3차)</h3>
        <p>Piecewise Cubic Hermite Interpolating Polynomial. 부드럽고 단조성 유지.</p>
        
        <h3>Cubic (3차 스플라인)</h3>
        <p>3차 다항식을 사용한 부드러운 곡선 보간.</p>
        
        <h3>V5Cubic (MATLAB V5)</h3>
        <p>MATLAB Version 5 스타일의 3차 보간.</p>
        
        <h3>Makima (수정 Akima)</h3>
        <p>Modified Akima 보간. 오버슈팅을 줄인 부드러운 곡선.</p>
        
        <h3>Spline (스플라인)</h3>
        <p>자연 스플라인 보간. 매우 부드러운 곡선 생성.</p>
        
        <h2>📉 다운샘플링 (Downsampling) - 단위가 커질 때</h2>
        <p class="category">원본 단위 < 목표 단위 (예: 1초 → 1분)</p>
        
        <h3>Average (평균)</h3>
        <p>구간 내 데이터의 평균값을 사용. 가장 일반적인 방법.</p>
        
        <h3>Skip (건너뛰기)</h3>
        <p>일정 간격으로 데이터를 선택. 빠르지만 정보 손실 가능.</p>
        
        <h3>Max / Min (최대/최소값)</h3>
        <p>구간 내 최대값 또는 최소값을 사용. 피크 분석에 유용.</p>
        
        <h3>Median (중앙값)</h3>
        <p>구간 내 중앙값을 사용. 이상치에 강건함.</p>
        
        <h2>🔧 필터 (Filter) - 동일 단위일 때</h2>
        <p class="category">원본 단위 = 목표 단위</p>
        
        <h3>LPF (저역통과필터)</h3>
        <p>Low Pass Filter. 고주파 노이즈를 제거하고 저주파 신호만 통과.</p>
        
        <h3>HPF (고역통과필터)</h3>
        <p>High Pass Filter. 저주파 성분을 제거하고 고주파 신호만 통과.</p>
        """)
        
        layout.addWidget(info_text)
        
        # 닫기 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)


class MainWindow(QMainWindow):
    """
    메인 윈도우 클래스 - SCADA 스타일 UI

    데이터 수정 프로그램의 전체 UI를 구성하고 관리합니다.
    .ui 파일을 로드하여 UI를 구성합니다.
    """

    def __init__(self):
        """메인 윈도우 초기화"""
        super().__init__()

        # .ui 파일 로드
        ui_path = os.path.join(os.path.dirname(__file__), 'main_window.ui')
        uic.loadUi(ui_path, self)

        # UI 요소 크기 조정 (버튼 텍스트 잘림 방지)
        self.btnTableView.setMinimumWidth(120)
        self.btnTableView.setMaximumWidth(120)

        # 데이터 관련 변수 초기화
        self.df = None
        self.file_path = None

        # 추가 초기화
        self.setup_graph()
        self.setup_custom_unit_visibility()
        self.setup_stats_and_log_ui()  # 통계 및 로그 UI 추가
        self.connect_signals()

        # 상태 표시줄 설정
        self.statusbar.showMessage("Ready. Please load a data file.")
        self.lblFileInfo.setText("No file loaded")

    def setup_graph(self):
        """Matplotlib 그래프 설정"""
        # 한글 폰트 설정 (Windows)
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False

        # frameGraph의 레이아웃에서 placeholder 제거
        layout = self.frameGraph.layout()
        
        # 기존 위젯 제거
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Matplotlib Figure 생성
        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor='#1E1E1E')
        self.canvas = FigureCanvas(self.figure)
        
        # 그래프 설정
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1E1E1E')
        self.ax.set_title("Before/After Comparison Graph", color='white', fontsize=12, fontweight='bold')
        self.ax.set_xlabel("Sample Count", color='#CCCCCC')
        self.ax.set_ylabel("Value", color='#CCCCCC')
        self.ax.tick_params(colors='#CCCCCC')
        self.ax.grid(True, alpha=0.3, color='#555555')
        
        # 스파인 색상
        for spine in self.ax.spines.values():
            spine.set_color('#555555')
        
        self.figure.tight_layout()
        
        # 레이아웃에 캔버스 추가
        layout.addWidget(self.canvas)

    def setup_custom_unit_visibility(self):
        """Custom 단위 선택 시 위젯 표시/숨김 설정"""
        # 초기 상태: Custom이 아니면 숨김
        self.update_custom_unit_visibility()

    def update_custom_unit_visibility(self):
        """Custom 선택 여부에 따라 위젯 표시/숨김"""
        original_is_custom = "Custom" in self.comboOriginalUnit.currentText()
        target_is_custom = "Custom" in self.comboTargetUnit.currentText()
        
        # Original 단위 커스텀 설정
        self.lblCustomOriginal.setVisible(original_is_custom)
        self.spinOriginalValue.setVisible(original_is_custom)
        self.comboOriginalBaseUnit.setVisible(original_is_custom)
        
        # Target 단위 커스텀 설정
        self.lblCustomTarget.setVisible(target_is_custom)
        self.spinTargetValue.setVisible(target_is_custom)
        self.comboTargetBaseUnit.setVisible(target_is_custom)
        
        # 변환 계수 업데이트
        self.update_conversion_factor()

    def setup_stats_and_log_ui(self):
        """통계 및 로그 섹션 UI 추가 (Code-behind)"""
        # 1. GroupBox 생성 - 하얀색 실선 테두리 스타일
        self.groupStatsLog = QGroupBox("5. Statistics & Log")
        self.groupStatsLog.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 1px solid white;
                border-radius: 0px;
                margin-top: 8px;
                padding: 10px;
                padding-top: 5px;
                font-weight: normal;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 5px;
                top: 0px;
                padding: 0px 3px;
                background-color: #1E1E1E;
                color: white;
                font-size: 11px;
                font-weight: normal;
            }
        """)
        
        layout = QVBoxLayout(self.groupStatsLog)
        layout.setSpacing(10)
        
        # 2. 통계 테이블 (Min, Max, Avg, Std)
        stats_label = QLabel("📊 Quick Statistics")
        stats_label.setStyleSheet("color: white; font-weight: normal; margin-bottom: 3px; font-size: 11px;")
        layout.addWidget(stats_label)
        
        self.tableStats = QTableWidget(1, 4)
        self.tableStats.setHorizontalHeaderLabels(["Min", "Max", "Avg", "Std"])
        self.tableStats.setVerticalHeaderLabels(["Value"])
        self.tableStats.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableStats.verticalHeader().setVisible(False)
        self.tableStats.setFixedHeight(60)
        self.tableStats.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                border: 1px solid #3C3C3C;
                color: #E0E0E0;
                gridline-color: #3C3C3C;
            }
            QHeaderView::section {
                background-color: #333337;
                color: #AAAAAA;
                padding: 2px;
                border: none;
                font-size: 11px;
            }
        """)
        # 초기값 설정
        for col in range(4):
            self.tableStats.setItem(0, col, QTableWidgetItem("-"))
            
        layout.addWidget(self.tableStats)
        
        # 3. 로그 리스트 (History)
        log_label = QLabel("📝 Operation Log")
        log_label.setStyleSheet("color: white; font-weight: normal; margin-top: 3px; margin-bottom: 3px; font-size: 11px;")
        layout.addWidget(log_label)
        
        self.listLog = QListWidget()
        self.listLog.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                border: 1px solid #3C3C3C;
                color: #E0E0E0;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 4px;
            }
        """)
        self.listLog.addItem("Ready. System initialized.")
        layout.addWidget(self.listLog)
        
        # 4. 왼쪽 패널에 추가 (Spacer 바로 앞에 추가)
        # leftPanelLayout의 마지막 아이템은 Spacer이므로, count() - 1 위치에 삽입
        count = self.leftPanelLayout.count()
        if count > 0:
            self.leftPanelLayout.insertWidget(count - 1, self.groupStatsLog)
        else:
            self.leftPanelLayout.addWidget(self.groupStatsLog)

    def connect_signals(self):
        """시그널-슬롯 연결"""
        # 버튼 연결
        self.btnLoadFile.clicked.connect(self.browse_file)
        self.btnTableView.clicked.connect(self.show_table_view)
        self.btnPreviewSelection.clicked.connect(self.preview_selection)
        self.btnMethodInfo.clicked.connect(self.show_method_info)
        self.btnPreview.clicked.connect(self.preview_modification)
        self.btnExecute.clicked.connect(self.execute_modification)
        self.btnSaveAs.clicked.connect(self.save_data)
        self.btnExportGraph.clicked.connect(self.export_graph)

        # 콤보박스 연결
        self.comboOriginalUnit.currentTextChanged.connect(self.update_custom_unit_visibility)
        self.comboTargetUnit.currentTextChanged.connect(self.update_custom_unit_visibility)
        self.comboMethod.currentTextChanged.connect(self.on_method_changed)
        
        # Custom 단위 SpinBox 연결
        self.spinOriginalValue.valueChanged.connect(self.update_conversion_factor)
        self.spinTargetValue.valueChanged.connect(self.update_conversion_factor)
        self.comboOriginalBaseUnit.currentTextChanged.connect(self.update_conversion_factor)
        self.comboTargetBaseUnit.currentTextChanged.connect(self.update_conversion_factor)

    def add_log(self, message):
        """로그 리스트에 메시지 추가"""
        self.listLog.addItem(message)
        self.listLog.scrollToBottom()
        self.statusbar.showMessage(message)

    def update_statistics(self):
        """현재 데이터의 통계 업데이트"""
        if self.df is None:
            return
            
        # 첫 번째 숫자형 컬럼 찾기 (Time 제외)
        target_col = None
        for col in self.df.columns:
            if col.lower() != 'time' and pd.api.types.is_numeric_dtype(self.df[col]):
                target_col = col
                break
        
        if target_col:
            stats = self.df[target_col].describe()
            self.tableStats.setItem(0, 0, QTableWidgetItem(f"{stats['min']:.4g}"))
            self.tableStats.setItem(0, 1, QTableWidgetItem(f"{stats['max']:.4g}"))
            self.tableStats.setItem(0, 2, QTableWidgetItem(f"{stats['mean']:.4g}"))
            self.tableStats.setItem(0, 3, QTableWidgetItem(f"{stats['std']:.4g}"))
            self.add_log(f"Stats updated for column: {target_col}")

    # ============ 이벤트 핸들러 메서드 ============

    def browse_file(self):
        """파일 선택 대화상자 열기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "Data Files (*.xlsx *.xls *.csv *.txt);;All Files (*)"
        )

        if file_path:
            self.load_data(file_path)

    def load_data(self, file_path):
        """데이터 파일 로드"""
        try:
            self.editFilePath.setText(file_path)
            self.add_log(f"Loading file: {os.path.basename(file_path)}...")
            
            # 파일 확장자에 따라 로드
            if file_path.endswith('.csv') or file_path.endswith('.txt'):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            self.file_path = file_path
            
            # UI 업데이트
            rows, cols = self.df.shape
            self.lblFileInfo.setText(f"Loaded: {rows} rows, {cols} columns")
            self.add_log(f"Successfully loaded {rows} rows, {cols} columns.")
            
            # Row Range 초기화
            self.editRowStart.setText("0")
            self.editRowEnd.setText(str(rows))
            
            # Column Checkbox 동적 생성
            # 기존 체크박스 제거
            while self.columnSelectLayout.count() > 1: # 첫 번째 아이템(Label) 제외하고 제거
                item = self.columnSelectLayout.takeAt(1)
                if item.widget():
                    item.widget().deleteLater()
            
            # 새 체크박스 추가
            self.column_checkboxes = []
            for col in self.df.columns:
                chk = QCheckBox(col)
                chk.setChecked(True) # 기본적으로 모두 선택
                chk.setStyleSheet("color: #E0E0E0;")
                chk.stateChanged.connect(self.update_graph_from_selection) # 이벤트 연결
                self.columnSelectLayout.addWidget(chk)
                self.column_checkboxes.append(chk)
            
            # 통계 업데이트
            self.update_statistics()
            
            # 그래프 초기화
            self.update_graph_from_selection()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
            self.add_log(f"Error loading file: {str(e)}")

    def update_graph_from_selection(self):
        """선택된 컬럼에 따라 그래프 업데이트"""
        if self.df is None: return
        
        # 선택된 컬럼 확인
        selected_cols = []
        if hasattr(self, 'column_checkboxes'):
            for chk in self.column_checkboxes:
                if chk.isChecked():
                    selected_cols.append(chk.text())
        
        if not selected_cols:
            self.ax.clear()
            self.ax.set_facecolor('#1E1E1E')
            self.ax.grid(True, alpha=0.3, color='#555555')
            self.canvas.draw()
            return

        # 데이터 준비 (Downsampling)
        rows = len(self.df)
        max_points = 2000
        if rows > max_points:
            step = rows // max_points
            plot_df = self.df.iloc[::step]
        else:
            plot_df = self.df
            
        self.ax.clear()
        self.selection_span = None # Reset selection span
        self.ax.set_facecolor('#1E1E1E')
        self.ax.grid(True, alpha=0.3, color='#555555')
        
        # 각 컬럼 플롯
        x_index = plot_df.index
        for col in selected_cols:
            # 데이터가 숫자가 아닌 경우 처리 (문자열이 Y축에 표시되는 문제 방지)
            try:
                # 숫자로 변환 시도 (에러 발생 시 NaN)
                numeric_data = pd.to_numeric(plot_df[col], errors='coerce')
                
                # 유효한 데이터가 하나라도 있는 경우에만 플롯
                if not numeric_data.isna().all():
                    self.ax.plot(x_index, numeric_data, label=col, linewidth=1)
                else:
                    self.add_log(f"Skipped plotting non-numeric column: {col}")
            except Exception as e:
                self.add_log(f"Error plotting column {col}: {str(e)}")
            
        self.ax.legend(loc='upper left', facecolor='#2D2D30', edgecolor='#555555', labelcolor='white')
        
        # X축 라벨 설정
        self.ax.set_xlabel("Sample Count", color='#CCCCCC')
        self.ax.set_ylabel("Value", color='#CCCCCC')
        
        # 눈금 색상 설정
        self.ax.tick_params(axis='x', colors='#CCCCCC')
        self.ax.tick_params(axis='y', colors='#CCCCCC')
        
        # X축이 너무 빽빽하지 않게 자동 조정
        self.figure.autofmt_xdate()
        
        self.canvas.draw()

    def plot_data(self, x, y):
        """데이터 플롯 (Legacy support or single usage)"""
        # 이 메서드는 이제 update_graph_from_selection에 의해 대체될 수 있음
        # 하지만 호환성을 위해 남겨두거나, 내부적으로 update_graph_from_selection을 호출하도록 변경 가능
        # 여기서는 단순화를 위해 남겨두되, 실제로는 위 함수가 주도함.
        pass

    def on_method_changed(self, method):
        """수정 방법 변경 시 UI 업데이트"""
        # 기본 연산일 때만 Value 입력 표시
        is_basic_op = method in ["Multiplication", "Division", "Addition", "Subtraction"]
        self.lblMethodValue.setVisible(is_basic_op)
        self.spinMethodValue.setVisible(is_basic_op)
        
        # 설명 업데이트
        descriptions = {
            "Multiplication": "Multiply selected data by value.",
            "Division": "Divide selected data by value.",
            "Addition": "Add value to selected data.",
            "Subtraction": "Subtract value from selected data.",
            "Linear": "Linear interpolation (Upsampling).",
            "Cubic": "Cubic spline interpolation (Upsampling).",
            "Nearest": "Nearest neighbor interpolation (Upsampling).",
            "Average": "Average resampling (Downsampling).",
            "Max": "Max value resampling (Downsampling).",
            "Min": "Min value resampling (Downsampling)."
        }
        self.lblMethodDescription.setText(descriptions.get(method, ""))

    def update_conversion_factor(self):
        """단위 변환 계수 업데이트"""
        # 단위를 초 단위로 변환하는 기준값
        unit_to_seconds = {
            '초': 1,
            '분': 60,
            '시간': 3600,
            '일': 86400
        }
        
        # Helper function to get seconds from unit selection
        def get_seconds(unit_text, is_custom, custom_val, custom_base):
            if "Custom" in unit_text:
                return custom_val * unit_to_seconds.get(custom_base, 1)
            else:
                # "분 (minute)" -> "분"
                unit_key = unit_text.split()[0]
                return unit_to_seconds.get(unit_key, 1)

        # Original 단위 계산
        original_seconds = get_seconds(
            self.comboOriginalUnit.currentText(),
            "Custom" in self.comboOriginalUnit.currentText(),
            self.spinOriginalValue.value(),
            self.comboOriginalBaseUnit.currentText()
        )
        
        # Target 단위 계산
        target_seconds = get_seconds(
            self.comboTargetUnit.currentText(),
            "Custom" in self.comboTargetUnit.currentText(),
            self.spinTargetValue.value(),
            self.comboTargetBaseUnit.currentText()
        )
        
        # 변환 계수 계산 (Original / Target)
        if target_seconds != 0:
            self.conversion_ratio = original_seconds / target_seconds
        else:
            self.conversion_ratio = 1.0
            
        # 결과 표시
        if hasattr(self, 'lblConversionFactor'):
            self.lblConversionFactor.setText(f"Conversion Factor: {self.conversion_ratio:.4g}")
        

    def preview_selection(self):
        """데이터 선택 미리보기 (그래프에 영역 표시)"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return
            
        try:
            start_row = int(self.editRowStart.text())
            end_row = int(self.editRowEnd.text())
            
            if start_row < 0 or end_row >= len(self.df) or start_row > end_row:
                raise ValueError("Invalid row range.")
            
            # 그래프에 영역 표시
            # 기존 영역 제거
            if hasattr(self, 'selection_span') and self.selection_span:
                try:
                    self.selection_span.remove()
                except:
                    pass
                self.selection_span = None
            
            # 노란색 반투명 영역으로 표시
            self.selection_span = self.ax.axvspan(start_row, end_row, color='yellow', alpha=0.2, label='Selected Range')
            
            # 범례 업데이트 (중복 방지)
            handles, labels = self.ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), loc='upper left', facecolor='#2D2D30', edgecolor='#555555', labelcolor='white')
            
            self.canvas.draw()
            
            # 선택된 컬럼 확인 (로그용)
            selected_cols = []
            if hasattr(self, 'column_checkboxes'):
                for chk in self.column_checkboxes:
                    if chk.isChecked():
                        selected_cols.append(chk.text())
            
            self.add_log(f"Selected range: {start_row} to {end_row}. Columns: {len(selected_cols)}")
            
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid row indices.")

    def on_method_changed(self, method_text):
        """수정 방법 변경 시 UI 업데이트"""
        # Method 텍스트 파싱 (예: "Multiplication (곱하기)" -> "Multiplication")
        method = method_text.split()[0]
        
        # 기본 연산 또는 필터일 때 Value 입력 표시
        is_basic_op = method in ["Multiplication", "Division", "Addition", "Subtraction"]
        is_filter = method in ["LPF", "HPF"]
        
        self.lblValue.setVisible(is_basic_op or is_filter)
        self.editValue.setVisible(is_basic_op or is_filter)
        
        # 라벨 텍스트 변경
        if is_filter:
            self.lblValue.setText("Tau (s)")
        else:
            self.lblValue.setText("Value")
        
        # 설명 업데이트 (라벨이 없으므로 Statusbar 사용)
        descriptions = {
            "Multiplication": "Multiply selected data by value.",
            "Division": "Divide selected data by value.",
            "Addition": "Add value to selected data.",
            "Subtraction": "Subtract value from selected data.",
            "Linear": "Linear interpolation (Upsampling).",
            "Cubic": "Cubic spline interpolation (Upsampling).",
            "Nearest": "Nearest neighbor interpolation (Upsampling).",
            "Average": "Average resampling (Downsampling).",
            "Max": "Max value resampling (Downsampling).",
            "Min": "Min value resampling (Downsampling).",
            "LPF": "Low Pass Filter (Tau = Time Constant).",
            "HPF": "High Pass Filter (Tau = Time Constant)."
        }
        # self.lblMethodDescription.setText(descriptions.get(method, "")) # 라벨 없음
        self.statusbar.showMessage(f"Method: {method} - {descriptions.get(method, '')}")

    def apply_modification(self, df_subset, method, value, ratio):
        """데이터 수정 로직 적용 (Core Logic)"""
        # 데이터프레임 복사 및 수치형 변환
        result_df = df_subset.copy()
        
        # 모든 컬럼을 수치형으로 변환 (에러 발생 시 NaN)
        # 이렇게 해야 mean(), interp() 등 수치 연산에서 에러가 발생하지 않음
        for col in result_df.columns:
            result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
        
        # 1. Basic Operations
        if method == "Multiplication":
            result_df = result_df * value
        elif method == "Division":
            if value != 0:
                result_df = result_df / value
        elif method == "Addition":
            result_df = result_df + value
        elif method == "Subtraction":
            result_df = result_df - value
            
        # 4. Filters (LPF, HPF)
        elif method in ["LPF", "HPF"]:
            tau = value # Time constant
            dt = getattr(self, 'current_dt', 1.0) # Sampling interval
            
            if tau <= 0:
                return result_df # Invalid tau
            
            # Filter implementation
            for col in result_df.columns:
                data = result_df[col].values
                filtered_data = np.zeros_like(data)
                
                if method == "LPF":
                    # Low Pass Filter: y[i] = alpha * x[i] + (1 - alpha) * y[i-1]
                    # alpha = dt / (tau + dt)
                    alpha = dt / (tau + dt)
                    filtered_data[0] = data[0]
                    for i in range(1, len(data)):
                        # Handle NaN
                        if np.isnan(data[i]):
                            filtered_data[i] = filtered_data[i-1]
                        else:
                            filtered_data[i] = alpha * data[i] + (1 - alpha) * filtered_data[i-1]
                            
                elif method == "HPF":
                    # High Pass Filter: y[i] = alpha * (y[i-1] + x[i] - x[i-1])
                    # alpha = tau / (tau + dt)
                    alpha = tau / (tau + dt)
                    filtered_data[0] = 0 # Start from 0 or data[0]
                    for i in range(1, len(data)):
                        if np.isnan(data[i]):
                            filtered_data[i] = filtered_data[i-1]
                        else:
                            filtered_data[i] = alpha * (filtered_data[i-1] + data[i] - data[i-1])
                            
                result_df[col] = filtered_data
            
        # 2. Upsampling (Ratio > 1)
        elif method in ["Linear", "Cubic", "Nearest", "Next", "Previous", "PCHIP", "V5Cubic", "Makima", "Spline"]:
            if ratio <= 1:
                return result_df # Upsampling requires ratio > 1
                
            # 새로운 인덱스 생성 (현재 길이 * ratio)
            new_length = int(len(result_df) * ratio)
            old_indices = np.linspace(0, len(result_df) - 1, len(result_df))
            new_indices = np.linspace(0, len(result_df) - 1, new_length)
            
            # 보간 적용 (각 컬럼별)
            new_data = {}
            for col in result_df.columns:
                # NaN이 포함된 경우 보간 결과도 NaN일 수 있음.
                
                # Scipy 사용 가능 여부에 따른 분기
                if SCIPY_AVAILABLE:
                    try:
                        y = result_df[col].values
                        
                        if method == "Linear":
                            f = interp1d(old_indices, y, kind='linear', fill_value="extrapolate")
                            new_data[col] = f(new_indices)
                        elif method == "Nearest":
                            f = interp1d(old_indices, y, kind='nearest', fill_value="extrapolate")
                            new_data[col] = f(new_indices)
                        elif method == "Next":
                            f = interp1d(old_indices, y, kind='next', fill_value="extrapolate")
                            new_data[col] = f(new_indices)
                        elif method == "Previous":
                            f = interp1d(old_indices, y, kind='previous', fill_value="extrapolate")
                            new_data[col] = f(new_indices)
                        elif method == "Cubic":
                            f = interp1d(old_indices, y, kind='cubic', fill_value="extrapolate")
                            new_data[col] = f(new_indices)
                        elif method == "Spline":
                            # UnivariateSpline or CubicSpline
                            f = CubicSpline(old_indices, y)
                            new_data[col] = f(new_indices)
                        elif method == "PCHIP":
                            f = PchipInterpolator(old_indices, y)
                            new_data[col] = f(new_indices)
                        elif method == "Makima" or method == "V5Cubic":
                            # Akima for Makima (approx), CubicSpline for V5Cubic (approx)
                            if method == "Makima":
                                f = Akima1DInterpolator(old_indices, y)
                            else:
                                f = CubicSpline(old_indices, y)
                            new_data[col] = f(new_indices)
                        else:
                            # Default to Linear
                            new_data[col] = np.interp(new_indices, old_indices, y)
                            
                    except Exception as e:
                        # Fallback to Linear on error
                        print(f"Interpolation error ({method}): {e}, falling back to Linear")
                        new_data[col] = np.interp(new_indices, old_indices, result_df[col])
                else:
                    # Scipy 없으면 Linear 또는 Nearest만 가능 (Numpy)
                    if method == "Nearest":
                        # Nearest implementation using numpy
                        idx = np.abs(np.subtract.outer(new_indices, old_indices)).argmin(1)
                        new_data[col] = result_df[col].values[idx]
                    else:
                        # Default to Linear
                        new_data[col] = np.interp(new_indices, old_indices, result_df[col])
            
            result_df = pd.DataFrame(new_data)

        # 3. Downsampling (Ratio < 1)
        elif method in ["Average", "Max", "Min"]:
            if ratio >= 1:
                return result_df # Downsampling requires ratio < 1
            
            # 그룹 크기 계산 (예: ratio 0.1 -> 10개씩 묶음)
            group_size = int(1 / ratio)
            if group_size < 1: group_size = 1
            
            # 정수 인덱스 기반 그룹화
            # numeric_only=True는 groupby 메서드가 아니라 집계 함수(mean, max 등)에 전달해야 할 수도 있음
            # 하지만 위에서 이미 to_numeric으로 변환했으므로 안전함.
            grouped = result_df.groupby(np.arange(len(result_df)) // group_size)
            
            if method == "Average":
                result_df = grouped.mean()
            elif method == "Max":
                result_df = grouped.max()
            elif method == "Min":
                result_df = grouped.min()
                
        return result_df

    def preview_modification(self):
        """수정 결과 미리보기 (그래프에 빨간색 라인 표시)"""
        if self.df is None: return
        
        try:
            # 1. 파라미터 가져오기
            start_row = int(self.editRowStart.text())
            end_row = int(self.editRowEnd.text())
            
            # Method 텍스트 파싱
            method_text = self.comboMethod.currentText()
            method = method_text.split()[0]
            
            # Value 파싱 (기본 연산일 때만 필요하지만, 미리 파싱)
            try:
                value = float(self.editValue.text())
            except ValueError:
                value = 0.0
                
            ratio = getattr(self, 'conversion_ratio', 1.0)
            
            # 2. 선택된 컬럼 가져오기
            selected_cols = []
            if hasattr(self, 'column_checkboxes'):
                for chk in self.column_checkboxes:
                    if chk.isChecked():
                        selected_cols.append(chk.text())
            
            if not selected_cols:
                QMessageBox.warning(self, "Warning", "Please select at least one column.")
                return

            # 3. 데이터 서브셋 추출
            # 원본 데이터 전체 복사 (그래프 표시용)
            # 여기서는 첫 번째 선택된 컬럼만 그래프에 표시한다고 가정 (복잡도 감소)
            target_col = selected_cols[0]
            subset = self.df[target_col].iloc[start_row:end_row]
            
            # 4. 수정 로직 적용
            modified_subset = self.apply_modification(pd.DataFrame(subset), method, value, ratio)
            
            # 5. 그래프 업데이트 (빨간색 점선)
            # X축 계산: 원본 인덱스 위치에 맞춰서 표시
            # Upsampling/Downsampling의 경우 X축 간격이 달라짐
            
            # 원본 X축 범위
            x_start = start_row
            x_end = end_row
            
            # 수정된 데이터의 X축 생성
            modified_len = len(modified_subset)
            modified_x = np.linspace(x_start, x_end, modified_len)
            
            # 기존 미리보기 라인 제거
            for line in self.ax.lines:
                if line.get_label() == 'Preview':
                    line.remove()
            
            self.ax.plot(modified_x, modified_subset.iloc[:, 0], 'r--', label='Preview', linewidth=1.5)
            
            # 범례 업데이트
            handles, labels = self.ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), loc='upper left', facecolor='#2D2D30', edgecolor='#555555', labelcolor='white')
            
            self.canvas.draw()
            self.add_log(f"Preview: {method} on {target_col} ({start_row}~{end_row})")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Preview failed: {str(e)}")

    def execute_modification(self):
        """수정 사항 적용 (데이터프레임 업데이트)"""
        if self.df is None: return
        
        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to apply these changes permanently?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            # 1. 파라미터 가져오기
            start_row = int(self.editRowStart.text())
            end_row = int(self.editRowEnd.text())
            
            # Method 텍스트 파싱
            method_text = self.comboMethod.currentText()
            method = method_text.split()[0]
            
            try:
                value = float(self.editValue.text())
            except ValueError:
                value = 0.0
                
            ratio = getattr(self, 'conversion_ratio', 1.0)
            
            # 2. 선택된 컬럼
            selected_cols = []
            if hasattr(self, 'column_checkboxes'):
                for chk in self.column_checkboxes:
                    if chk.isChecked():
                        selected_cols.append(chk.text())
            
            # 3. 수정 적용
            # 주의: Upsampling/Downsampling은 행 개수가 바뀌므로 전체 DF 구조가 바뀔 수 있음
            # 여기서는 "선택된 구간만 교체"하는 것이 기본이지만, 
            # 길이가 바뀌면 Insert/Delete가 필요함.
            
            # 단순화를 위해: 길이가 바뀌는 연산(Up/Down)은 "전체 구간"에 대해서만 허용하거나,
            # 또는 해당 구간을 잘라내고 새 데이터를 끼워넣음.
            
            # 데이터 처리
            subset = self.df.iloc[start_row:end_row][selected_cols]
            
            modified_subset = self.apply_modification(subset, method, value, ratio)
            
            # 4. 데이터프레임 병합
            # 길이가 같은 경우 (Basic Ops)
            if len(modified_subset) == len(subset):
                # 선택된 컬럼만 업데이트
                for col in selected_cols:
                    self.df.loc[start_row:end_row-1, col] = modified_subset[col].values
            else:
                # 길이가 다른 경우 (Resampling) -> DataFrame 재구성 필요
                # Part 1: Start 이전
                df_start = self.df.iloc[:start_row]
                # Part 3: End 이후
                df_end = self.df.iloc[end_row:]
                
                # Part 2: Modified (선택되지 않은 컬럼은 어떻게? -> 보통 Resampling은 전체 Row에 영향)
                # 만약 특정 컬럼만 Resampling하면 다른 컬럼과 길이가 안 맞음 -> 에러 또는 NaN 채움
                # 여기서는 "선택된 컬럼만 수정"하되, 다른 컬럼은 해당 구간을 삭제하거나 보간해야 함.
                # 복잡성을 피하기 위해, Resampling 시에는 "다른 컬럼도 동일 비율로 처리"하거나 경고.
                
                # 전략: Resampling은 선택된 컬럼만 처리하고, 결과 DF는 선택된 컬럼만 남김 (또는 사용자에게 알림)
                # 여기서는 "선택된 컬럼만으로 새 DF 생성" + "나머지 컬럼은 버림" (가장 안전)
                # 또는 "전체 컬럼에 대해 동일 연산 적용" (사용자가 모든 컬럼 체크했다고 가정)
                
                # 개선: Resampling일 경우, 선택되지 않은 컬럼도 자동으로 동일한 방식(Linear/Average)으로 처리하여 길이를 맞춤.
                
                new_parts = []
                for col in self.df.columns:
                    col_data = self.df.iloc[start_row:end_row][[col]]
                    # 선택된 컬럼은 지정된 메서드로, 아니면 기본(Linear/Average)로 처리하여 길이 맞춤
                    if col in selected_cols:
                        mod_data = self.apply_modification(col_data, method, value, ratio)
                    else:
                        # 선택 안 된 컬럼도 길이를 맞춰야 함 (동기화)
                        sync_method = "Linear" if ratio > 1 else "Average"
                        mod_data = self.apply_modification(col_data, sync_method, value, ratio)
                    new_parts.append(mod_data.reset_index(drop=True))
                
                modified_middle = pd.concat(new_parts, axis=1)
                
                # 합치기
                self.df = pd.concat([df_start, modified_middle, df_end]).reset_index(drop=True)

            self.add_log(f"Executed: {method} on rows {start_row}~{end_row}")
            
            # UI 리프레시
            self.update_statistics()
            # 그래프 리프레시
            self.update_graph_from_selection()
            
            # Row End 업데이트 (길이가 변했을 수 있음)
            self.editRowEnd.setText(str(len(self.df)))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Execution failed: {str(e)}")

    def save_data(self):
        """데이터 저장"""
        if self.df is None: return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.df.to_excel(file_path, index=False)
                self.add_log(f"Saved to {file_path}")
                QMessageBox.information(self, "Success", "File saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Save failed: {str(e)}")

    def export_graph(self):
        """그래프 이미지로 내보내기"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Graph",
            "",
            "PNG Image (*.png);;PDF Document (*.pdf);;All Files (*)"
        )

        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='#1E1E1E')
            QMessageBox.information(self, "Export", f"Graph exported to:\n{file_path}")
            self.statusbar.showMessage("Graph exported successfully")

    def show_table_view(self):
        """테이블 뷰 다이얼로그 표시"""
        if self.df is not None:
            dialog = TableViewDialog(self, self.df.values, self.df.columns.tolist())
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Warning", "No data loaded.")

    def show_method_info(self):
        """수정 방법 설명 다이얼로그 표시"""
        dialog = MethodInfoDialog(self)
        dialog.exec_()


if __name__ == '__main__':
    # 테스트 실행
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
