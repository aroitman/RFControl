
style = \
    """
    QWidget:disabled{
                border-width:3px;
                border-color:white;
                color:white;
                background-color:white;
    }

    QLineEdit:focus{
                border-style:solid;
                border-color:black;
                border-width:2px;
                background-color:lightgreen;
    }

    QLineEdit:enabled{
                color:black;
                background-color:lightgreen;
    }


    QLabel:enabled{
                border-width:1px;
                color:black;
                background-color:lightgreen;
    }

    """
normal = "color:black;background-color:lightgreen;"

warn = "color:black;background-color:yellow;"

alarm = "color:black;background-color:red;"

invalid = normal
# invalid = "border-style:solid;border-width:1px;border-color:white;"

disabled = "border-style:solid;border-width:5px;border-color:white;color:white;background-color:white;"

style_property = """
    eFancySpin:focus{
                border-style:solid;
                border-color:black;
                border-width:2px;
                background-color:lightgreen;
    }

    eFancySpin:enabled{
                color:black;
                background-color:lightgreen;
    }

    QPushButton[status='ready']{
        color: white;
        background-color: gray;
    }

    QPushButton[status='clicked']{
        color: white;
        background-color: gray;
    }

    e2CheckBox[status='normal']{
        color: black;
        background-color: lightgreen;
    }

    e2CheckBox[status='warn']{
        color: black;
        background-color: yellow;
    }

    e2CheckBox[status='alarm']{
        color: black;
        background-color: red;
    }

    e2CheckBox[status='disabled']{
        border-style: solid;
        border-width: 5px;
        border-color: white;
        color: white;
        background-color: white;
    }

    e2CheckBox[status='invalid']{
        color: black;
        background-color: white;
    }

    QSlider::groove:horizontal {
        border: 1px solid #bbb;
        background: white;
        height: 10px;
        border-radius: 4px;
    }

    QSlider::sub-page:horizontal {
        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
            stop: 0 #66e, stop: 1 #bbf);
        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
            stop: 0 #bbf, stop: 1 #55f);
        border: 1px solid #777;
        height: 10px;
        border-radius: 4px;
    }

    QSlider::sub-page:horizontal[status='normal'] {
        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
            stop: 0 #66e, stop: 1 lightgreen);
        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
            stop: 0 lightgreen, stop: 1 green);
        border: 1px solid #777;
        height: 10px;
        border-radius: 4px;
    }

    QSlider::sub-page:horizontal[status='alarm'] {
        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
            stop: 0 #66e, stop: 1 lightred);
        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
            stop: 0 lightred, stop: 1 red);
        border: 1px solid #777;
        height: 10px;
        border-radius: 4px;
    }

    QSlider::sub-page:horizontal[status='warn'] {
        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
            stop: 0 #66e, stop: 1 lightyellow);
        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
            stop: 0 lightyellow, stop: 1 yellow);
        border: 1px solid #777;
        height: 10px;
        border-radius: 4px;
    }

    QSlider::add-page:horizontal {
        background: #fff;
        border: 1px solid #777;
        height: 10px;
        border-radius: 4px;
    }

    QSlider::handle:horizontal {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #eee, stop:1 #ccc);
        border: 1px solid #777;
        width: 13px;
        margin-top: -2px;
        margin-bottom: -2px;
        border-radius: 4px;
    }

    QSlider::handle:horizontal:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #fff, stop:1 #ddd);
        border: 1px solid #444;
        border-radius: 4px;
    }

    QSlider::sub-page:horizontal:disabled {
        background: #bbb;
        border-color: #999;
    }

    QSlider::add-page:horizontal:disabled {
        background: #eee;
        border-color: #999;
    }

    QSlider::handle:horizontal:disabled {
        background: #eee;
        border: 1px solid #aaa;
        border-radius: 4px;
    }
"""

standard_formatting = r"""{0}[status='normal']{{
        color: black;
        background-color: lightgreen;
    }}

    {0}[status='warn']{{
        color: black;
        background-color: yellow;
    }}

    {0}[status='alarm']{{
        color: black;
        background-color: red;
    }}

    {0}[status='disabled']{{
        border-style: solid;
        border-width: 5px;
        border-color: white;
        color: white;
        background-color: white;
    }}

    {0}[status='invalid']{{
        color: black;
        background-color: white;
    }}"""

widgets = ('e2CheckBox', 'e2Combo', 'e2Label', 'eButtonGroup', 'eFancySpin', 'eIndicator', 'e2TextEdit', 'eButton')
for w in widgets:
    style_property += standard_formatting.format(w)
