import cv2
import numpy as np


def order_points(points):
    """
    Order four points as:
    top-left, top-right, bottom-right, bottom-left
    """

    points = np.array(points, dtype="float32")

    ordered = np.zeros((4, 2), dtype="float32")

    total = points.sum(axis=1)
    difference = np.diff(points, axis=1)

    ordered[0] = points[np.argmin(total)]       # top-left
    ordered[2] = points[np.argmax(total)]       # bottom-right

    ordered[1] = points[np.argmin(difference)] # top-right
    ordered[3] = points[np.argmax(difference)] # bottom-left

    return ordered


def four_point_transform(image, points):
    """
    Transform a detected document quadrilateral
    into a straight rectangular view.
    """

    rect = order_points(points)

    top_left, top_right, bottom_right, bottom_left = rect

    width_top = np.linalg.norm(top_right - top_left)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)

    max_width = int(max(width_top, width_bottom))

    height_left = np.linalg.norm(bottom_left - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)

    max_height = int(max(height_left, height_right))

    if max_width < 100 or max_height < 100:
        return None

    destination = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]
        ],
        dtype="float32"
    )

    matrix = cv2.getPerspectiveTransform(
        rect,
        destination
    )

    warped = cv2.warpPerspective(
        image,
        matrix,
        (max_width, max_height)
    )

    return warped


def find_document_contour(image):
    """
    Try to find the outer document boundary.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    edges = cv2.Canny(
        blurred,
        50,
        150
    )

    # Close small gaps in document borders
    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    image_area = image.shape[0] * image.shape[1]

    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    for contour in contours[:20]:

        area = cv2.contourArea(contour)

        # Ignore very small contours
        if area < image_area * 0.20:
            continue

        perimeter = cv2.arcLength(
            contour,
            True
        )

        approximation = cv2.approxPolyDP(
            contour,
            0.02 * perimeter,
            True
        )

        # We want a four-corner document
        if len(approximation) == 4:

            points = approximation.reshape(
                4,
                2
            )

            return points

    return None


def small_angle_deskew(image):
    """
    Conservative fallback.

    Only correct small rotations.
    Never blindly rotate 90 or 180 degrees.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=100,
        minLineLength=int(image.shape[1] * 0.30),
        maxLineGap=20
    )

    if lines is None:
        return image

    angles = []

    for line in lines:

        x1, y1, x2, y2 = line[0]

        angle = np.degrees(
            np.arctan2(
                y2 - y1,
                x2 - x1
            )
        )

        # Normalize angle around horizontal
        if angle > 45:
            angle -= 90

        elif angle < -45:
            angle += 90

        # Only accept small skew
        if abs(angle) <= 10:
            angles.append(angle)

    if not angles:
        return image

    # Median is safer than trusting one detected line
    angle = float(np.median(angles))

    # Ignore tiny rotation
    if abs(angle) < 0.5:
        return image

    height, width = image.shape[:2]

    center = (
        width // 2,
        height // 2
    )

    rotation_matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    corrected = cv2.warpAffine(
        image,
        rotation_matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return corrected


def deskew_image(input_path, output_path):

    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(
            "Could not read the image"
        )

    # ------------------------------------------------
    # STEP 1: Try document boundary detection
    # ------------------------------------------------

    document_contour = find_document_contour(
        image
    )

    if document_contour is not None:

        corrected = four_point_transform(
            image,
            document_contour
        )

        if corrected is not None:

            cv2.imwrite(
                output_path,
                corrected
            )

            return output_path

    # ------------------------------------------------
    # STEP 2: Safe small-angle fallback
    # ------------------------------------------------

    corrected = small_angle_deskew(
        image
    )

    cv2.imwrite(
        output_path,
        corrected
    )

    return output_path