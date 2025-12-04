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
    QGroupBox, QListWidget, QSizePolicy, QProgressBar,
    QWidget, QHBoxLayout, QPushButton, QTabWidget, QApplication, QSplashScreen,
    QComboBox, QLineEdit, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QIcon, QFont, QPixmap
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
    """데이터 테이블을 보여주는 팝업 다이얼로그 (탭 지원)"""
    
    def __init__(self, parent=None, data=None, headers=None, data_dict=None):
        """
        Args:
            data: Single table data (Legacy support)
            headers: Single table headers (Legacy support)
            data_dict: Dictionary {TabName: (Data, Headers)} for multiple tabs
        """
        super().__init__(parent)
        self.setWindowTitle("Data Table View")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # 다크 테마 스타일
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #AAAAAA;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3E3E42;
            }
            QTableWidget {
                background-color: #252526;
                border: none;
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
        
        # 탭 위젯 생성
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # 데이터 처리
        if data_dict:
            # 탭 모드
            for tab_name, (tab_data, tab_headers) in data_dict.items():
                self.add_tab(tab_name, tab_data, tab_headers)
        elif data is not None and headers is not None:
            # 레거시 모드 (단일 탭)
            self.add_tab("Data", data, headers)
            
        # 닫기 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)

    def add_tab(self, name, data, headers):
        """탭 추가 헬퍼 메서드"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setRowCount(len(data))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 데이터 채우기 (최대 1000행까지만 표시하여 성능 최적화)
        max_rows = min(len(data), 1000)
        for row in range(max_rows):
            for col, value in enumerate(data[row]):
                item = QTableWidgetItem(str(value))
                
                # Diff 컬럼 (헤더 이름으로 판단) 빨간색 처리
                if headers[col].endswith('_Diff'):
                    item.setForeground(QColor("#FF5555")) # 밝은 빨강 (다크 테마용)
                    
                table.setItem(row, col, item)
                
        self.tabs.addTab(table, name)




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
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)


class LoadingDialog(QDialog):
    """데이터 로딩 중 표시할 커스텀 다이얼로그 (검정 테마)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        # 스타일 설정 (검정 배경, 흰색 글자)
        self.setStyleSheet("""
            QDialog {
                background-color: black;
                border: 1px solid #333333;
            }
            QLabel {
                color: white;
                font-family: 'Segoe UI';
            }
            QProgressBar {
                border: 1px solid #333333;
                background-color: #1E1E1E;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 커스텀 타이틀바
        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: black; border-bottom: 1px solid #333333;")
        title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 0, 0)
        
        title_label = QLabel("In Progress")
        title_label.setStyleSheet("font-weight: bold;")
        title_layout.addWidget(title_label)
        
        layout.addWidget(title_bar)
        
        # 내용 영역
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        self.msg_label = QLabel("Loading data...\nPlease wait.")
        self.msg_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.msg_label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate mode
        content_layout.addWidget(self.progress)
        
        layout.addWidget(content_widget)

class DataLoader(QObject):
    """백그라운드 데이터 로딩을 위한 워커 클래스"""
    finished = pyqtSignal(object) # DataFrame or Exception
    
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
            self.finished.emit(e)


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

        # 아이콘 설정
        icon_path = os.path.join(os.path.dirname(__file__), 'ProgramIcon.ico')
        self.setWindowIcon(QIcon(icon_path))

        # UI 요소 크기 조정 (버튼 텍스트 잘림 방지)
        self.btnTableView.setMinimumWidth(120)
        self.btnTableView.setMaximumWidth(120)

        # 데이터 관련 변수 초기화
        self.df = None
        self.file_path = None
        self.preview_active = False # 프리뷰 활성화 상태 플래그

        # 추가 초기화
        self.setup_graph()
        self.setup_custom_unit_visibility()
        self.setup_time_ui() # 시간 컬럼 설정 UI 추가
        self.setup_stats_and_log_ui()  # 통계 및 로그 UI 추가
        self.setup_preview_ui() # 프리뷰 UI 추가
        self.connect_signals()

    def setup_preview_ui(self):
        """프리뷰 섹션에 Table View 버튼 추가"""
        # groupModificationPreview 레이아웃에 버튼 추가
        # 기존 레이아웃이 QVBoxLayout이므로, 버튼을 상단이나 하단에 추가
        # 여기서는 tablePreview 위에 버튼을 추가하기 위해 insertWidget 사용
        
        layout = self.groupModificationPreview.layout()
        
        # 버튼 생성
        self.btnPreviewTablePopup = QPushButton("📊 Table View (Popup)")
        self.btnPreviewTablePopup.setMinimumHeight(30)
        self.btnPreviewTablePopup.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #007ACC;
            }
        """)
        self.btnPreviewTablePopup.clicked.connect(self.show_preview_popup)
        
        # 레이아웃의 첫 번째 위치(테이블 위)에 추가
        layout.insertWidget(0, self.btnPreviewTablePopup)

    def show_preview_popup(self):
        """수정 전후 데이터를 비교하는 팝업 테이블 표시 (탭 방식)"""
        if self.df is None:
            self.show_custom_message_box("Warning", "Please load data first.", QMessageBox.Warning)
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
            
            # 2. 선택된 컬럼 가져오기
            selected_cols = []
            if hasattr(self, 'column_checkboxes'):
                for chk in self.column_checkboxes:
                    if chk.isChecked():
                        selected_cols.append(chk.text())
            
            if not selected_cols:
                self.show_custom_message_box("Warning", "Please select at least one column.", QMessageBox.Warning)
                return

            # 3. 데이터 준비 (탭별로 구성)
            tabs_data = {} # {TabName: (Data, Headers)}
            
            # 모든 컬럼에 대해 탭 생성
            for col in self.df.columns:
                # Original Data
                orig_subset = self.df[col].iloc[start_row:end_row].values
                
                # 데이터 구성
                col_data = {}
                
                # 기본적으로 Modified는 Origin과 동일하게 설정 (변경 없음)
                mod_values = orig_subset
                
                # Preview 활성화 상태이고, 현재 컬럼이 선택된 컬럼 중 하나일 때만 Modified 값 계산
                if self.preview_active and col in selected_cols:
                    mod_subset_df = self.apply_modification(pd.DataFrame(self.df[col].iloc[start_row:end_row]), method, value, ratio)
                    mod_values = mod_subset_df.iloc[:, 0].values
                
                # 데이터 타입 확인 (수치형인지)
                is_numeric = pd.api.types.is_numeric_dtype(self.df[col])
                
                # 길이 맞춤 (Resampling 대응)
                max_len = max(len(orig_subset), len(mod_values))
                
                # Index
                col_data['Index'] = range(max_len)
                
                # Origin Padding
                orig_padded = np.full(max_len, np.nan, dtype=object) # Object type to hold strings if needed
                orig_padded[:len(orig_subset)] = orig_subset
                col_data['Origin'] = orig_padded
                
                # Modified Padding
                mod_padded = np.full(max_len, np.nan, dtype=object)
                mod_padded[:len(mod_values)] = mod_values
                col_data['Modified'] = mod_padded
                
                # Diff (수치형이고 길이가 같을 때만)
                if is_numeric and len(orig_subset) == len(mod_values):
                    try:
                        col_data['Diff'] = mod_values - orig_subset
                    except:
                        col_data['Diff'] = np.zeros_like(orig_subset) # 계산 실패 시 0으로 채움
                elif is_numeric:
                     # 길이가 다르면 Diff 계산 불가 (Resampling 등) -> NaN 또는 0 처리?
                     # 여기서는 NaN으로 채움
                     col_data['Diff'] = np.full(max_len, np.nan)
                
                # DataFrame 생성
                comp_df = pd.DataFrame(col_data)
                
                # 탭 데이터 저장
                tabs_data[col] = (comp_df.values, comp_df.columns.tolist())

            # 팝업 표시
            dialog = TableViewDialog(self, data_dict=tabs_data)
            dialog.setWindowTitle("Modification Preview Table")
            dialog.resize(1000, 700)
            dialog.exec_()
            
        except Exception as e:
            self.show_custom_message_box("Error", f"Failed to show preview table: {str(e)}", QMessageBox.Critical)



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

    def setup_time_ui(self):
        """시간 컬럼 설정 UI 추가 (Code-behind)"""
        # 1. GroupBox 생성
        self.groupTimeConfig = QGroupBox("3. Time Column Settings")
        self.groupTimeConfig.setObjectName("sectionGroup")
        self.groupTimeConfig.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 1px solid white;
                border-radius: 0px;
                margin-top: 4px;
                padding: 4px;
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
                font-weight: normal;
                font-size: 10px;
            }
        """)
        
        layout = QVBoxLayout(self.groupTimeConfig)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 8, 4, 4)
        
        # 2. 시간 컬럼 존재 여부 체크박스
        self.chkTimeExists = QCheckBox("Time Column Exists")
        self.chkTimeExists.setChecked(False)
        self.chkTimeExists.stateChanged.connect(self.toggle_time_ui)
        layout.addWidget(self.chkTimeExists)
        
        # 3. 시간 컬럼 선택 콤보박스
        time_col_layout = QHBoxLayout()
        time_col_layout.setSpacing(4)
        time_col_layout.setContentsMargins(0, 0, 0, 0)
        time_col_layout.addWidget(QLabel("Column:"))
        self.comboTimeCol = QComboBox()
        self.comboTimeCol.setEnabled(False)
        time_col_layout.addWidget(self.comboTimeCol)
        layout.addLayout(time_col_layout)
        
        # 4. 날짜 포맷 입력
        format_layout = QHBoxLayout()
        format_layout.setSpacing(4)
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.addWidget(QLabel("Format:"))
        
        self.editDateFormat = QComboBox()
        self.editDateFormat.setEditable(True)
        
        # 날짜 포맷 매핑 (Display -> Python Format)
        self.dateFormatMap = {
            "yyyy-mm-dd HH:MM:SS": "%Y-%m-%d %H:%M:%S",
            "yyyy-mm-dd HH:MM": "%Y-%m-%d %H:%M",
            "yyyy-mm-dd": "%Y-%m-%d",
            "mm/dd/yyyy": "%m/%d/%Y",
            "dd/mm/yyyy": "%d/%m/%Y",
            "yyyy.mm.dd": "%Y.%m.%d",
            "HH:MM:SS": "%H:%M:%S"
        }
        self.editDateFormat.addItems(self.dateFormatMap.keys())
        self.editDateFormat.setEnabled(False)
        
        format_layout.addWidget(self.editDateFormat)
        layout.addLayout(format_layout)
        
        # 5. 추출할 컴포넌트 선택 (체크박스)
        components_label = QLabel("Extract Components:")
        layout.addWidget(components_label)
        
        comp_layout_1 = QHBoxLayout()
        comp_layout_1.setSpacing(4)
        comp_layout_1.setContentsMargins(0, 0, 0, 0)
        self.chkYear = QCheckBox("Year")
        self.chkMonth = QCheckBox("Month")
        self.chkDay = QCheckBox("Day")
        comp_layout_1.addWidget(self.chkYear)
        comp_layout_1.addWidget(self.chkMonth)
        comp_layout_1.addWidget(self.chkDay)
        layout.addLayout(comp_layout_1)
        
        comp_layout_2 = QHBoxLayout()
        comp_layout_2.setSpacing(4)
        comp_layout_2.setContentsMargins(0, 0, 0, 0)
        self.chkHour = QCheckBox("Hour")
        self.chkMinute = QCheckBox("Minute")
        self.chkSecond = QCheckBox("Second")
        comp_layout_2.addWidget(self.chkHour)
        comp_layout_2.addWidget(self.chkMinute)
        comp_layout_2.addWidget(self.chkSecond)
        layout.addLayout(comp_layout_2)
        
        # 초기 상태 설정
        for chk in [self.chkYear, self.chkMonth, self.chkDay, self.chkHour, self.chkMinute, self.chkSecond]:
            chk.setEnabled(False)
            
        # UI에 추가 (Unit Config 다음에 추가)
        # leftPanelLayout의 인덱스를 찾아서 삽입해야 함 (Unit Config가 1번 인덱스라고 가정)
        # 안전하게 groupUnitConfig 다음에 추가하기 위해 layout을 순회하거나 끝에 추가 후 이동
        
        # 현재 leftPanelLayout 구조:
        # 0: groupDataLoad
        # 1: groupUnitConfig
        # 2: groupDataRange
        # 3: groupModificationMethod
        
        # 2번 인덱스(groupDataRange 앞)에 삽입
        self.leftPanelLayout.insertWidget(2, self.groupTimeConfig)

    def toggle_time_ui(self, state):
        """시간 설정 UI 활성화/비활성화 토글"""
        enabled = (state == Qt.Checked)
        self.comboTimeCol.setEnabled(enabled)
        self.editDateFormat.setEnabled(enabled)
        for chk in [self.chkYear, self.chkMonth, self.chkDay, self.chkHour, self.chkMinute, self.chkSecond]:
            chk.setEnabled(enabled)

    def setup_stats_and_log_ui(self):
        """통계 및 로그 섹션 UI 추가 (Code-behind)"""
        # 1. GroupBox 생성 - 하얀색 실선 테두리 스타일
        self.groupStatsLog = QGroupBox("6. Statistics & Log")
        self.groupStatsLog.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 1px solid white;
                border-radius: 0px;
                margin-top: 4px;
                padding: 4px;
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
                font-size: 10px;
                font-weight: normal;
            }
        """)
        
        # 세로로 늘어나도록 설정
        self.groupStatsLog.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self.groupStatsLog)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 8, 4, 4)
        
        # 2. 통계 테이블 (Min, Max, Avg, Std)
        stats_label = QLabel("📊 Quick Statistics")
        stats_label.setStyleSheet("color: white; font-weight: normal; margin-bottom: 3px; font-size: 11px;")
        layout.addWidget(stats_label)
        
        self.tableQuickStats = QTableWidget(0, 5)
        self.tableQuickStats.setHorizontalHeaderLabels(["Column", "Min", "Max", "Avg", "Std"])
        self.tableQuickStats.verticalHeader().setVisible(False)
        header = self.tableQuickStats.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Column Name은 내용에 맞게
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
            
        layout.addWidget(self.tableQuickStats, 1) # Stretch 1
        
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
        self.listLog.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.listLog.addItem("Ready. System initialized.")
        layout.addWidget(self.listLog, 1) # Stretch 1
        
        # 4. 왼쪽 패널에 추가 (Spacer 제거 후 추가)
        # 기존 Spacer 제거하여 GroupBox가 남은 공간을 차지하도록 함
        count = self.leftPanelLayout.count()
        if count > 0:
            # 마지막 아이템(Spacer) 제거
            item = self.leftPanelLayout.takeAt(count - 1)
            if item.widget():
                # 만약 위젯이라면 다시 넣어줌 (Spacer가 아닐 경우 대비)
                self.leftPanelLayout.addWidget(item.widget())
                
        self.leftPanelLayout.addWidget(self.groupStatsLog)

    def connect_signals(self):
        """시그널-슬롯 연결"""
        # 버튼 연결
        self.btnLoadFile.clicked.connect(self.browse_file)
        self.btnTableView.clicked.connect(self.show_preview_popup)
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
        print(f"[LOG] {message}") # Console output for debugging
        self.listLog.addItem(message)
        self.listLog.scrollToBottom()
        self.statusbar.showMessage(message)

    def show_custom_message_box(self, title, message, icon_type=QMessageBox.Warning):
        """Dark Theme 적용된 커스텀 메시지 박스 표시"""
        msg = QMessageBox(self)
        msg.setIcon(icon_type)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
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
        msg.exec_()

    def create_loading_dialog(self, message):
        """저장 중 로딩 다이얼로그 생성"""
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                border: 1px solid #3C3C3C;
                border-radius: 8px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        return dialog

    def update_statistics(self):
        """현재 데이터의 통계 업데이트"""
        if self.df is None:
            return
            
        # 기존 테이블 초기화
        self.tableQuickStats.setRowCount(0)
        
        numeric_cols = []
        for col in self.df.columns:
            # Time 컬럼 제외하고 숫자형 컬럼 찾기
            if col.lower() != 'time' and pd.api.types.is_numeric_dtype(self.df[col]):
                numeric_cols.append(col)
        
        if not numeric_cols:
            return

        self.tableQuickStats.setRowCount(len(numeric_cols))
        
        for i, col in enumerate(numeric_cols):
            stats = self.df[col].describe()
            
            # Column Name
            self.tableQuickStats.setItem(i, 0, QTableWidgetItem(str(col)))
            # Stats
            self.tableQuickStats.setItem(i, 1, QTableWidgetItem(f"{stats['min']:.4g}"))
            self.tableQuickStats.setItem(i, 2, QTableWidgetItem(f"{stats['max']:.4g}"))
            self.tableQuickStats.setItem(i, 3, QTableWidgetItem(f"{stats['mean']:.4g}"))
            self.tableQuickStats.setItem(i, 4, QTableWidgetItem(f"{stats['std']:.4g}"))
            
        self.add_log(f"Stats updated for {len(numeric_cols)} columns")

    def update_summary_table(self, original_df, modified_df):
        """Statistics Summary 테이블 업데이트 (Original vs Modified)"""
        # .ui 파일에 정의된 tableStats 사용
        if not hasattr(self, 'tableStats'): return
        
        # 테이블 초기화
        self.tableStats.setRowCount(0)
        self.tableStats.setColumnCount(3)
        self.tableStats.setHorizontalHeaderLabels(["Metric", "Original", "Modified"])
        
        # 비교할 컬럼들 (수치형만)
        cols = [c for c in modified_df.columns if pd.api.types.is_numeric_dtype(modified_df[c])]
        
        if not cols: return
        
        # 행 추가
        row_idx = 0
        for col in cols:
            # Original Stats
            if col in original_df.columns:
                orig_stats = original_df[col].describe()
            else:
                orig_stats = None
                
            # Modified Stats
            mod_stats = modified_df[col].describe()
            
            # Metrics to show
            metrics = ['min', 'max', 'mean', 'std']
            metric_names = ['Min', 'Max', 'Avg', 'Std']
            
            # Header Row for Column Name (if multiple columns)
            if len(cols) > 1:
                self.tableStats.insertRow(row_idx)
                self.tableStats.setItem(row_idx, 0, QTableWidgetItem(f"--- {col} ---"))
                self.tableStats.setSpan(row_idx, 0, 1, 3) # Span across 3 columns
                # Style for header row
                for c in range(3):
                    item = self.tableStats.item(row_idx, c)
                    if item:
                        item.setBackground(QColor("#333337"))
                        item.setForeground(QColor("#00CED1"))
                row_idx += 1
            
            for m, m_name in zip(metrics, metric_names):
                self.tableStats.insertRow(row_idx)
                
                # Metric Name
                self.tableStats.setItem(row_idx, 0, QTableWidgetItem(m_name))
                
                # Original Value
                if orig_stats is not None:
                    self.tableStats.setItem(row_idx, 1, QTableWidgetItem(f"{orig_stats[m]:.4g}"))
                else:
                    self.tableStats.setItem(row_idx, 1, QTableWidgetItem("-"))
                    
                # Modified Value
                self.tableStats.setItem(row_idx, 2, QTableWidgetItem(f"{mod_stats[m]:.4g}"))
                
                # Highlight differences
                if orig_stats is not None and abs(orig_stats[m] - mod_stats[m]) > 1e-9:
                     self.tableStats.item(row_idx, 2).setForeground(QColor("#FF5555")) # Red for changed values
                
                row_idx += 1
                
        self.tableStats.resizeColumnsToContents()

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
        """데이터 파일 로드 (Threaded)"""
        self.editFilePath.setText(file_path)
        self.add_log(f"Loading file: {os.path.basename(file_path)}...")
        
        # 로딩 다이얼로그 표시
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        
        # 스레드 설정
        self.thread = QThread()
        self.worker = DataLoader(file_path)
        self.worker.moveToThread(self.thread)
        
        # 시그널 연결
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # 스레드 시작
        self.thread.start()

    def on_data_loaded(self, result):
        """데이터 로드 완료 시 콜백"""
        # 다이얼로그 닫기
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
            
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(result)}")
            self.add_log(f"Error loading file: {str(result)}")
            return
            
        # 정상 로드
        try:
            self.df = result
            self.file_path = self.editFilePath.text()
            
            # UI 업데이트
            rows, cols = self.df.shape
            self.lblFileInfo.setText(f"Loaded: {rows} rows, {cols} columns")
            self.add_log(f"Successfully loaded {rows} rows, {cols} columns.")
            
            # Row Range 초기화
            self.editRowStart.setText("0")
            self.editRowEnd.setText(str(rows))
            
            # Column Checkbox 동적 생성
            # Column Checkbox 동적 생성
            # 기존 체크박스 제거 (Label 제외하고 모두 제거)
            while self.columnSelectLayout.count() > 1: 
                item = self.columnSelectLayout.takeAt(1)
                if item.widget():
                    item.widget().deleteLater()
            
            # ScrollArea 생성 (체크박스들을 담을 컨테이너)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea { border: none; background-color: transparent; }
                QWidget { background-color: transparent; }
                QScrollBar:vertical { width: 10px; }
            """)
            
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setContentsMargins(0, 0, 0, 0)
            scroll_layout.setSpacing(4)
            
            self.column_checkboxes = []
            for col in self.df.columns:
                chk = QCheckBox(col)
                chk.setChecked(True) # 기본적으로 모두 선택
                chk.setStyleSheet("color: #E0E0E0;")
                chk.stateChanged.connect(self.update_graph_from_selection) # 이벤트 연결
                scroll_layout.addWidget(chk)
                self.column_checkboxes.append(chk)
            
            scroll_layout.addStretch() # 위로 정렬
            scroll.setWidget(scroll_content)
            
            # Layout에 ScrollArea 추가
            self.columnSelectLayout.addWidget(scroll)
            
            # 통계 업데이트
            self.update_statistics()
            
            # 시간 컬럼 콤보박스 업데이트
            self.comboTimeCol.clear()
            self.comboTimeCol.addItems(self.df.columns)
            
            # 시간 컬럼 자동 감지 (time, date 포함된 컬럼)
            time_col_found = False
            for i, col in enumerate(self.df.columns):
                if 'time' in col.lower() or 'date' in col.lower():
                    self.comboTimeCol.setCurrentIndex(i)
                    self.chkTimeExists.setChecked(True)
                    time_col_found = True
                    break
            
            if not time_col_found:
                self.chkTimeExists.setChecked(False)
            
            # 그래프 초기화
            self.update_graph_from_selection()
            
            # 데이터 로드 완료 시 Preview 플래그 초기화
            self.preview_active = False
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating UI:\n{str(e)}")
            self.add_log(f"Error updating UI: {str(e)}")

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

            # 기존 미리보기 라인 제거
            for line in self.ax.lines[:]:  # Copy list to avoid modification issues during iteration
                if line.get_label() == 'Preview':
                    line.remove()

            # 3. 각 선택된 컬럼에 대해 루프 실행
            modified_data_dict = {} # Preview Table용 데이터 저장
            
            for target_col in selected_cols:
                # 데이터 서브셋 추출
                subset = self.df[target_col].iloc[start_row:end_row]
                
                # 4. 수정 로직 적용
                modified_subset = self.apply_modification(pd.DataFrame(subset), method, value, ratio)
                
                # 결과 저장 (Series로 변환)
                modified_data_dict[target_col] = modified_subset.iloc[:, 0].values
                
                # 5. 그래프 업데이트 (빨간색 점선)
                # X축 계산: 원본 인덱스 위치에 맞춰서 표시
                
                # 원본 X축 범위
                x_start = start_row
                x_end = end_row
                
                # 수정된 데이터의 X축 생성
                modified_len = len(modified_subset)
                modified_x = np.linspace(x_start, x_end, modified_len)
                
                self.ax.plot(modified_x, modified_subset.iloc[:, 0], 'r--', label='Preview', linewidth=1.5)
            
            # 범례 업데이트 (중복 방지)
            handles, labels = self.ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self.ax.legend(by_label.values(), by_label.keys(), loc='upper left', facecolor='#2D2D30', edgecolor='#555555', labelcolor='white')
            
            self.canvas.draw()
            
            # Preview 활성화 플래그 설정
            self.preview_active = True
            
            self.add_log(f"Preview: {method} on {len(selected_cols)} columns ({start_row}~{end_row})")
            
            # ==========================================
            # Preview Table 업데이트
            # ==========================================
            if modified_data_dict:
                # 최대 길이 계산
                max_len = max(len(v) for v in modified_data_dict.values())
                display_rows = min(max_len, 1000) # 최대 1000행까지만 표시
                
                # 테이블 설정
                self.tablePreview.setColumnCount(1 + len(selected_cols))
                self.tablePreview.setRowCount(display_rows)
                self.tablePreview.setHorizontalHeaderLabels(["Index"] + selected_cols)
                
                # 데이터 채우기
                for row in range(display_rows):
                    # Index
                    self.tablePreview.setItem(row, 0, QTableWidgetItem(str(row)))
                    
                    # Values
                    for i, col in enumerate(selected_cols):
                        vals = modified_data_dict[col]
                        if row < len(vals):
                            self.tablePreview.setItem(row, i + 1, QTableWidgetItem(f"{vals[row]:.4f}"))
                        else:
                            self.tablePreview.setItem(row, i + 1, QTableWidgetItem(""))
                            
                # ==========================================
                # Statistics Summary 업데이트 (Preview)
                # ==========================================
                # Original Subset
                original_subset = self.df.iloc[start_row:end_row][selected_cols]
                
                # Modified Subset (Construct from dict)
                # 모든 컬럼의 길이가 같다고 가정 (같은 Method/Ratio 적용)
                modified_subset_df = pd.DataFrame(modified_data_dict)
                
                self.update_summary_table(original_subset, modified_subset_df)
                
                # GroupBox Title 업데이트
                if hasattr(self, 'groupStatistics'):
                    self.groupStatistics.setTitle(f"Statistics Summary - {method} (Preview)")
                            
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
            
            # Statistics Summary 업데이트 (Original vs Modified)
            self.update_summary_table(subset, modified_subset)
            
            # GroupBox Title 업데이트 (Method 표시)
            if hasattr(self, 'groupStatistics'):
                self.groupStatistics.setTitle(f"Statistics Summary - {method}")
            
            # Preview Table용 데이터 수집
            preview_data = {}
            
            # 4. 데이터프레임 병합
            # 길이가 같은 경우 (Basic Ops)
            if len(modified_subset) == len(subset):
                # 선택된 컬럼만 업데이트
                for col in selected_cols:
                    self.df.loc[start_row:end_row-1, col] = modified_subset[col].values
                    preview_data[col] = modified_subset[col].values
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
                        preview_data[col] = mod_data.iloc[:, 0].values # Preview용 저장
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
            
            # Preview 플래그 초기화 (실행 완료했으므로)
            self.preview_active = False
            
            # Row End 업데이트 (길이가 변했을 수 있음)
            self.editRowEnd.setText(str(len(self.df)))
            
            # ==========================================
            # Preview Table 업데이트 (실행 결과 표시)
            # ==========================================
            if preview_data:
                # 최대 길이 계산
                max_len = max(len(v) for v in preview_data.values())
                display_rows = min(max_len, 1000) # 최대 1000행까지만 표시
                
                # 테이블 설정
                self.tablePreview.setColumnCount(1 + len(selected_cols))
                self.tablePreview.setRowCount(display_rows)
                self.tablePreview.setHorizontalHeaderLabels(["Index"] + selected_cols)
                
                # 데이터 채우기
                for row in range(display_rows):
                    # Index
                    self.tablePreview.setItem(row, 0, QTableWidgetItem(str(row)))
                    
                    # Values
                    for i, col in enumerate(selected_cols):
                        if col in preview_data:
                            vals = preview_data[col]
                            if row < len(vals):
                                self.tablePreview.setItem(row, i + 1, QTableWidgetItem(f"{vals[row]:.4f}"))
                            else:
                                self.tablePreview.setItem(row, i + 1, QTableWidgetItem(""))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Execution failed: {str(e)}")

    def process_time_column(self):
        """시간 컬럼 처리 및 추출"""
        if self.df is None: return None
        
        # 복사본 생성
        df_to_save = self.df.copy()
        
        # 시간 컬럼 설정이 활성화되어 있고 체크되어 있는지 확인
        if self.chkTimeExists.isChecked():
            try:
                time_col = self.comboTimeCol.currentText()
                
                # 포맷 매핑 확인 (사용자 입력이 매핑에 있으면 변환, 없으면 그대로 사용)
                raw_format = self.editDateFormat.currentText()
                
                # 1. 매핑 테이블 확인
                if raw_format in self.dateFormatMap:
                    date_format = self.dateFormatMap[raw_format]
                else:
                    # 2. 매핑에 없으면 동적 변환 시도 (Excel Style -> Python Style)
                    # yyyy -> %Y, mm -> %m, dd -> %d, HH -> %H, MM -> %M, SS -> %S
                    # 주의: mm(월)과 MM(분) 구분 필요. 
                    # 사용자가 입력한 문자열을 순차적으로 변환
                    converted = raw_format
                    converted = converted.replace("yyyy", "%Y")
                    converted = converted.replace("yy", "%y")
                    converted = converted.replace("mm", "%m")
                    converted = converted.replace("dd", "%d")
                    converted = converted.replace("HH", "%H")
                    converted = converted.replace("MM", "%M")
                    converted = converted.replace("SS", "%S")
                    date_format = converted
                    
                    self.add_log(f"Custom format conversion: '{raw_format}' -> '{date_format}'")
                
                # 날짜 변환
                if time_col in df_to_save.columns:
                    # Debug Logging
                    sample_data = df_to_save[time_col].head(5).tolist()
                    self.add_log(f"Debug: Time Column '{time_col}' Sample: {sample_data}")
                    self.add_log(f"Debug: Using Format: '{date_format}'")
                    
                    # pd.to_datetime은 포맷이 안 맞으면 에러 발생 가능
                    # errors='coerce'로 하면 변환 실패 시 NaT 반환
                    series_datetime = pd.to_datetime(df_to_save[time_col], format=date_format, errors='coerce')
                    
                    # Fallback: If all NaT, try auto-detection
                    if series_datetime.isna().all():
                        self.add_log(f"Warning: Strict format '{date_format}' failed. Attempting auto-detection...")
                        series_datetime = pd.to_datetime(df_to_save[time_col], errors='coerce')
                    
                    # Debug Result
                    sample_result = series_datetime.head(5).tolist()
                    self.add_log(f"Debug: Converted Sample: {sample_result}")
                    
                    # 추출할 컴포넌트
                    components = []
                    if self.chkYear.isChecked(): components.append(('Year', series_datetime.dt.year))
                    if self.chkMonth.isChecked(): components.append(('Month', series_datetime.dt.month))
                    if self.chkDay.isChecked(): components.append(('Day', series_datetime.dt.day))
                    if self.chkHour.isChecked(): components.append(('Hour', series_datetime.dt.hour))
                    if self.chkMinute.isChecked(): components.append(('Minute', series_datetime.dt.minute))
                    if self.chkSecond.isChecked(): components.append(('Second', series_datetime.dt.second))
                    
                    # 새 컬럼들을 DataFrame 앞에 추가
                    # insert 메서드를 사용하여 0번 인덱스부터 차례로 추가 (역순으로 추가해야 순서 유지됨? 아니면 리스트 만들어서 concat)
                    # concat이 깔끔함
                    
                    new_cols_df = pd.DataFrame()
                    for name, series in components:
                        new_cols_df[name] = series
                        
                    # 기존 데이터와 합치기 (새 컬럼들을 앞으로)
                    df_to_save = pd.concat([new_cols_df, df_to_save], axis=1)
                    
            except Exception as e:
                # 변환 실패 시 경고 로그 남기고 원본 저장
                self.add_log(f"Warning: Failed to process time column. {str(e)}")
                # 사용자에게 알림 (선택 사항)
                
        return df_to_save

    def save_data(self):
        """데이터 저장"""
        if self.df is None: return
        
        # 선택된 포맷 가져오기
        selected_format = self.comboFormat.currentText()
        
        # 필터 문자열 구성 (선택된 포맷을 가장 앞에 배치)
        filters = {
            ".csv": "CSV Files (*.csv)",
            ".xlsx": "Excel Files (*.xlsx)",
            ".txt": "Text Files (*.txt)"
        }
        
        default_filter = filters.get(selected_format, "CSV Files (*.csv)")
        remaining_filters = [f for k, f in filters.items() if k != selected_format]
        filter_str = f"{default_filter};;" + ";;".join(remaining_filters)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "", filter_str
        )
        
        if file_path:
            # 로딩 다이얼로그 표시
            loading_dialog = self.create_loading_dialog("Saving data... Please wait.")
            loading_dialog.show()
            QApplication.processEvents()
            
            try:
                # 시간 컬럼 처리된 데이터프레임 가져오기
                df_final = self.process_time_column()
                if df_final is None: df_final = self.df
                
                if file_path.endswith('.csv'):
                    df_final.to_csv(file_path, index=False, encoding='utf-8-sig')
                elif file_path.endswith('.xlsx'):
                    df_final.to_excel(file_path, index=False)
                elif file_path.endswith('.txt'):
                    df_final.to_csv(file_path, index=False, sep='\t', encoding='utf-8-sig') # 탭 구분자로 저장
                
                loading_dialog.close()
                self.add_log(f"Saved to {file_path}")
                self.show_custom_message_box("Success", "File saved successfully.", QMessageBox.Information)
            except Exception as e:
                loading_dialog.close()
                self.show_custom_message_box("Error", f"Save failed: {str(e)}", QMessageBox.Critical)

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
    # High DPI 디스플레이 지원
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    
    # 스플래시 화면 표시
    icon_path = os.path.join(os.path.dirname(__file__), 'ProgramIcon.png')
    if os.path.exists(icon_path):
        splash_pix = QPixmap(icon_path)
        splash_pix = splash_pix.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
    else:
        splash = None

    window = MainWindow()
    window.show()
    
    if splash:
        splash.finish(window)
        
    sys.exit(app.exec_())
