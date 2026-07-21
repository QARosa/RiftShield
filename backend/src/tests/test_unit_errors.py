from shared.utils.errors import AppError, UnauthorizedError, ForbiddenError, NotFoundError


class TestErrorsUnit:
    def test_app_error_default(self):
        err = AppError()
        assert err.status_code == 400
        assert err.message == "Erro interno"

    def test_app_error_custom(self):
        err = AppError("Custom error", 418)
        assert err.status_code == 418
        assert err.message == "Custom error"

    def test_unauthorized_error(self):
        err = UnauthorizedError()
        assert err.status_code == 401
        assert err.message == "Não autorizado"

    def test_unauthorized_error_custom(self):
        err = UnauthorizedError("Token expirado")
        assert err.status_code == 401
        assert err.message == "Token expirado"

    def test_forbidden_error(self):
        err = ForbiddenError()
        assert err.status_code == 403
        assert err.message == "Acesso negado"

    def test_not_found_error(self):
        err = NotFoundError()
        assert err.status_code == 404
        assert err.message == "Recurso não encontrado"

    def test_errors_are_exceptions(self):
        assert issubclass(AppError, Exception)
        assert issubclass(UnauthorizedError, AppError)
        assert issubclass(ForbiddenError, AppError)
        assert issubclass(NotFoundError, AppError)
