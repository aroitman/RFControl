from PyQt5 import QtCore, QtGui, QtWidgets
import helpers
import css

class fancySpin(QtWidgets.QLineEdit):
    sigValueChanging = QtCore.pyqtSignal()
    valueChanged = QtCore.pyqtSignal(float)

    def __init__(self, *args,**kwargs):

        super(fancySpin, self).__init__(*args,**kwargs)
        self.setEnabled(False)
        self.setStyleSheet(css.style_property)
        self.setProperty('status', 'disabled')
        self.setStyle(self.style())

        try:
            if "sig_figs" not in kwargs:
                kwargs["sig_figs"] = 3
            if "value" not in kwargs:
                kwargs["value"] = 0
            if "min" not in kwargs:
                kwargs["min"] = -1e9
            if "max" not in kwargs:
                kwargs["max"] = 1e9
            self.sig_figs = kwargs["sig_figs"]
            self._value = kwargs["value"]
            self.setRange(kwargs["min"],kwargs["max"])

            self.value = kwargs["value"]
        except:
            pass

        self.returnPressed.connect(self.sigValueChanging.emit)

    @property
    def value(self):
        if self.sig_figs > 0: # return float
            return self._value
        else: # return int
            return int(self._value)

    @value.setter
    def value(self,val):
        try:
            val = float(val)
        except ValueError:
            #print("Conv error, set to prev val")
            val = self.value
            pass

        val = max(self.minimum,val)
        val = min(self.maximum,val)
        self._value = round(val,self.sig_figs)

        l = len(self.text())
        pos = self.cursorPosition()

        #self.setText(str(self.value))
        #self.setText( "%.*f" % (self.sig_figs,self.value))
        super(fancySpin,self).setText( "%.*f" % (self.sig_figs,self.value))
        if l < len(self.text()):
            pos = pos + 1
            #print("first pos %d textL %d" % (l, len(self.text())))
        elif l > len(self.text()):
            #print("other pos %d textL %d" % (l, len(self.text())))
            pos = pos - 1

        self.setCursorPosition(pos)
        self.valueChanged.emit(self.value)

#    def setText(self,text):
#        self._value = float(text)
#        super(fancySpin,self).setText(str(text))

    # Change by one tick (precision of the box)
    def tickUp(self):
        self.value = self.value + 10**(-self.sig_figs)
    def tickDown(self):
        self.value = self.value - 10**(-self.sig_figs)
    # Give tick size
    @property
    def tickSize(self):
        return 10**(-self.sig_figs)


    def focusOutEvent(self,event):
        self.value = self.text()
        super(fancySpin,self).focusOutEvent(event)


    def keyPressEvent(self,e):
        #print("key pressss", e.key())
        val_before = self.value
        # Plain control does nothing
        if e.key() == QtCore.Qt.Key_Control:
            return
        # Plain shift does nothing
        if e.key() == QtCore.Qt.Key_Shift:
            return


        # Ctrl + something
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            # For select all and copy do the thing
            if e.key() == QtCore.Qt.Key_A or e.key() == QtCore.Qt.Key_C:
                super(fancySpin,self).keyPressEvent(e)
                return

            # For cut and paste this also will change the box!
            if e.key() == QtCore.Qt.Key_X or e.key() == QtCore.Qt.Key_V:
                super(fancySpin,self).keyPressEvent(e)
                self.value = helpers.get_number_as_text_from_string(self.text())
                #super(fancySpin,self).setText( "%.*f" % (self.sig_figs,self.value))
                #if self.value != val_before:
                #    self.sigValueChanging.emit()
                return


        # in case shift is depressed (marking with left-right arrows, home end)
        if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            if e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_Right \
                  or e.key() == QtCore.Qt.Key_Home or e.key() == QtCore.Qt.Key_End:
                super(fancySpin,self).keyPressEvent(e)
                return


        # In case no modifier keys pressed.

        # Let there be numbers, backspace and dot
        # numbers
        if e.key() >= 0x30 and e.key() <= 0x39:
            super(fancySpin,self).keyPressEvent(e)
            return
        # delete or backspace is ok
        elif e.key() == QtCore.Qt.Key_Delete or e.key() == QtCore.Qt.Key_Backspace:
            super(fancySpin,self).keyPressEvent(e)
            return
        # Dot is ok if not already existing or if it within marked text
        elif e.key() == QtCore.Qt.Key_Period:
            if "." in self.selectedText():
                super(fancySpin,self).keyPressEvent(e)
                return
            if "." in super(fancySpin,self).text():
                return
            else:
                super(fancySpin,self).keyPressEvent(e)
                return
        # minus is ok in the very beginning of the line and when < 0 allowed:
        elif e.key() == QtCore.Qt.Key_Minus and self.minimum < 0:
            # Beginning of the line
            if  self.cursorPosition() == 0 or \
                 self.selectedText() == self.text():
                super(fancySpin,self).keyPressEvent(e)
        elif e.key() == QtCore.Qt.Key_Home or e.key() == QtCore.Qt.Key_End:
            super(fancySpin,self).keyPressEvent(e)


        # Ok now something that will actually "lock" the number
        # Like enter, moving left-right, minus
        elif e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return or \
               e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_Right or \
               e.key() == QtCore.Qt.Key_Up or e.key() == QtCore.Qt.Key_Down:
#               e.key() == QtCore.Qt.Key_Minus:

            # Emit only one signal
            #print("old val from FSB ", self._value)
            old_val = self._value
            self.blockSignals(True)
            # Get the cursor position relative to dot BEFORE move
            pos = self.cursorPosition()
            if "." in self.text():
                dot_pos = self.text().find(".")
            else:
                dot_pos = len(self.text())
            # relative position to dot or end of number (if integer)
            # zero = just left of dot. more left is more negative
            rel_pos = pos - dot_pos
            # Do we go more left or right?
            if e.key() == QtCore.Qt.Key_Left:
                rel_pos = rel_pos - 1
            elif e.key() == QtCore.Qt.Key_Right:
                rel_pos = rel_pos + 1

            # Minus will set minus value but only if minus values are allowed
            #if e.key() == QtCore.Qt.Key_Minus and self.minimum < 0:
            #    print("minus")
            #    if "-" in self.text():
            #        self.value = helpers.get_number_as_text_from_string(self.text()[1:])
            #    else:
            #        self.value = helpers.get_number_as_text_from_string("-"+self.text())
            #else:
            self.value = helpers.get_number_as_text_from_string(self.text())
#            super(fancySpin,self).keyPressEvent(e)

            # Now after we want to set the cursor relative to dot
            if "." in self.text():
                dot_pos = self.text().find(".")
            else:
                dot_pos = len(self.text())
            new_pos = dot_pos + rel_pos
            if new_pos < 0:
                new_pos = 0
            elif new_pos > len(self.text()):
                new_pos = len(self.text())
            self.setCursorPosition(new_pos)

            # Up or down will change the value
            if e.key() == QtCore.Qt.Key_Up or e.key() == QtCore.Qt.Key_Down:
                pos = self.cursorPosition()
                rel_cursor_pos = pos - dot_pos
                # Don't do if 1) cursor on left side of -, 2) right side of dot
                if (self.text()[0] != "-" or pos > 0):
                    if rel_cursor_pos != 1:
                        # zero is just left to dot
                        if rel_cursor_pos <= 0: # 1, 10, 100 x change
                            change = 10**(-rel_cursor_pos)
                        else: # Right side there is . that takes 1 cursor pos
                            change = 10**(-rel_cursor_pos+1)

                        if e.key() == QtCore.Qt.Key_Up: 
                            self.value = self.value + change
                        elif e.key() == QtCore.Qt.Key_Down: 
                            self.value = self.value - change

            self.blockSignals(False)
            #print("new val from FSB", self._value)
            if old_val != self._value:
                self.valueChanged.emit(self.value)

            return

    def setValue(self,value_to_set):
        self.value = value_to_set
        #self.setText( "%.*f" % (self.sig_figs,value_to_set))
        pass
         
    def setRange(self,min_,max_):
        self.minimum = min_
        self.maximum = max_

        if self.minimum > self.value or self.maximum < self.value:
            self.value = self.value

    def setDecimals(self,precision):
        self.sig_figs = precision
        self.value = self.value

    def setPrecision(self,precision):
        self.sig_figs = precision
        self.value = self.value


    def setMinimum(self,value):
        self.minimum = value
        if self.minimum > self.value:
            self.value = self.value

    def setMaximum(self,value):
        self.maximum = value
        if self.maximum < self.value:
            self.value = self.value

    def setText(self,text_to_set): # This call might come outside..
        # Let's see if the text to set has format 1.234;3;-5;5
        # Then it is number to set 1.234, decimals 3, min -5, max 5
        vals = text_to_set.split(';')
        if len(vals) == 4:
            self.setRange(float(vals[2]),float(vals[3]))
            self.setDecimals(int(vals[1]))
            self.value = helpers.get_number_as_text_from_string(vals[0])
        else:
        #self.value = float(text_to_set)
            self.value = helpers.get_number_as_text_from_string(text_to_set)

