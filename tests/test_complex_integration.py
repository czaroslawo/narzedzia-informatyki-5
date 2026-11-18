

from src.manager import Manager
from src.models import Parameters
from src.models import ApartmentSettlement, Bill, Tenant, TenantSettlement

def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs == "Mieszkanie nie istnieje"

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == "Brak rachunku dla tego mieszkania w podanym miesiacu"

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 0)
    assert costs == "Miesiac jest niepoprawny"

    costs = manager.get_apartment_costs('apart-polanka', 2024, 15)
    assert costs == "Miesiac jest niepoprawny"



def test_create_apartment_settlement():
    manager = Manager(Parameters())
    manager.bills = []
    for apartment, year, month, amount in [
        ('apart-polanka', 2025, 2, 100.0),
        ('apart-polanka', 2025, 2, 50.0),
    ]:
        manager.bills.append(Bill(
            apartment=apartment,
            date_due='2025-03-15',
            settlement_year=year,
            settlement_month=month,
            amount_pln=amount,
            type='rent',
        ))

    settlement = manager.create_apartment_settlement('apart-polanka', 2025, 2)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2025
    assert settlement.month == 2
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_bills_pln == 150.0
    assert settlement.total_due_pln == -150.0

    empty_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 3)

    assert isinstance(empty_settlement, ApartmentSettlement)
    assert empty_settlement.apartment == 'apart-polanka'
    assert empty_settlement.year == 2025
    assert empty_settlement.month == 3
    assert empty_settlement.total_rent_pln == 0.0
    assert empty_settlement.total_bills_pln == 0.0
    assert empty_settlement.total_due_pln == 0.0


def test_create_tenant_settlements():
    manager = Manager(Parameters())
    manager.tenants = {}
    for key, apartment, start, end in [
        ('tenant-1', 'apart-polanka', '2025-02-01', '2025-02-15'),
        ('tenant-2', 'apart-polanka', '2025-02-16', '2025-12-31'),
    ]:
        manager.tenants[key] = Tenant(
            name=key,
            apartment=apartment,
            room='room-test',
            rent_pln=1000.0,
            deposit_pln=2000.0,
            date_agreement_from=start,
            date_agreement_to=end,
        )
    apartment_settlement = ApartmentSettlement(
        apartment='apart-polanka',
        year=2025,
        month=2,
        total_rent_pln=0.0,
        total_bills_pln=150.0,
        total_due_pln=-150.0,
    )

    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 2
    assert {settlement.tenant for settlement in settlements} == {'tenant-1', 'tenant-2'}
    for settlement in settlements:
        assert isinstance(settlement, TenantSettlement)
        assert settlement.apartment_settlement == 'apart-polanka-2025-02'
        assert settlement.year == 2025
        assert settlement.month == 2
        assert settlement.rent_pln == 0.0
        assert settlement.bills_pln == 75.0
        assert settlement.total_due_pln == 75.0
        assert settlement.balance_pln == -75.0
    assert sum(settlement.bills_pln for settlement in settlements) == 150.0

    del manager.tenants['tenant-2']
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 1
    assert settlements[0].tenant == 'tenant-1'
    assert settlements[0].bills_pln == 150.0
    assert settlements[0].total_due_pln == 150.0
    assert settlements[0].balance_pln == -150.0

    del manager.tenants['tenant-1']

    assert manager.create_tenant_settlements(apartment_settlement) == []
