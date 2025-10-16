
from __future__ import annotations
from datetime import date
from typing import List, Tuple, Dict

from models import Customer, LoyaltyTier
from repositories import VisitRepository, InMemoryCustomerRepository
from strategies import months_ago

class ReportService:
    def __init__(self, repo: VisitRepository, customers: InMemoryCustomerRepository):
        self.repo = repo
        self.customers = customers

    def visits_by_month(self, customer: Customer, months: int, as_of: date) -> Dict[Tuple[int,int], int]:
        return self.repo.visits_by_month(customer.id, months, as_of)

    def ranking_top_customers(self, months: int, as_of: date) -> List[Tuple[Customer, int]]:
        start_date = months_ago(as_of, months)
        from datetime import datetime
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(as_of, datetime.max.time())

        rows: List[Tuple[Customer, int]] = []
        for c in self.customers.find_all():
            count = self.repo.count_visits(c.id, start_dt, end_dt, unique_per_day=True)
            rows.append((c, count))
        rows.sort(key=lambda x: (-x[1], x[0].name.lower()))
        return rows

    def export_ranking_csv(self, rows: List[Tuple[Customer,int]], path: str) -> None:
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["customer_id","name","email","phone","visits_last_window"])
            for c, v in rows:
                w.writerow([c.id, c.name, c.email, c.phone, v])
