"""Modern Qt application styling service."""


class ModernStyleService:
    """Apply the shared modern Fusion/QSS style across the application."""

    @staticmethod
    def apply_modern_style(app, qt_widgets, qt_gui, background_image_path=None):
        """Apply a sleek, modern style across the app. Optional background image."""
        qt_widgets.QApplication.setStyle("Fusion")

        palette = qt_gui.QPalette()
        base = qt_gui.QColor(37, 37, 38)
        panel = qt_gui.QColor(45, 45, 48)
        text = qt_gui.QColor(220, 220, 220)
        highlight = qt_gui.QColor(14, 122, 254)
        disabled = qt_gui.QColor(127, 127, 127)

        palette.setColor(qt_gui.QPalette.ColorRole.Window, panel)
        palette.setColor(qt_gui.QPalette.ColorRole.WindowText, text)
        palette.setColor(qt_gui.QPalette.ColorRole.Base, base)
        palette.setColor(qt_gui.QPalette.ColorRole.AlternateBase, panel)
        palette.setColor(qt_gui.QPalette.ColorRole.ToolTipBase, panel)
        palette.setColor(qt_gui.QPalette.ColorRole.ToolTipText, text)
        palette.setColor(qt_gui.QPalette.ColorRole.Text, text)
        palette.setColor(qt_gui.QPalette.ColorRole.Button, panel)
        palette.setColor(qt_gui.QPalette.ColorRole.ButtonText, text)
        palette.setColor(qt_gui.QPalette.ColorRole.Highlight, highlight)
        palette.setColor(qt_gui.QPalette.ColorRole.HighlightedText, qt_gui.QColor(255, 255, 255))
        palette.setColor(qt_gui.QPalette.ColorGroup.Disabled, qt_gui.QPalette.ColorRole.Text, disabled)
        palette.setColor(qt_gui.QPalette.ColorGroup.Disabled, qt_gui.QPalette.ColorRole.ButtonText, disabled)
        app.setPalette(palette)

        bg_image_rule = (
            f"border-image: url('{background_image_path}') 0 0 0 0 stretch stretch;"
            if background_image_path else ""
        )
        popup_image_rule = (
            f"background-image: url('{background_image_path}');"
            f"background-position: center;"
            f"background-attachment: fixed;"
            if background_image_path else "background-image: none;"
        )
        qss = f"""
        QMainWindow {{
            background-color: {panel.name()};
            color: {text.name()};
        }}
        QWidget {{
            background-color: {panel.name()};
            color: {text.name()};
        }}
        #centralWidget {{
            {bg_image_rule}
            background-color: {panel.name()};
        }}

        QDialog, QMessageBox, QProgressDialog {{
            {popup_image_rule}
            background-color: {panel.name()};
            color: {text.name()};
        }}

        QWidget[popupBg="true"] {{
            {popup_image_rule}
            background-color: {panel.name()};
            color: {panel.name()};
        }}
        QWidget[popupBg="true"] QLabel {{
            background-color: transparent;
            color: {panel.name()};
        }}
        QLabel{{
            background-color: transparent;
            color: {panel.name()};
        }}

        QMenuBar {{ background-color: {panel.name()}; border: none; }}
        QMenuBar::item {{ padding: 6px 10px; background: transparent; }}
        QMenuBar::item:selected {{ background: rgba(255,255,255,0.06); border-radius: 4px; }}

        QMenu {{ background-color: {panel.name()}; border: 1px solid rgba(255,255,255,0.08); }}
        QMenu::item {{ padding: 6px 12px; }}
        QMenu::item:selected {{ background: rgba(255,255,255,0.08); }}

        QScrollArea {{ border: none; background: transparent; }}
        QScrollArea > QWidget > QWidget {{ background: transparent; }}
        QScrollBar:vertical {{ background: transparent; width: 10px; }}
        QScrollBar::handle:vertical {{ background: rgba(255,255,255,0.18); border-radius: 5px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: rgba(255,255,255,0.28); }}
        QScrollBar:horizontal {{ background: transparent; height: 10px; }}
        QScrollBar::handle:horizontal {{ background: rgba(255,255,255,0.18); border-radius: 5px; min-width: 40px; }}

        QCheckBox {{
            background: transparent;
            color: {panel.name()};
        }}

        QCheckBox::indicator:unchecked {{
            background: transparent;
            background-color: transparent;
            color: white;
            border: 1px solid #5A5A5A;
        }}

        QPushButton {{
            background-color: rgba(255,255,255,0.06);
            border: 0px solid rgba(255,255,255,0.08);
            border-radius: 0px;
            padding: 6px 10px;
            color: {panel.name()};
        }}
        QPushButton:hover {{ background-color: rgba(255,255,255,0.12); }}
        QPushButton:pressed {{ background-color: rgba(255,255,255,0.18); }}
        QPushButton:disabled {{ color: {disabled.name()}; border-color: rgba(255,255,255,0.04); }}

        QLineEdit, QComboBox, QTextEdit {{
            background-color: {text.name()};
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 8px;
            padding: 6px 8px;
            color: {panel.name()};
            selection-background-color: {highlight.name()};
        }}
        QComboBox QAbstractItemView {{
            background-color: {panel.name()};
            border: 1px solid rgba(255,255,255,0.08);
            selection-background-color: rgba(255,255,255,0.10);
        }}

        QToolTip {{
            background: {text.name()};
            background-color: {text.name()};
            color: {panel.name()};
            border: 3px solid rgba(255,255,255,0.12);
            padding: 2px 2px;
            opacity: 230;
        }}
        """
        app.setStyleSheet(qss)
