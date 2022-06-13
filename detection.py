import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)
import tensorflow as tf
import cv2

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

PATH_TO_MODEL_DIR = './detection-AI/'
MIN_CONF_THRESH = float(0.60)
PATH_TO_SAVED_MODEL = PATH_TO_MODEL_DIR + "/saved_model"


def get_detection_function():
    print('Loading model...', end='')
    # LOAD SAVED MODEL AND BUILD DETECTION FUNCTION
    detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
    print('Done! model was loaded')
    return detect_fn


def detection_prediction(image_path, detect_fn):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if image_rgb.shape[1] > 1280:
        dim = (1280, image_rgb.shape[0])
        image_rgb = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
    if image_rgb.shape[0] > 1280:
        dim = (image_rgb.shape[1], 1280)
        image_rgb = cv2.resize(image_rgb, dim, interpolation = cv2.INTER_AREA)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image_rgb)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)

    detection_flag = False
    prediction = 0
    for index, leaf in enumerate(detections['detection_classes'][0].numpy()):
        if leaf == 1:
            if detections['detection_scores'][0].numpy()[index] > MIN_CONF_THRESH:
                detection_flag = True
                prediction = detections['detection_scores'][0].numpy()[index]
                break
    return (detection_flag, prediction)
