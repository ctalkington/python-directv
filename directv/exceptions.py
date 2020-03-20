"""Exceptions for DirecTV."""


class DIRECTVError(Exception):
    """Generic DirecTV exception."""

    pass


class DIRECTVConnectionError(DIRECTVError):
    """DirecTV connection exception."""

    pass


class DIRECTVAccessRestricted(DIRECTVError):
    """DirecTV access restricted."""

    pass
