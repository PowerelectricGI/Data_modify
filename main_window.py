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
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QAbstractTableModel
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QCheckBox,
    QVBoxLayout, QDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QLabel, QTextEdit,
    QGroupBox, QListWidget, QSizePolicy, QProgressDialog,
    QTabWidget, QTableView
)
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


class FileLoaderThread(QThread):
    """파일 로딩을 위한 백그라운드 스레드"""
    finished = pyqtSignal(object) # DataFrame
    error = pyqtSignal(str) # Error message

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            if self.file_path.endswith('.csv') or self.file_path.endswith('.txt'):
                df = pd.read_csv(self.file_path)
            elif self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
                df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format")
            
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))


class PandasModel(QAbstractTableModel):
    """Pandas DataFrame을 위한 Qt 모델 (고성능)"""
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                
                # Float formatting
                if isinstance(value, (float, np.floating)):
                    return f"{value:.4f}"
                return str(value)
            
            elif role == Qt.ForegroundRole:
                # Diff 컬럼 (마지막 컬럼)이고 값이 0이 아니면 빨간색 표시
                # 여기서는 컬럼 이름으로 체크하는 것이 안전함
                col_name = self._data.columns[index.column()]
                if col_name == "Diff":
                    value = self._data.iloc[index.row(), index.column()]
                    try:
                        if isinstance(value, (int, float, np.number)) and abs(value) > 1e-9:
                            return QColor("#FF0000")
                    except:
                        pass
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[col])
        return None


class TableViewDialog(QDialog):
    """데이터 테이블을 탭 형태로 보여주는 팝업 다이얼로그"""
    
    def __init__(self, parent=None, original_df=None, modified_df=None):
        super().__init__(parent)
        self.setWindowTitle("Full Data Table View")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        self.original_df = original_df
        self.modified_df = modified_df
        
        # 라이트 테마 스타일 (가독성 향상)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #000000;
            }
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F0F0F0;
                color: #000000;
                padding: 8px 20px;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom: 1px solid #FFFFFF;
                font-weight: bold;
            }
            QTableView {
                background-color: #FFFFFF;
                border: none;
                gridline-color: #DDDDDD;
                color: #000000;
                selection-background-color: #E6F7FF;
                selection-color: #000000;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                color: #000000;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #CCCCCC;
                border-right: 1px solid #CCCCCC;
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
        
        # 탭 위젯 생성
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tabs)
        
        # 탭 초기화 (데이터가 있을 경우)
        if self.original_df is not None and self.modified_df is not None:
            # 컬럼 목록 (Original 기준)
            self.columns = self.original_df.columns
            
            for col in self.columns:
                # 각 탭에 빈 QTableView 추가 (Lazy Loading을 위해)
                # 실제 모델 설정은 탭이 선택될 때 수행
                tab = QTableView()
                # 성능 최적화 설정
                tab.setAlternatingRowColors(False)
                # 헤더 설정
                tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
                self.tabs.addTab(tab, col)
            
            # 첫 번째 탭 로드
            if self.tabs.count() > 0:
                self.load_tab_data(0)
        
        # 닫기 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

    def on_tab_changed(self, index):
        """탭 변경 시 데이터 로드 (Lazy Loading)"""
        if index >= 0:
            self.load_tab_data(index)

    def load_tab_data(self, index):
        """특정 탭의 데이터를 로드"""
        table_view = self.tabs.widget(index)
        
        # 이미 모델이 설정된 경우 스킵
        if table_view.model() is not None:
            return
            
        col_name = self.tabs.tabText(index)
        
        try:
            orig_series = self.original_df[col_name]
            # Modified DF에 해당 컬럼이 있는지 확인
            if col_name in self.modified_df.columns:
                mod_series = self.modified_df[col_name]
            else:
                mod_series = None
            
            if mod_series is None:
                return
            
            # 길이 비교 및 최대 길이 계산
            len_orig = len(orig_series)
            len_mod = len(mod_series)
            max_len = max(len_orig, len_mod)
            
            # 통합 DataFrame 생성 (항상 Original, Modified, Diff 표시)
            # Series를 새로 생성하여 인덱스를 0부터 max_len까지 맞춤 (자동으로 NaN 채움)
            s_orig = pd.Series(orig_series.values, name='Original')
            s_mod = pd.Series(mod_series.values, name='Modified')
            
            display_df = pd.DataFrame({
                'Index': range(max_len),
                'Original': s_orig.reindex(range(max_len)),
                'Modified': s_mod.reindex(range(max_len))
            })
            
            # Diff 계산 (숫자형인 경우)
            if pd.api.types.is_numeric_dtype(display_df['Original']) and pd.api.types.is_numeric_dtype(display_df['Modified']):
                display_df['Diff'] = display_df['Modified'] - display_df['Original']
            else:
                display_df['Diff'] = 0 # 또는 NaN
            
            # 모델 설정
            model = PandasModel(display_df)
            table_view.setModel(model)
            
        except Exception as e:
            print(f"Error loading tab {col_name}: {e}")


class MethodInfoDialog(QDialog):
    """수정 방법 설명을 보여주는 팝업 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modification Methods Information")
        self.setMinimumSize(650, 600)
        self.resize(700, 650)
        
        # 라이트 테마 스타일 (가독성 향상)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 0;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                color: #000000;
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
            h2 { color: #005A9E; margin-top: 20px; margin-bottom: 10px; }
            h3 { color: #0078D4; margin-top: 15px; margin-bottom: 5px; }
            p { color: #000000; margin: 5px 0; line-height: 1.4; }
            .category { color: #D83B01; font-weight: bold; }
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
        if getattr(sys, 'frozen', False):
            # PyInstaller로 패키징된 경우
            application_path = sys._MEIPASS
        else:
            # 일반 Python 스크립트로 실행되는 경우
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        ui_path = os.path.join(application_path, 'main_window.ui')
        uic.loadUi(ui_path, self)

        # QMessageBox 및 공통 다이얼로그 스타일 적용 (Light Theme for Popups)
        # 기존 스타일시트에 추가
        current_style = self.styleSheet()
        popup_style = """
            QMessageBox {
                background-color: #FFFFFF;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #E0E0E0;
                color: #000000;
                border: 1px solid #AAAAAA;
                border-radius: 4px;
                padding: 4px 12px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #D0D0D0;
            }
            QMessageBox QPushButton:pressed {
                background-color: #B0B0B0;
            }
        """
        self.setStyleSheet(current_style + popup_style)

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
        
        # Copyright 추가
        # Copyright 추가
        self.copyright_label = QLabel("(c)2025. G.H.KIM All rights reserved.")
        self.copyright_label.setStyleSheet("color: white; font-weight: bold; margin-right: 20px; background-color: transparent;")
        self.statusBar().addPermanentWidget(self.copyright_label)
        
        self.lblFileInfo.setText("No file loaded")
        
        # Full Preview 데이터 저장용 변수
        self.latest_preview_data = None
        self.latest_preview_headers = None
        
        # Full Preview 버튼 추가 (UI 파일 로드 후)
        self.setup_full_preview_button()
        
        # Preview Results UI 설정 (Section 6)
        self.setup_preview_results_ui()

    def setup_full_preview_button(self):
        """Full Preview 버튼을 UI에 동적으로 추가"""
        # groupModificationPreview 찾기
        if hasattr(self, 'groupModificationPreview'):
            # 버튼 생성
            from PyQt5.QtWidgets import QPushButton
            self.btnFullPreview = QPushButton("🔍 Full Table View")
            self.btnFullPreview.setMinimumHeight(24)
            self.btnFullPreview.setStyleSheet("""
                QPushButton {
                    background-color: #3C3C3C;
                    color: #E0E0E0;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px 12px;
                }
                QPushButton:hover {
                    background-color: #505050;
                    border-color: #007ACC;
                }
            """)
            self.btnFullPreview.clicked.connect(self.show_full_preview)
            
            # previewTableLayout에 추가 (테이블 위에)
            if hasattr(self, 'previewTableLayout'):
                self.previewTableLayout.insertWidget(0, self.btnFullPreview)

    def setup_preview_results_ui(self):
        """Section 6. Preview Results의 Statistics Summary UI 설정"""
        # 1. Method Label 추가
        if hasattr(self, 'statsLayout'):
            self.lblPreviewMethod = QLabel("Method: -")
            self.lblPreviewMethod.setStyleSheet("color: #007ACC; font-weight: bold; margin-bottom: 5px;")
            self.statsLayout.insertWidget(0, self.lblPreviewMethod)
            
        # 2. Table 설정 (Section 6의 tableStats)
        if hasattr(self, 'tableStats'):
            # 컬럼 설정: Metric, Modified
            self.tableStats.setColumnCount(2)
            self.tableStats.setHorizontalHeaderLabels(["Metric", "Modified"])
            self.tableStats.verticalHeader().setVisible(False)
            
            # 초기화
            self.tableStats.setRowCount(4)
            metrics = ["Min", "Max", "Mean", "Std"]
            for i, metric in enumerate(metrics):
                self.tableStats.setItem(i, 0, QTableWidgetItem(metric))
                self.tableStats.setItem(i, 1, QTableWidgetItem("-"))
                
            # 스타일 및 크기 조정
            self.tableStats.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # 가로 길이 고정 제거 및 Expanding 설정
            self.tableStats.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
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
        
        self.tableQuickStats = QTableWidget(1, 4)
        self.tableQuickStats.setHorizontalHeaderLabels(["Min", "Max", "Avg", "Std"])
        self.tableQuickStats.setVerticalHeaderLabels(["Value"])
        self.tableQuickStats.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableQuickStats.verticalHeader().setVisible(False)
        # self.tableQuickStats.setFixedHeight(100) # Remove fixed height
        self.tableQuickStats.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableQuickStats.setStyleSheet("""
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
            self.tableQuickStats.setItem(0, col, QTableWidgetItem("-"))
            
        layout.addWidget(self.tableQuickStats, 1) # Stretch factor 1
        
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
        # ListWidget을 Expanding으로 설정하여 남은 공간 차지
        self.listLog.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.listLog, 1) # Stretch factor 1
        
        # GroupBox도 Expanding으로 설정
        self.groupStatsLog.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        # 4. 왼쪽 패널에 추가
        # 기존 Spacer 제거 (마지막 아이템이 Spacer라고 가정)
        count = self.leftPanelLayout.count()
        if count > 0:
            item = self.leftPanelLayout.itemAt(count - 1)
            if item.spacerItem():
                self.leftPanelLayout.removeItem(item)
                
        # GroupBox 추가 (Spacer가 제거되었으므로 마지막에 추가하면 됨)
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
            
        # 숫자형 컬럼 찾기 (Time 제외)
        numeric_cols = []
        for col in self.df.columns:
            if col.lower() != 'time' and pd.api.types.is_numeric_dtype(self.df[col]):
                numeric_cols.append(col)
        
        if numeric_cols:
            # 테이블 초기화 및 크기 설정
            self.tableQuickStats.setRowCount(len(numeric_cols))
            self.tableQuickStats.setVerticalHeaderLabels(numeric_cols)
            self.tableQuickStats.verticalHeader().setVisible(True) # 컬럼명 표시
            
            # 각 컬럼별 통계 계산 및 표시
            for i, col in enumerate(numeric_cols):
                stats = self.df[col].describe()
                self.tableQuickStats.setItem(i, 0, QTableWidgetItem(f"{stats['min']:.4g}"))
                self.tableQuickStats.setItem(i, 1, QTableWidgetItem(f"{stats['max']:.4g}"))
                self.tableQuickStats.setItem(i, 2, QTableWidgetItem(f"{stats['mean']:.4g}"))
                self.tableQuickStats.setItem(i, 3, QTableWidgetItem(f"{stats['std']:.4g}"))
            
            self.add_log(f"Stats updated for {len(numeric_cols)} columns")
        else:
            self.tableQuickStats.setRowCount(0)
            self.add_log("No numeric columns found for statistics.")

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
        """데이터 파일 로드 (Thread 사용)"""
        self.editFilePath.setText(file_path)
        self.add_log(f"Loading file: {os.path.basename(file_path)}...")
        
        # Progress Dialog 표시
        self.progress_dialog = QProgressDialog("Loading file...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowTitle("In progress") # 타이틀 변경
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0) # 즉시 표시
        self.progress_dialog.setMinimumWidth(400) # 가로 길이 늘림
        
        # QPalette를 사용하여 텍스트 색상 강제 설정 (Method 1)
        palette = QPalette()
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.ButtonText, Qt.black)
        self.progress_dialog.setPalette(palette)
        
        # 스타일 설정 (White background, Black text) (Method 2)
        self.progress_dialog.setStyleSheet("""
            QProgressDialog {
                background-color: #FFFFFF;
                color: #000000;
            }
            QProgressDialog QLabel {
                color: #000000;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                background-color: #E0E0E0;
                color: #000000;
                border: 1px solid #AAAAAA;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                text-align: center;
                color: #000000;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
            }
        """)
        
        self.progress_dialog.show()
        
        # 스레드 시작
        self.loader_thread = FileLoaderThread(file_path)
        self.loader_thread.finished.connect(self.on_load_finished)
        self.loader_thread.error.connect(self.on_load_error)
        self.loader_thread.start()

    def on_load_finished(self, df):
        """파일 로드 완료 시 호출"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        try:
            self.df = df
            self.file_path = self.loader_thread.file_path
            
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
            self.on_load_error(str(e))

    def on_load_error(self, error_msg):
        """파일 로드 실패 시 호출"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{error_msg}")
        self.add_log(f"Error loading file: {error_msg}")

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
        elif method in ["Linear", "Cubic", "Nearest", "Next", "Previous", "PCHIP", "V5Cubic", "Makima", "Spline", "ZeroFill"]:
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
                        elif method == "ZeroFill":
                            # 0으로 초기화
                            filled_data = np.zeros(new_length)
                            for i, val in enumerate(result_df[col].values):
                                new_idx = int(round(i * ratio))
                                if new_idx < new_length:
                                    filled_data[new_idx] = val
                            new_data[col] = filled_data
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
                    elif method == "ZeroFill":
                         # 0으로 초기화
                        filled_data = np.zeros(new_length)
                        for i, val in enumerate(result_df[col].values):
                            new_idx = int(round(i * ratio))
                            if new_idx < new_length:
                                filled_data[new_idx] = val
                        new_data[col] = filled_data
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
            grouped = result_df.groupby(np.arange(len(result_df)) // group_size)
            
            if method == "Average":
                result_df = grouped.mean()
            elif method == "Max":
                result_df = grouped.max()
            elif method == "Min":
                result_df = grouped.min()
                
        return result_df

    def preview_modification(self):
        """수정 결과 미리보기 (그래프 및 테이블 업데이트)"""
        if self.df is None: return
        
        try:
            # 1. 파라미터 가져오기
            start_row = int(self.editRowStart.text())
            end_row = int(self.editRowEnd.text())
            
            # Method 텍스트 파싱
            method_text = self.comboMethod.currentText()
            method = method_text.split()[0]
            
            # Value 파싱
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

            # 3. 기존 미리보기 라인 제거
            # 리스트를 복사해서 순회해야 삭제 시 문제 없음
            lines_to_remove = [line for line in self.ax.lines if line.get_label() == 'Preview']
            for line in lines_to_remove:
                line.remove()

            # 4. 각 컬럼별 수정 로직 적용 및 그래프 표시
            preview_data_list = [] # (col_name, modified_subset) 튜플 저장
            all_modified_values = [] # 통계 계산용
            
            # 원본 X축 범위
            x_start = start_row
            x_end = end_row
            
            for col in selected_cols:
                subset = self.df[col].iloc[start_row:end_row]
                
                # 수정 로직 적용
                modified_subset_df = self.apply_modification(pd.DataFrame(subset), method, value, ratio)
                modified_subset = modified_subset_df[col]
                
                # 그래프 업데이트
                modified_len = len(modified_subset)
                modified_x = np.linspace(x_start, x_end, modified_len)
                
                # 빨간색 점선으로 표시 (alpha값으로 겹침 표현)
                self.ax.plot(modified_x, modified_subset, 'r--', label='Preview', linewidth=1.5, alpha=0.7)
                
                # 데이터 저장 (테이블용)
                preview_data_list.append((col, modified_subset))
                all_modified_values.extend(modified_subset.values)

            # 범례 업데이트 (중복 제거)
            handles, labels = self.ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), loc='upper left', facecolor='#2D2D30', edgecolor='#555555', labelcolor='white')
            
            self.canvas.draw()
            
            # 5. 테이블 미리보기 업데이트 (모든 선택된 컬럼 표시)
            if hasattr(self, 'tablePreview') and preview_data_list:
                self.tablePreview.clear()
                
                # 헤더 설정 (선택된 모든 컬럼)
                headers = [item[0] for item in preview_data_list]
                self.tablePreview.setColumnCount(len(headers))
                self.tablePreview.setHorizontalHeaderLabels(headers)
                
                # 데이터 채우기 (최대 100행)
                # 첫 번째 컬럼 기준으로 행 수 결정 (모든 컬럼이 동일한 변환을 거치므로 길이는 같음)
                first_subset = preview_data_list[0][1]
                max_rows = min(len(first_subset), 100)
                self.tablePreview.setRowCount(max_rows)
                
                for i in range(max_rows):
                    for col_idx, (col_name, mod_subset) in enumerate(preview_data_list):
                        val = mod_subset.iloc[i]
                        self.tablePreview.setItem(i, col_idx, QTableWidgetItem(f"{val:.4f}"))
                        
                # 컬럼 너비 자동 조정 (Stretch) - 짤림 방지
                self.tablePreview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                
            # 6. Statistics Summary 업데이트 (Section 6)
            if hasattr(self, 'tableStats'):
                # Method Label 업데이트
                if hasattr(self, 'lblPreviewMethod'):
                    self.lblPreviewMethod.setText(f"Method: {method}")
                
                # 통계 계산 (전체 선택된 컬럼의 수정된 값 기준)
                if all_modified_values:
                    vals = np.array(all_modified_values)
                    stats = {
                        "Min": np.min(vals),
                        "Max": np.max(vals),
                        "Mean": np.mean(vals),
                        "Std": np.std(vals)
                    }
                    
                    # 테이블 업데이트
                    metrics = ["Min", "Max", "Mean", "Std"]
                    for i, metric in enumerate(metrics):
                        self.tableStats.setItem(i, 1, QTableWidgetItem(f"{stats[metric]:.4g}"))
            
            # Full Preview 데이터 준비 (전체 DataFrame)
            # get_modified_dataframe을 사용하여 전체 수정된 DF 생성
            self.latest_preview_original = self.df
            self.latest_preview_modified = self.get_modified_dataframe(
                self.df, method, value, ratio, start_row, end_row, selected_cols
            )
        
            self.add_log(f"Preview: {method} on {len(selected_cols)} columns ({start_row}~{end_row})")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Preview failed: {str(e)}")

    def show_full_preview(self):
        """전체 미리보기 데이터를 팝업으로 표시"""
        if hasattr(self, 'latest_preview_original') and hasattr(self, 'latest_preview_modified') and \
           self.latest_preview_original is not None and self.latest_preview_modified is not None:
            
            dialog = TableViewDialog(self, original_df=self.latest_preview_original, modified_df=self.latest_preview_modified)
            dialog.exec_()
        else:
            QMessageBox.information(self, "Info", "No preview data available. Please click 'Preview' first.")

    def get_modified_dataframe(self, df, method, value, ratio, start_row, end_row, selected_cols):
        """
        주어진 파라미터로 수정된 전체 데이터프레임을 생성하여 반환
        (Preview 및 Execute 공용 로직)
        """
        if df is None: return None
        
        # 복사본 생성
        result_df = df.copy()
        
        # 1. 데이터 서브셋 추출
        subset = result_df.iloc[start_row:end_row][selected_cols]
        
        # 2. 수정 로직 적용
        modified_subset = self.apply_modification(subset, method, value, ratio)
        
        # 3. 데이터프레임 병합
        # 길이가 같은 경우 (Basic Ops)
        if len(modified_subset) == len(subset):
            # 선택된 컬럼만 업데이트
            for col in selected_cols:
                # FutureWarning 방지: int 컬럼에 float 값을 넣을 때 발생하는 경고 해결
                # 만약 원본이 int이고 수정된 값이 float라면, 원본 컬럼을 float로 변환
                if pd.api.types.is_integer_dtype(result_df[col]) and pd.api.types.is_float_dtype(modified_subset[col]):
                    result_df[col] = result_df[col].astype(float)
                
                result_df.loc[start_row:end_row-1, col] = modified_subset[col].values
        else:
            # 길이가 다른 경우 (Resampling) -> DataFrame 재구성 필요
            # Part 1: Start 이전
            df_start = result_df.iloc[:start_row]
            # Part 3: End 이후
            df_end = result_df.iloc[end_row:]
            
            # Part 2: Modified Middle
            # 선택되지 않은 컬럼도 동기화 필요
            new_parts = []
            for col in result_df.columns:
                col_data = result_df.iloc[start_row:end_row][[col]]
                
                if col in selected_cols:
                    mod_data = self.apply_modification(col_data, method, value, ratio)
                else:
                    # 선택 안 된 컬럼도 길이를 맞춰야 함 (동기화)
                    # Upsampling 시 "ZeroFill" 사용 (선택 안된 데이터는 0으로 채움)
                    sync_method = "ZeroFill" if ratio > 1 else "Average"
                    mod_data = self.apply_modification(col_data, sync_method, value, ratio)
                
                # 여기서도 타입 변환이 필요할 수 있지만, concat 시 자동으로 처리됨 (보통)
                # 하지만 명시적으로 처리하는 것이 안전함
                new_parts.append(mod_data.reset_index(drop=True))
            
            modified_middle = pd.concat(new_parts, axis=1)
            
            # 합치기
            result_df = pd.concat([df_start, modified_middle, df_end]).reset_index(drop=True)
            
        return result_df

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
            
            # 3. 수정된 데이터프레임 생성 (Helper 사용)
            new_df = self.get_modified_dataframe(self.df, method, value, ratio, start_row, end_row, selected_cols)
            
            if new_df is not None:
                self.df = new_df
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
        
        # 선택된 포맷 가져오기
        selected_format = self.comboFormat.currentText() # .xlsx, .csv, .txt
        
        # 파일 필터 설정
        filter_str = ""
        if selected_format == ".xlsx":
            filter_str = "Excel Files (*.xlsx)"
        elif selected_format == ".csv":
            filter_str = "CSV Files (*.csv)"
        elif selected_format == ".txt":
            filter_str = "Text Files (*.txt)"
        else:
            filter_str = "All Files (*)"
            
        # 저장 대화상자 열기
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", filter_str
        )
        
        if file_path:
            try:
                # 확장자 강제 적용 (사용자가 입력하지 않은 경우)
                if not file_path.lower().endswith(selected_format.lower()):
                    file_path += selected_format
                
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.df.to_excel(file_path, index=False)
                elif file_path.endswith('.txt'):
                    # TXT는 CSV 형식(콤마 구분) 또는 TSV(탭 구분)로 저장 가능
                    # 여기서는 CSV와 동일하게 저장하되 확장자만 txt로 함
                    self.df.to_csv(file_path, index=False)
                    
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
