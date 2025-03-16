import cv2

from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Load the pre-trained Haar cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_EXPOSURE, 40)
for _ in range(10):
    cap.read()
cap.release()


# Open the webcam (0 for default camera)
def detect_face(plot=False):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_EXPOSURE, 40)
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return None, None
    cap.release()
    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces (adjust scaleFactor and minNeighbors as needed)
    try:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if plot:
            image = Image.fromarray(frame[::4, ::4])
            plt.figure()
            plt.imshow(image)
            for x, y, w, h in faces:
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # print(
                #     x + 0.5 * w,
                #     y + 0.5 * h,
                #     (x + w / 2) / gray.shape[1],
                #     (y + h / 2) / gray.shape[0],
                #     gray.shape,
                # )
                # Display the frame with detections (optional)

                plt.gca().add_patch(
                    patches.Rectangle(
                        (x / 4, y / 4),
                        w / 4,
                        h / 4,
                        linewidth=1,
                        edgecolor="r",
                        facecolor="none",
                    )
                )
            plt.savefig("test_face.png")
            plt.close()
        x, y, w, h = faces[-1]
        return (x + w / 2) / gray.shape[1], (y + h / 2) / gray.shape[0]
    except Exception as e:
        print(e)
        print("No face detected")
        # image = Image.fromarray(frame[::4, ::4])
        # plt.figure()
        # plt.imshow(image)
        # plt.savefig("test_face.png")
        # plt.close()
        return None, None


if __name__ == "__main__":
    while True:
        detect_face(plot=True)
