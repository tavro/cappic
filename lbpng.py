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

label = "Test Label"
embed_label("test.png", "labeled.png", label)
