class ImageError(RuntimeError):
    """
    Base exception for image loading failures.
    """


class ImageDownloadError(ImageError):
    """
    Raised when image data cannot be downloaded.
    """


class ImageDecodeError(ImageError):
    """
    Raised when downloaded data cannot be decoded as an image.
    """
