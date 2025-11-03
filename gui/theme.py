"""
TikTok Theme Configuration
Dark theme with TikTok's signature colors and styling
"""

# TikTok Color Palette
COLORS = {
    # Background colors
    'bg_primary': '#000000',           # Pure black background
    'bg_secondary': '#121212',         # Slightly lighter black
    'bg_card': '#1A1A1A',             # Card/panel background
    'bg_hover': '#2A2A2A',            # Hover state

    # TikTok accent colors
    'accent_pink': '#FE2C55',         # TikTok hot pink
    'accent_cyan': '#25F4EE',         # TikTok cyan/turquoise
    'accent_blue': '#00F2EA',         # Alternative cyan

    # Text colors
    'text_primary': '#FFFFFF',         # White text
    'text_secondary': '#A8A8A8',       # Gray text
    'text_dim': '#666666',            # Dimmed text

    # Status colors
    'success': '#00D46A',             # Green for success
    'error': '#FF3B5C',               # Red for errors
    'warning': '#FFC107',             # Yellow for warnings
    'info': '#25F4EE',                # Cyan for info

    # UI elements
    'border': '#333333',              # Border color
    'border_active': '#FE2C55',       # Active border (pink)
    'shadow': '#000000',              # Shadow color
}

# Font Configuration
FONTS = {
    'title': ('Segoe UI', 28, 'bold'),
    'heading': ('Segoe UI', 20, 'bold'),
    'subheading': ('Segoe UI', 16, 'bold'),
    'body': ('Segoe UI', 11),
    'body_bold': ('Segoe UI', 11, 'bold'),
    'small': ('Segoe UI', 9),
    'button': ('Segoe UI', 10, 'bold'),
    'stats': ('Segoe UI', 24, 'bold'),
}

# Spacing and Layout
SPACING = {
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 20,
    'border_radius': 8,
    'border_width': 2,
}

# Button Styles
BUTTON_STYLES = {
    'primary': {
        'bg': COLORS['accent_pink'],
        'fg': COLORS['text_primary'],
        'activebackground': '#E02449',
        'activeforeground': COLORS['text_primary'],
        'relief': 'flat',
        'cursor': 'hand2',
        'borderwidth': 0,
    },
    'secondary': {
        'bg': COLORS['accent_cyan'],
        'fg': COLORS['bg_primary'],
        'activebackground': '#1DD9D3',
        'activeforeground': COLORS['bg_primary'],
        'relief': 'flat',
        'cursor': 'hand2',
        'borderwidth': 0,
    },
    'ghost': {
        'bg': COLORS['bg_card'],
        'fg': COLORS['text_primary'],
        'activebackground': COLORS['bg_hover'],
        'activeforeground': COLORS['text_primary'],
        'relief': 'flat',
        'cursor': 'hand2',
        'borderwidth': 1,
    },
}

# Widget Default Styles
WIDGET_STYLES = {
    'frame': {
        'bg': COLORS['bg_primary'],
    },
    'label_frame': {
        'bg': COLORS['bg_card'],
        'fg': COLORS['text_primary'],
        'relief': 'flat',
        'borderwidth': 0,
    },
    'label': {
        'bg': COLORS['bg_primary'],
        'fg': COLORS['text_primary'],
    },
    'entry': {
        'bg': COLORS['bg_card'],
        'fg': COLORS['text_primary'],
        'insertbackground': COLORS['text_primary'],
        'relief': 'flat',
        'borderwidth': 2,
        'highlightthickness': 2,
        'highlightbackground': COLORS['border'],
        'highlightcolor': COLORS['accent_pink'],
    },
    'text': {
        'bg': COLORS['bg_card'],
        'fg': COLORS['text_primary'],
        'insertbackground': COLORS['text_primary'],
        'relief': 'flat',
        'borderwidth': 0,
    },
}

# TTK Styles Configuration
def configure_ttk_theme(style):
    """Configure ttk theme with TikTok colors"""

    # Notebook (tabs)
    style.configure('TNotebook',
                   background=COLORS['bg_primary'],
                   borderwidth=0)
    style.configure('TNotebook.Tab',
                   background=COLORS['bg_card'],
                   foreground=COLORS['text_secondary'],
                   padding=[20, 10],
                   borderwidth=0,
                   font=FONTS['body_bold'])
    style.map('TNotebook.Tab',
             background=[('selected', COLORS['bg_primary'])],
             foreground=[('selected', COLORS['accent_pink'])])

    # Treeview (tables)
    style.configure('Treeview',
                   background=COLORS['bg_card'],
                   foreground=COLORS['text_primary'],
                   fieldbackground=COLORS['bg_card'],
                   borderwidth=0,
                   font=FONTS['body'])
    style.configure('Treeview.Heading',
                   background=COLORS['bg_secondary'],
                   foreground=COLORS['text_primary'],
                   borderwidth=0,
                   font=FONTS['body_bold'])
    style.map('Treeview',
             background=[('selected', COLORS['accent_pink'])],
             foreground=[('selected', COLORS['text_primary'])])

    # Entry
    style.configure('TEntry',
                   fieldbackground=COLORS['bg_card'],
                   foreground=COLORS['text_primary'],
                   borderwidth=2,
                   relief='flat')

    # Button
    style.configure('TButton',
                   background=COLORS['accent_pink'],
                   foreground=COLORS['text_primary'],
                   borderwidth=0,
                   relief='flat',
                   font=FONTS['button'],
                   padding=[15, 8])
    style.map('TButton',
             background=[('active', '#E02449')])

    # Frame
    style.configure('TFrame',
                   background=COLORS['bg_primary'])

    # Label
    style.configure('TLabel',
                   background=COLORS['bg_primary'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['body'])

    # LabelFrame
    style.configure('TLabelframe',
                   background=COLORS['bg_card'],
                   foreground=COLORS['text_primary'],
                   borderwidth=0,
                   relief='flat')
    style.configure('TLabelframe.Label',
                   background=COLORS['bg_card'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['subheading'])

# Gradient effect simulation (using darker/lighter shades)
def get_gradient_colors(base_color, steps=5):
    """Generate gradient colors for visual effects"""
    # This is a simplified version for Tkinter
    # Real gradients would need canvas or image-based implementation
    return [base_color] * steps
