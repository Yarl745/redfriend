from loader import dp
from .is_user import IsUser
from .is_active import IsActive

if __name__ == "filters":
    dp.filters_factory.bind(IsUser)
    dp.filters_factory.bind(IsActive)
