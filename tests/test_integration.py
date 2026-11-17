from contextlib import nullcontext

from src.models import Apartment
from src.manager import Manager
from src.models import Parameters
import pytest


def test_load_data():
    parameters = Parameters()
    manager = Manager(parameters)
    assert isinstance(manager.apartments, dict)
    assert isinstance(manager.tenants, dict)
    assert isinstance(manager.transfers, list)
    assert isinstance(manager.bills, list)

    for apartment_key, apartment in manager.apartments.items():
        assert isinstance(apartment, Apartment)
        assert apartment.key == apartment_key

def test_tenants_in_manager():
    parameters = Parameters()
    manager = Manager(parameters)
    assert len(manager.tenants) > 0
    names = [tenant.name for tenant in manager.tenants.values()]
    for tenant in ['Jan Nowak', 'Adam Kowalski', 'Ewa Adamska']:
        assert tenant in names

def test_if_tenants_have_valid_apartment_keys():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.check_tenants_apartment_keys() == True

    manager.tenants['tenant-1'].apartment = 'invalid-key'
    assert manager.check_tenants_apartment_keys() == False

def test_if_apartment_cost_sum_properly():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs("apart", 2025, 1) == "Mieszkanie nie istnieje"
    assert manager.get_apartment_costs("apart-polanka", 2025, 3) == "Brak rachunku dla tego mieszkania w podanym miesiacu"
    assert manager.get_apartment_costs("apart-polanka", 2025, 1) == 910
