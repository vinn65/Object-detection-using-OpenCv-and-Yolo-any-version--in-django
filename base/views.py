import cv2
import numpy as np
from django.shortcuts import render
from .forms import DetectionForm
import cv2
import numpy as np
from django.core.files.base import ContentFile


def get_output_layers(net):
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers

def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def detect(request):
    global classes, COLORS
    if request.method == 'POST':
        form = DetectionForm(request.POST, request.FILES)
        if form.is_valid():
            detection = form.save()

            image = np.frombuffer(detection.image.read(), np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)

            Width = image.shape[1]
            Height = image.shape[0]
            scale = 0.00392

            classes = None

            with open(detection.classes.path, 'r') as f:
                classes = [line.strip() for line in f.readlines()]

            COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

            net = cv2.dnn.readNet(detection.weights.path, detection.config.path)

            blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

            net.setInput(blob)

            outs = net.forward(get_output_layers(net))

            class_ids = []
            confidences = []
            boxes = []
            conf_threshold = 0.5
            nms_threshold = 0.4


            for out in outs:
                for object_detection in out:
                    scores = object_detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(object_detection[0] * Width)
                        center_y = int(object_detection[1] * Height)
                        w = int(object_detection[2] * Width)
                        h = int(object_detection[3] * Height)
                        x = center_x - w / 2
                        y = center_y - h / 2
                        class_ids.append(class_id)
                        confidences.append(float(confidence))
                        boxes.append([x, y, w, h])


            indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

            for i in indices:
                try:
                    box = boxes[i]
                except:
                    i = i[0]
                    box = boxes[i]

                x = box[0]
                y = box[1]
                w = box[2]
                h = box[3]
                draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

            # Save the modified image
            _, buffer = cv2.imencode('.jpg', image)
            detection.image.save('detection.jpg', ContentFile(buffer.tobytes()), save=True)

            return render(request, 'base/detection_result.html', {'detection': detection})
    else:
        form = DetectionForm()

    return render(request, 'base/detect.html', {'form': form})

def home(request):
    return render(request, 'base/home.html')
