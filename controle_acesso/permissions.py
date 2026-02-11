from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Permissão base que verifica se o usuário tem o role necessário.
    Roles são hierárquicos: admin > superintendente > supervisor > apac
    """
    required_role = None

    # Hierarquia de roles (maior índice = maior permissão)
    ROLE_HIERARCHY = {
        'apac': 0,
        'supervisor': 1,
        'superintendente': 2,
        'admin': 3,
    }

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusuários Django sempre têm acesso
        if request.user.is_superuser:
            return True

        try:
            user_role = request.user.profile.role
        except Exception:
            return False

        user_level = self.ROLE_HIERARCHY.get(user_role, -1)
        required_level = self.ROLE_HIERARCHY.get(self.required_role, 99)

        return user_level >= required_level


class IsApac(HasRole):
    """Permite apac, supervisor, superintendente, admin"""
    required_role = 'apac'


class IsSupervisor(HasRole):
    """Permite supervisor, superintendente, admin"""
    required_role = 'supervisor'


class IsSuperintendente(HasRole):
    """Permite superintendente, admin"""
    required_role = 'superintendente'


class IsAdmin(HasRole):
    """Permite somente admin"""
    required_role = 'admin'
