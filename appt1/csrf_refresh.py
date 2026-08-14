from django.middleware.csrf import CsrfViewMiddleware

class CsrfRefreshMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Força a atualização do token CSRF em cada requisição
        if getattr(request, 'csrf_processing_done', False):
            return None
            
        try:
            self._accept_token(request)
        except:
            # Gera um novo token se o atual for inválido
            request.META["CSRF_COOKIE"] = self._get_new_csrf_string()
            request.META["CSRF_COOKIE_USED"] = True
            
        return super().process_view(request, callback, callback_args, callback_kwargs)