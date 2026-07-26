"""Error shape for the ValueWeave API.

One class, because an API that fails in five different shapes is an API a client
has to guess about. Every failure produces the same envelope with an HTTP status,
a stable machine-readable `code`, and a message written for the person reading it.
"""


class ApiError(Exception):
    def __init__(self, status, code, message, **detail):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.detail = detail

    def to_dict(self):
        d = {"error": {"code": self.code, "message": self.message, "status": self.status}}
        if self.detail:
            d["error"]["detail"] = self.detail
        return d

    # ------------------------------------------------------- constructors
    @classmethod
    def not_found(cls, what, identifier):
        return cls(404, "NOT_FOUND", f"no {what} with id {identifier!r}",
                   resource=what, id=identifier)

    @classmethod
    def bad_request(cls, message, **detail):
        return cls(400, "BAD_REQUEST", message, **detail)

    @classmethod
    def unsupported_method(cls, method, path):
        return cls(405, "METHOD_NOT_ALLOWED",
                   f"{method} is not supported; this API is read-only. "
                   f"Writes go to packages, never to the graph (ADR-001).",
                   method=method, path=path)
