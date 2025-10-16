
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class LoyaltyTier:
    name: str
    priority: int = 0  # mayor número = tier más alto

@dataclass
class LoyaltyRule:
    min_visits: int
    window_months: int
    resulting_tier: LoyaltyTier

    def applies(self, visits_in_window: int) -> bool:
        return visits_in_window >= self.min_visits

@dataclass
class Customer:
    id: str
    name: str
    email: str
    phone: str

@dataclass
class Reservation:
    id: str
    customer_id: str
    dt: datetime
    party_size: int

    @staticmethod
    def parse_iso(dt_str: str) -> datetime:
        # Admite "YYYY-MM-DDTHH:MM" o "YYYY-MM-DD HH:MM" o solo fecha
        for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(dt_str.strip(), fmt)
            except ValueError:
                pass
        raise ValueError(f"Fecha/hora inválida: {dt_str}")
