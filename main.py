"""
데이터 수정 프로그램 - 메인 엔트리 포인트
PyQt5 기반 GUI 애플리케이션

Author: Claude
Created: 2025-11-27
Version: 1.0.0
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from main_window import MainWindow


def main():
    """
    애플리케이션 메인 함수

    PyQt5 애플리케이션을 초기화하고 메인 윈도우를 표시합니다.
    """
    # Qt 애플리케이션 인스턴스 생성
    app = QApplication(sys.argv)

    # 애플리케이션 정보 설정
    app.setApplicationName("데이터 수정 프로그램")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Data Modification Tool")

    # High DPI 디스플레이 지원
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    # 이벤트 루프 시작
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
