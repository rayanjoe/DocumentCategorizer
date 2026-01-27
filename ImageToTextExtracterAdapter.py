import base64

def image_to_base64(path):
    with open(path, 'rb') as file:
        # read the binary data
        binary_data = file.read()

        # encode to base64 bytes
        base64_bytes = base64.b64encode(binary_data)

        # decode bytes to utf-8 string
        base_string = base64_bytes.decode('utf-8')
        
        print(base_string)
        return base_string

# base_64_value = image_to_base64(r"E:\Project\Freddiie Mac\document-cat\POC\test\insurance.png")
# print(base_64_value)

# def base64_to_image(base64_string, output_path):
#     image_bytes = base64.b64decode(base64_string)
#     with open(output_path, 'wb') as file:
#         file.write(image_bytes)
#
# base64_to_image(base_64_value,
#                 r"C:\Users\darshan.lingegowda\Downloads\recreated.jpg"
#                 )




# from PIL import Image
# import pytesseract
 
# # If needed, set this path (example):
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# img_path = r"E:\Project\Freddiie Mac\document-cat\POC\test\insurance.png"
# text = pytesseract.image_to_string(Image.open(img_path))

# print(text)
