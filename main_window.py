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
    QHeaderView, QDialogButtonBox, QLabel, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


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
        
        # 샘플 데이터 (실제로는 data 파라미터 사용)
        if headers is None:
            headers = ["Time_s", "Value_A", "Value_B"]
        
        if data is None:
            data = [
                ["0", "13.193", "0.061293"],
                ["1", "13.773", "0.367387"],
                ["2", "12.282", "0.816167"],
                ["3", "14.521", "0.234567"],
                ["4", "15.892", "0.456789"],
            ]
        
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
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

        # 추가 초기화
        self.setup_graph()
        self.setup_custom_unit_visibility()
        self.connect_signals()

        # 상태 표시줄 설정
        self.statusbar.showMessage("Ready. Loaded file: sensor_log_2025.csv (1000 rows, 3 columns)")

    def setup_graph(self):
        """Matplotlib 그래프 설정"""
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
        self.ax.set_xlabel("Time_m", color='#CCCCCC')
        self.ax.set_ylabel("Time_s", color='#CCCCCC')
        self.ax.tick_params(colors='#CCCCCC')
        self.ax.grid(True, alpha=0.3, color='#555555')
        
        # 스파인 색상
        for spine in self.ax.spines.values():
            spine.set_color('#555555')
        
        # 샘플 데이터 플롯
        x = np.linspace(0, 30, 100)
        y_original = x * 20
        y_modified = x * 15 + 50
        
        self.ax.plot(x, y_original, 'b-', label='Original (Time_s)', linewidth=2)
        self.ax.plot(x, y_modified, 'g-', label='Modified (Time_m)', linewidth=2)
        self.ax.legend(loc='upper left', facecolor='#2D2D30', edgecolor='#555555', labelcolor='white')
        
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
            self.editFilePath.setText(file_path)
            # TODO: 실제 파일 로드 후 행/열 수 업데이트
            self.lblFileInfo.setText("Loaded: 1000 rows, 3 columns")
            self.statusbar.showMessage(f"Ready. Loaded file: {file_path}")

    def show_table_view(self):
        """테이블 뷰 팝업 표시"""
        dialog = TableViewDialog(self)
        dialog.exec_()

    def show_method_info(self):
        """수정 방법 설명 팝업 표시"""
        dialog = MethodInfoDialog(self)
        dialog.exec_()

    def update_conversion_factor(self):
        """단위 변환 계수 업데이트"""
        # 단위를 초 단위로 변환하는 기준값
        unit_to_seconds = {
            '초': 1,
            '분': 60,
            '시간': 3600,
            '일': 86400
        }
        
        # Original 단위 계산
        original_text = self.comboOriginalUnit.currentText()
        if "Custom" in original_text:
            original_value = self.spinOriginalValue.value()
            original_base = self.comboOriginalBaseUnit.currentText()
            original_seconds = original_value * unit_to_seconds.get(original_base, 1)
        else:
            original_unit = original_text.split()[0]
            original_seconds = unit_to_seconds.get(original_unit, 1)
        
        # Target 단위 계산
        target_text = self.comboTargetUnit.currentText()
        if "Custom" in target_text:
            target_value = self.spinTargetValue.value()
            target_base = self.comboTargetBaseUnit.currentText()
            target_seconds = target_value * unit_to_seconds.get(target_base, 1)
        else:
            target_unit = target_text.split()[0]
            target_seconds = unit_to_seconds.get(target_unit, 1)
        
        # 변환 계수 계산
        if target_seconds != 0:
            factor = original_seconds / target_seconds
        else:
            factor = 1
        
        self.lblConversionFactor.setText(f"Conversion Factor: {factor:.7g}")

    def preview_selection(self):
        """데이터 선택 미리보기"""
        selected_cols = []
        if self.chkColumn1.isChecked():
            selected_cols.append(self.chkColumn1.text())
        if self.chkColumn2.isChecked():
            selected_cols.append(self.chkColumn2.text())
        if self.chkColumn3.isChecked():
            selected_cols.append(self.chkColumn3.text())
            
        start_row = self.editRowStart.text()
        end_row = self.editRowEnd.text()
        
        self.statusbar.showMessage(f"Selected columns: {selected_cols}, Rows: {start_row} to {end_row}")

    def on_method_changed(self, method):
        """수정 방법 변경 시 UI 업데이트"""
        # 구분선 항목은 선택 불가능하게 처리
        if method.startswith("---"):
            # 이전 선택으로 되돌리기 또는 첫 번째 항목 선택
            self.comboMethod.setCurrentIndex(0)
            return
        self.statusbar.showMessage(f"Method changed to: {method}")

    def preview_modification(self):
        """데이터 수정 미리보기"""
        method = self.comboMethod.currentText()
        value = self.editValue.text()
        self.statusbar.showMessage(f"Preview: {method} with value {value}")

    def execute_modification(self):
        """데이터 수정 실행"""
        method = self.comboMethod.currentText()
        value = self.editValue.text()

        # TODO: 실제 데이터 수정 로직 구현
        self.statusbar.showMessage(f"Executing: {method} with value {value}")
        QMessageBox.information(self, "Execute", f"Method: {method}\nValue: {value}")

    def save_data(self):
        """수정된 데이터 저장"""
        format_ext = self.comboFormat.currentText()
        
        file_filter = {
            ".xlsx": "Excel Files (*.xlsx)",
            ".csv": "CSV Files (*.csv)",
            ".txt": "Text Files (*.txt)"
        }.get(format_ext, "All Files (*)")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "",
            file_filter
        )

        if file_path:
            self.statusbar.showMessage(f"Saved: {file_path}")
            QMessageBox.information(self, "Save", f"Data saved to:\n{file_path}")

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


if __name__ == '__main__':
    # 테스트 실행
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
