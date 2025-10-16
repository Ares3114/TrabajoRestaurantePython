
from __future__ import annotations
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Iterable, Tuple
from pathlib import Path

from models import Reservation, Customer

class VisitRepository:
    def get_reservations(self) -> List[Reservation]:
        raise NotImplementedError

    def count_visits(self, customer_id: str, start_dt: datetime, end_dt: datetime, unique_per_day: bool=True) -> int:
        res = [
            r for r in self.get_reservations()
            if r.customer_id == customer_id and start_dt <= r.dt <= end_dt
        ]
        if unique_per_day:
            days = {r.dt.date() for r in res}
            return len(days)
        return len(res)

    def visits_by_month(self, customer_id: str, months: int, as_of: date) -> Dict[Tuple[int,int], int]:
        """Devuelve {(year, month): count} para los últimos 'months' meses hasta as_of"""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta  # optional, but we won't use external deps
        # Implement without external deps:
        def add_months(d: date, m: int) -> date:
            y = d.year + (d.month - 1 + m) // 12
            m2 = (d.month - 1 + m) % 12 + 1
            day = min(d.day, [31,29 if y%4==0 and (y%100!=0 or y%400==0) else 28,31,30,31,30,31,31,30,31,30,31][m2-1])
            return date(y, m2, day)

        # Inicio = primer día del mes 'months-1' meses atrás
        start_month = add_months(as_of.replace(day=1), -(months-1))
        end_dt = datetime.combine(as_of, datetime.min.time()).replace(hour=23, minute=59, second=59)
        start_dt = datetime.combine(start_month, datetime.min.time())
        counts: Dict[Tuple[int,int], int] = defaultdict(int)

        for r in self.get_reservations():
            if r.customer_id != customer_id:
                continue
            if start_dt <= r.dt <= end_dt:
                key = (r.dt.year, r.dt.month)
                counts[key] += 1

        # asegurar llaves para todos los meses en rango
        out = {}
        cur = start_month
        for _ in range(months):
            out[(cur.year, cur.month)] = counts.get((cur.year, cur.month), 0)
            cur = add_months(cur, 1)
        return out

class CsvVisitRepository(VisitRepository):
    def __init__(self, path: str):
        self.path = Path(path)
        self._reservations: List[Reservation] = []
        self._customers: Dict[str, Customer] = {}

    def load(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"No existe el archivo: {self.path}")
        with self.path.open(newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected = {"reservation_id","customer_id","name","email","phone","datetime","party_size"}
            missing = expected - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"Faltan columnas en CSV: {missing}")

            seen_res_ids = set()
            for i, row in enumerate(reader, start=2):  # header es línea 1
                rid = row["reservation_id"].strip()
                if not rid or rid in seen_res_ids:
                    # saltar vacíos o duplicados
                    continue
                seen_res_ids.add(rid)

                cid = row["customer_id"].strip()
                name = row["name"].strip()
                email = row["email"].strip()
                phone = row["phone"].strip()
                dt_str = row["datetime"].strip()
                size_str = row["party_size"].strip()

                try:
                    from models import Reservation
                    dt = Reservation.parse_iso(dt_str)
                    size = int(size_str)
                    if size <= 0:
                        raise ValueError("party_size debe ser > 0")
                except Exception as e:
                    # ignorar fila inválida pero continuar
                    # en productivo: registrar en log
                    continue

                if cid not in self._customers:
                    self._customers[cid] = Customer(id=cid, name=name, email=email, phone=phone)

                self._reservations.append(Reservation(
                    id=rid, customer_id=cid, dt=dt, party_size=size
                ))

    def get_reservations(self):
        return list(self._reservations)

    def get_customers(self) -> Dict[str, Customer]:
        return dict(self._customers)

class InMemoryCustomerRepository:
    def __init__(self, customers: Dict[str, Customer]):
        self._customers = customers

    def find_by_id(self, cid: str) -> Customer | None:
        return self._customers.get(cid)

    def find_all(self):
        return list(self._customers.values())
