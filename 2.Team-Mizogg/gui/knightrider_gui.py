from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

# KnightRiderWidget: Custom QWidget for a Knight Rider-style animation of moving lights.
class KnightRiderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set up timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        # Initialize position and direction
        self.position = 0
        self.direction = 1
        # Define light dimensions and spacing
        self.lightWidth = 35
        self.lightHeight = 12
        self.lightSpacing = 10
        # Set light color
        self.lightColor = QColor('#FF0000')
        # Configure widget properties
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def startAnimation(self):
        # Start the animation timer
        self.timer.start(5)

    def stopAnimation(self):
        # Stop the animation timer
        self.timer.stop()

    def paintEvent(self, event):
        # Override paint event to draw lights
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(12):
            # Calculate position of each light
            lightX = self.position + i * (self.lightWidth + self.lightSpacing)
            lightRect = QRect(lightX, 0, self.lightWidth, self.lightHeight)
            # Draw rounded rectangle for each light
            painter.setBrush(self.lightColor)
            painter.drawRoundedRect(lightRect, 5, 5)

    def update(self):
        # Update position for animation
        self.position += self.direction
        # Reverse direction at edges
        if self.position <= 0 or self.position >= self.width() - self.lightWidth - self.lightSpacing:
            self.direction *= -1
        self.repaint()