from constant import root_path
import onnxruntime as rt
import os
import numpy as np
import cv2

model_path = os.path.join(root_path, "template/gain.onnx")
model = rt.InferenceSession(model_path, providers=["CPUExecutionProvider"])
input_name = model.get_inputs()[0].name

def search_echoes(img: np.ndarray):
    height, width = img.shape[:2]
    x_factor = width / 640
    y_factor = height / 640

    img = cv2.resize(img, (640, 640))
    im = np.array(img) / 255.0
    im = np.transpose(im, (2, 0, 1))
    im = np.expand_dims(im, axis=0).astype(np.float32)

    pred = model.run(None, {input_name: im})
    outputs = np.transpose(np.squeeze(pred[0]))
    rows = outputs.shape[0]
    boxes = []
    scores = []
    for i in range(rows):
        classes_scores = outputs[i][4:]
        max_score = np.amax(classes_scores)
        if max_score >= 0.5:
            x, y, w, h = outputs[i][0], outputs[i][1], outputs[i][2], outputs[i][3]
            left = int((x - w / 2) * x_factor)
            top = int((y - h / 2) * y_factor)
            width = int(w * x_factor)
            height = int(h * y_factor)
            scores.append(max_score)
            boxes.append([left, top, width, height])
    indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, 0.5)
    conf = 0
    res = None
    for i in indices:
        score = scores[i]
        if score > conf:
            conf = score
            res = boxes[i]
    return int(res[0] + 0.5 * res[2]) if res is not None else None
