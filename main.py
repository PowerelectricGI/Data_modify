"""
데이터 수정 프로그램 - 메인 엔트리 포인트
PyQt5 기반 GUI 애플리케이션 (SCADA Style)

Author: Claude
Created: 2025-11-27
Version: 1.0.0
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from main_window import MainWindow


def main():
    """
    애플리케이션 메인 함수

    PyQt5 애플리케이션을 초기화하고 메인 윈도우를 표시합니다.
    """
    # High DPI 디스플레이 지원 (app 생성 전에 설정)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Qt 애플리케이션 인스턴스 생성
    app = QApplication(sys.argv)

    # 스플래시 화면 표시
    icon_path = os.path.join(os.path.dirname(__file__), 'ProgramIcon.png')
    splash_pix = QPixmap(icon_path)
    # 이미지 크기 조정 (예: 500x500)
    splash_pix = splash_pix.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    # 애플리케이션 정보 설정
    app.setApplicationName("Data Modification Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Data Modification Tool")

    # 기본 폰트 설정
    default_font = QFont("Segoe UI", 9)
    app.setFont(default_font)

    # 메인 윈도우 생성 및 표시
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 스플래시 화면 종료
    splash.finish(window)

    # 이벤트 루프 시작
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
