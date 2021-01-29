from django.contrib.auth.mixins import UserPassesTestMixin
# importo anche questi per rescrivere la funzione 'handle_no_permission' in modo che mi reindirizzi in automatico alla pagina login,
# altrimenti mi darebbe pagina 403 FORBIDDEN
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

class StaffMixin(UserPassesTestMixin):
    """ lo scopo di questo Mixin è fare in modo che solo lo Staff possa creare nuove Sezioni """

    def test_func(self): # definita in UserPassesTestMixin
        # passa il test se l'user è dell staff ( viene definito nel pannello Admin da SuperUser)
        return self.request.user.is_staff

    # sovrascrivo la funzione per farmi indirizzare alla pagina Login
    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
