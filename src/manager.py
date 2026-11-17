from src.models import Apartment, Bill, Parameters, Tenant, Transfer


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