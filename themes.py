"""
UI Theme Definitions
macOS native dark mode color scheme
"""

# macOS Native Dark Mode Colors
MACOS_DARK = {
    # Background colors
    'bg_primary': '#1e1e1e',      # Main window background
    'bg_secondary': '#2a2a2a',    # Chat display background  
    'bg_tertiary': '#3a3a3a',     # Buttons and inputs
    'bg_hover': '#4a4a4a',        # Hover states
    
    # Text colors
    'text_primary': '#ffffff',     # Main text
    'text_secondary': '#a0a0a0',   # Muted text
    'text_tertiary': '#808080',    # Disabled text
    
    # Border colors
    'border': '#4a4a4a',
    'border_focus': '#707070',
    
    # Accent colors (subtle, macOS-style)
    'accent': '#5a5a5a',          # Buttons
    'accent_hover': '#6a6a6a',    # Button hover
    'mcp_accent': '#059669',       #MCP green
    'mcp_border': '#10b981',
}

# Button Styles
BUTTON_STYLE = """
    QPushButton {{
        background-color: {bg};
        color: {color};
        border: 1px solid {border};
        border-radius: 6px;
        padding: {padding};
    }}
    QPushButton:hover {{
        background-color: {hover};
    }}
    QPushButton:disabled {{
        background-color: #3a3a3a;
        color: #808080;
    }}
"""

# Input Style
INPUT_STYLE = """
    QLineEdit {{
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        padding: 10px;
    }}
    QLineEdit:focus {{
        border-color: #707070;
    }}
"""

# Chat Display Style
CHAT_STYLE = """
    QTextEdit {{
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        padding: 12px;
    }}
"""

def get_button_style(padding="6px 12px"):
    """Get button style with macOS theme"""
    return BUTTON_STYLE.format(
        bg=MACOS_DARK['bg_tertiary'],
        color=MACOS_DARK['text_primary'],
        border=MACOS_DARK['border'],
        hover=MACOS_DARK['bg_hover'],
        padding=padding
    )

def get_mcp_button_style():
    """Get MCP button style"""
    return """
        QPushButton {
            background-color: #059669;
            border: 2px solid #10b981;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #047857;
            border-color: #34d399;
        }
    """
