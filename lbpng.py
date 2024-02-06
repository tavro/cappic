import sys
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QLineEdit, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

from PIL import Image, ImageDraw, ImageFont

def embed_label(path, out, meta):
  signature = b'\x89PNG\r\n\x1a\n'
  
  with open(path, 'rb') as file:
    content = file.read()

  if not content.startswith(signature):
    raise ValueError("File is not PNG!")

  iend = content.rfind(b'IEND')

  # TODO: Calculate CRC
  
  key = 'CustomLabel'.encode('utf-8')
  val = meta.encode('utf-8')
  data = key + b'\x00' + val

  length = len(data).to_bytes(4, byteorder='big')
  chunk = length + b'tEXt' + data

  out_content = content[:iend] + chunk + content[iend:]

  with open(out, 'wb') as file:
      file.write(out_content)

def read_labels(path):
  with open(path, 'rb') as file:
    content = file.read()

  pos = 0
  while pos < len(content):
    pos = content.find(b'tEXt', pos)
    if pos == -1:
      break

    length = int.from_bytes(content[pos-4:pos], byteorder='big')
    start = pos + 4
    end = start + length
    data = content[start:end]

    if b'CustomLabel\x00' in data:
      label_start = data.find(b'\x00') + 1
      label = data[label_start:].decode('utf-8')
      return label

    pos = end

  return None

def process_labels(labels):
  pattern = r"\[content:'(.*?)',\s*position:\((\d+),\s*(\d+)\)\]"
  matches = re.findall(pattern, labels)
  result = [{'content': match[0], 'position': (int(match[1]), int(match[2]))} for match in matches]

  return result

def draw_label(path, out, labelpath):
    image = Image.open(path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", size=24)

    labels = read_labels(labelpath)
    labels = process_labels(labels)

    for data in labels:
        meta = data['content']
        position = data['position']
        color = (255, 0, 0)
        draw.text(position, meta, fill=color, font=font)

    image.save(out)

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_pixels = []
        self.image_label = QLabel()
        self.image_label.setMouseTracking(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Pixel Selector")
        self.setGeometry(100, 100, 800, 600)

        open_button = QPushButton("Open Image", self)
        open_button.clicked.connect(self.open_image)

        save_button = QPushButton("Save Selected Pixels", self)
        save_button.clicked.connect(self.save_pixels)

        layout = QVBoxLayout()
        layout.addWidget(open_button)
        layout.addWidget(save_button)
        layout.addWidget(self.image_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.tiff)")
        if file_path:
            self.image = QPixmap(file_path)
            self.image_label.setPixmap(self.image)

    def save_pixels(self):
        if self.selected_pixels:
            pixel_string = ",".join(self.selected_pixels)

            embed_label("test.png", "labeled.lbpng", pixel_string)
            draw_label("test.png", "labeled.png", "labeled.lbpng")

            image = Image.open("labeled.png")
            image.show()
        else:
            print("No pixels selected to save.")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image_label.pixmap() is not None:
            x = event.x() - self.image_label.pos().x()
            y = event.y() - self.image_label.pos().y()
            if 0 <= x < self.image_label.pixmap().width() and 0 <= y < self.image_label.pixmap().height():
                image = self.image_label.pixmap().toImage()
                content, ok = QInputDialog.getText(self, "Enter Content", "Enter content for selected pixel:")
                if ok:
                    pixel_info = f"[content:'{content}', position:({x}, {y})]"
                    self.selected_pixels.append(pixel_info)
                    print(f"Selected pixel at ({x}, {y}) with content: {content}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageWindow()
    ex.show()
    sys.exit(app.exec_())
