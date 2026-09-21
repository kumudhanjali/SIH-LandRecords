import cv2


def check_image_quality(input_path):
    image = cv2.imread(input_path)

    if image is None:
        raise ValueError("Could not read the image")

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    brightness = gray.mean()

    issues = []

    if width < 500 or height < 500:
        issues.append("Image resolution is too low")

    if blur_score < 50:
        issues.append("Image may be blurry")

    if brightness < 40:
        issues.append("Image is too dark")

    if brightness > 220:
        issues.append("Image is too bright")

    quality = "good" if not issues else "poor"

    return {
        "quality": quality,
        "width": width,
        "height": height,
        "blur_score": round(float(blur_score), 2),
        "brightness": round(float(brightness), 2),
        "issues": issues
    }