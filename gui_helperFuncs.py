import base64
import io


def dangerApnea(val):
    """
    Determine if the apnea count value indicates danger.

    This function takes an apnea count value as input and returns True if the
    value is greater than 1, indicating a potential danger

    Args:
        val (int): Apnea count value

    Returns:
        bool: True if apnea count is greater than 1, False otherwise
    """
    if val > 1:
        return True
    else:
        return False


def decodeImg(encodedString):
    """
    Decode an image from its encoded string representation.

    This function takes an encoded image string as input, decodes it,
    and returns an image buffer

    Args:
        encodedString (str): Encoded image string

    Returns:
        io.BytesIO: Image buffer
    """
    image_bytes = base64.b64decode(encodedString)
    image_buf = io.BytesIO(image_bytes)
    return image_buf


def valPressureInput(val):
    """
    Validate the input value for pressure.

    This function checks if the input value is a non-empty string and a valid
    integer. If so, it converts the value to an integer and checks if it falls
    within the valid pressure range (4 to 25)

    Args:
        val (str): Input value for pressure

    Returns:
        bool: True if the input is a valid pressure value, False otherwise
    """
    if val:
        try:
            val = int(val)
        except ValueError:
            return False

        if 4 <= val <= 25:
            return True
        return False

    return True
