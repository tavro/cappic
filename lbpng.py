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

def read_label(path):
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

label = "Test Label"
embed_label("test.png", "labeled.png", label)

data = read_label("labeled.png")
print(data)
