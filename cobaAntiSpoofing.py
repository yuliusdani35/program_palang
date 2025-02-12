from deepface import DeepFace

res = DeepFace.extract_faces(
  img_path="output/20062024_143206_Unknown.png",
  anti_spoofing = True
)
print(res[0].get("facial_area"))
print(res[0].get("is_real"))