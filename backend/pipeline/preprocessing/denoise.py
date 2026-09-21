import cv2


def denoise_image(input_path, output_path):
    image = cv2.imread(input_path)

    if image is None:
        raise ValueError("Could not read the image")

    denoised = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        10,
        10,
        7,
        21
    )

    cv2.imwrite(output_path, denoised)

    return output_path