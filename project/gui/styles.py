from enum import Enum
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon
from PyQt6.QtCore import Qt
import os
import platform


class AppTheme(Enum):
    """Application theme options."""
    LIGHT = 0
    DARK = 1
    SYSTEM = 2


class StyleManager:
    """
    Manages application styling and theming.
    Provides consistent colors, fonts, and styling for the application.
    """
    
    # Color Palette - Light Theme
    LIGHT_COLORS = {
        "background": "#FFFFFF",
        "card_background": "#F5F7FA",
        "primary": "#007AFF",     # macOS blue
        "primary_dark": "#0062CC",
        "primary_light": "#CCE4FF",
        "accent": "#FF9500",      # macOS orange
        "error": "#FF3B30",       # macOS red
        "success": "#34C759",     # macOS green
        "warning": "#FF9500",     # macOS orange
        "info": "#5AC8FA",        # macOS light blue
        "text_primary": "#000000",
        "text_secondary": "#8E8E93",
        "text_disabled": "#C7C7CC",
        "divider": "#E5E5EA",
        "button_text": "#FFFFFF",
        "input_background": "#FFFFFF",
        "input_border": "#D1D1D6"
    }
    
    # Color Palette - Dark Theme
    DARK_COLORS = {
        "background": "#1C1C1E",
        "card_background": "#2C2C2E",
        "primary": "#0A84FF",     # macOS blue (dark)
        "primary_dark": "#0071E3",
        "primary_light": "#1A3E5A",
        "accent": "#FF9F0A",      # macOS orange (dark)
        "error": "#FF453A",       # macOS red (dark)
        "success": "#30D158",     # macOS green (dark)
        "warning": "#FF9F0A",     # macOS orange (dark)
        "info": "#64D2FF",        # macOS light blue (dark)
        "text_primary": "#FFFFFF",
        "text_secondary": "#98989D",
        "text_disabled": "#48484A",
        "divider": "#38383A",
        "button_text": "#FFFFFF",
        "input_background": "#2C2C2E",
        "input_border": "#48484A"
    }
    
    # Font Styles
    FONTS = {
        "regular": QFont("-apple-system", 13),
        "small": QFont("-apple-system", 11),
        "large": QFont("-apple-system", 16),
        "title": QFont("-apple-system", 20, QFont.Weight.Bold),
        "button": QFont("-apple-system", 13, QFont.Weight.Medium),
        "bold": QFont("-apple-system", 13, QFont.Weight.Bold)
    }
    
    # Spacing
    MARGINS = {
        "small": 8,
        "medium": 16,
        "large": 24,
        "xlarge": 32
    }
    
    # Border Radius
    RADIUS = {
        "small": 4,
        "medium": 8,
        "large": 12
    }
    
    @staticmethod
    def is_dark_mode_detected() -> bool:
        """
        Detect if system is using dark mode.
        Currently supported on macOS.
        """
        if platform.system() == 'Darwin':  # macOS
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'], 
                    capture_output=True, 
                    text=True
                )
                return result.stdout.strip() == 'Dark'
            except Exception:
                return False
        return False
    
    @staticmethod
    def set_app_theme(app, theme: AppTheme = AppTheme.SYSTEM):
        """
        Apply theme to the application.
        
        Args:
            app: The QApplication instance
            theme: The theme to apply (LIGHT, DARK, or SYSTEM)
        """
        if theme == AppTheme.SYSTEM:
            # Detect system theme
            use_dark = StyleManager.is_dark_mode_detected()
        else:
            use_dark = theme == AppTheme.DARK
        
        # Get the appropriate color set
        colors = StyleManager.DARK_COLORS if use_dark else StyleManager.LIGHT_COLORS
        
        # Create palette
        palette = QPalette()
        
        # Set window/background colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["input_background"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["card_background"]))
        
        # Set button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["button_text"]))
        
        # Set text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["text_primary"]))
        
        # Set highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["button_text"]))
        
        # Set link color
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(colors["primary_dark"]))
        
        # Set tooltip colors
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["card_background"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text_primary"]))
        
        # Set the palette
        app.setPalette(palette)
        
        # Apply stylesheet for more fine-grained control
        app.setStyleSheet(StyleManager.get_stylesheet(use_dark))
    
    @staticmethod
    def get_stylesheet(dark_mode: bool = False) -> str:
        """
        Get the application stylesheet.
        
        Args:
            dark_mode: Whether to use dark mode colors
            
        Returns:
            The stylesheet as a string
        """
        # Get color palette based on theme
        colors = StyleManager.DARK_COLORS if dark_mode else StyleManager.LIGHT_COLORS
        
        # Base stylesheet
        return f"""
        /* QWidget */
        QWidget {{
            background-color: {colors["background"]};
            color: {colors["text_primary"]};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            font-size: 13px;
        }}
        
        /* QLabel */
        QLabel {{
            background-color: transparent;
            color: {colors["text_primary"]};
        }}
        
        QLabel#titleLabel {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        QLabel#headingLabel {{
            font-size: 16px;
            font-weight: bold;
        }}
        
        QLabel#errorLabel {{
            color: {colors["error"]};
        }}
        
        QLabel#successLabel {{
            color: {colors["success"]};
        }}
        
        /* QPushButton */
        QPushButton {{
            background-color: {colors["primary"]};
            color: {colors["button_text"]};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: medium;
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: {colors["primary_dark"]};
        }}
        
        QPushButton:pressed {{
            background-color: {colors["primary_dark"]};
            opacity: 0.8;
        }}
        
        QPushButton:disabled {{
            background-color: {colors["text_disabled"]};
            color: {colors["background"]};
            opacity: 0.7;
        }}
        
        QPushButton#secondaryButton {{
            background-color: transparent;
            color: {colors["primary"]};
            border: 1px solid {colors["primary"]};
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: {colors["primary_light"]};
        }}
        
        QPushButton#destructiveButton {{
            background-color: {colors["error"]};
        }}
        
        QPushButton#destructiveButton:hover {{
            background-color: #FF5A4F;
        }}
        
        /* QLineEdit */
        QLineEdit {{
            background-color: {colors["input_background"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["input_border"]};
            border-radius: 6px;
            padding: 8px;
            min-height: 16px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {colors["primary"]};
        }}
        
        /* QComboBox */
        QComboBox {{
            background-color: {colors["input_background"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["input_border"]};
            border-radius: 6px;
            padding: 8px;
            min-height: 16px;
        }}
        
        QComboBox:editable {{
            background-color: {colors["input_background"]};
        }}
        
        QComboBox:focus {{
            border: 1px solid {colors["primary"]};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 0px;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }}
        
        /* QScrollBar */
        QScrollBar:vertical {{
            border: none;
            background-color: {colors["input_background"]};
            width: 12px;
            margin: 12px 0px 12px 0px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors["text_secondary"]};
            min-height: 30px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors["primary"]};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {colors["input_background"]};
            height: 12px;
            margin: 0px 12px 0px 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors["text_secondary"]};
            min-width: 30px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors["primary"]};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
            width: 0px;
        }}
        
        /* QTabWidget and QTabBar */
        QTabWidget::pane {{
            border: 1px solid {colors["divider"]};
            border-radius: 6px;
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            color: {colors["text_secondary"]};
            border-bottom: 2px solid transparent;
            padding: 8px 16px;
            margin-right: 4px;
        }}
        
        QTabBar::tab:selected {{
            color: {colors["primary"]};
            border-bottom: 2px solid {colors["primary"]};
        }}
        
        QTabBar::tab:hover:!selected {{
            color: {colors["text_primary"]};
        }}
        
        /* QProgressBar */
        QProgressBar {{
            border: none;
            border-radius: 4px;
            background-color: {colors["input_background"]};
            text-align: center;
            color: transparent;
            max-height: 6px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors["primary"]};
            border-radius: 4px;
        }}
        
        /* QGroupBox */
        QGroupBox {{
            border: 1px solid {colors["divider"]};
            border-radius: 6px;
            margin-top: 16px;
            padding-top: 16px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 5px;
            color: {colors["text_secondary"]};
        }}
        
        /* QFrame (for dividers) */
        QFrame#hline {{
            background-color: {colors["divider"]};
            border: none;
            max-height: 1px;
            min-height: 1px;
        }}
        
        QFrame#vline {{
            background-color: {colors["divider"]};
            border: none;
            max-width: 1px;
            min-width: 1px;
        }}
        """
    
    @staticmethod
    def get_color(color_name: str, dark_mode: bool = False) -> QColor:
        """Get a color from the palette."""
        colors = StyleManager.DARK_COLORS if dark_mode else StyleManager.LIGHT_COLORS
        return QColor(colors.get(color_name, colors["text_primary"]))
    
    @staticmethod
    def get_font(font_name: str) -> QFont:
        """Get a font from the defined fonts."""
        return StyleManager.FONTS.get(font_name, StyleManager.FONTS["regular"])
    
    @staticmethod
    def get_margin(size: str) -> int:
        """Get a margin/padding value."""
        return StyleManager.MARGINS.get(size, StyleManager.MARGINS["medium"])
    
    @staticmethod
    def get_radius(size: str) -> int:
        """Get a border radius value."""
        return StyleManager.RADIUS.get(size, StyleManager.RADIUS["medium"]) 