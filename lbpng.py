from PIL import Image, ImageDraw, ImageFont
import re


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


label = "[content:'Namn Namnsson', position:(32, 32)],[content:'Test Testsson', position:(64, 64)],[content:'Sson Ssonnamn', position:(96, 96)]"
embed_label("test.png", "labeled.lbpng", label)

draw_label("test.png", "labeled.png", "labeled.lbpng")

image = Image.open("test.png")
image2 = Image.open("labeled.png")
image_with_label = Image.open("labeled.lbpng")

image.show()
image2.show()
image_with_label.show()