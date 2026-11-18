from calendar import monthrange
from datetime import date
from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(
            self,
            apartment_key: str,
            year: int | None = None,
            month: int | None = None,
    ) -> float | str:
        sum = 0.0
        if apartment_key not in self.apartments:
            return "Mieszkanie nie istnieje"
        if month is not None:
            if month > 12 or month < 1:
                return "Miesiac jest niepoprawny"
            if not any(
                    bill.apartment == apartment_key
                    and bill.settlement_month == month
                    and (year is None or bill.settlement_year == year)
                    for bill in self.bills
            ):
                return "Brak rachunku dla tego mieszkania w podanym miesiacu"
        for bill in self.bills:
            if (
                    bill.apartment == apartment_key
                    and (year is None or bill.settlement_year == year)
                    and (month is None or bill.settlement_month == month)
            ):
                sum += bill.amount_pln
        return sum

    def create_apartment_settlement(
            self,
            apartment_key: str,
            year: int,
            month: int,
    ) -> ApartmentSettlement:
        total_bills_pln = sum(
            bill.amount_pln
            for bill in self.bills
            if bill.apartment == apartment_key
            and bill.settlement_year == year
            and bill.settlement_month == month
        )
        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=0.0,
            total_bills_pln=total_bills_pln,
            total_due_pln=-total_bills_pln,
        )

    def create_tenant_settlements(
            self,
            apartment_settlement: ApartmentSettlement,
    ) -> list[TenantSettlement]:
        year = apartment_settlement.year
        month = apartment_settlement.month
        first_day = date(year, month, 1)
        last_day = date(year, month, monthrange(year, month)[1])
        tenants = [
            key for key, tenant in self.tenants.items()
            if tenant.apartment == apartment_settlement.apartment
            and date.fromisoformat(tenant.date_agreement_from) <= last_day
            and date.fromisoformat(tenant.date_agreement_to) >= first_day
        ]
        if not tenants:
            return []

        bills_pln = apartment_settlement.total_bills_pln / len(tenants)
        return [
            TenantSettlement(
                tenant=key,
                apartment_settlement=f'{apartment_settlement.apartment}-{year}-{month:02d}',
                year=year,
                month=month,
                rent_pln=0.0,
                bills_pln=bills_pln,
                total_due_pln=bills_pln,
                balance_pln=-bills_pln,
            )
            for key in tenants
        ]
