from fastapi import HTTPException, status


class ServiceException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class DocumentNotFoundException(ServiceException):
    def __init__(self):
        super().__init__(detail="Document not found", status_code=status.HTTP_404_NOT_FOUND)


class QuestionNotFoundException(ServiceException):
    def __init__(self):
        super().__init__(detail="Question not found", status_code=status.HTTP_404_NOT_FOUND)


class InvalidFileFormatException(ServiceException):
    def __init__(self, message: str = "Invalid file format. Only PDF, JPG, JPEG, and PNG files are allowed."):
        super().__init__(detail=message, status_code=status.HTTP_400_BAD_REQUEST)


class FileTooLargeException(ServiceException):
    def __init__(self, max_mb: int = 25):
        super().__init__(detail=f"File exceeds maximum allowed size of {max_mb} MB.", status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class UnauthorizedAccessException(ServiceException):
    def __init__(self):
        super().__init__(detail="Not authorized to access this resource", status_code=status.HTTP_403_FORBIDDEN)
