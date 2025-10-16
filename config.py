
from __future__ import annotations
from typing import List
from models import LoyaltyTier, LoyaltyRule

class Config:
    _instance = None

    def __init__(self):
        # Reglas por defecto: 3 meses, >=4 Super VIP, >=2 VIP
        self.rules: List[LoyaltyRule] = [
            LoyaltyRule(min_visits=4, window_months=3, resulting_tier=LoyaltyTier("Super VIP", 2)),
            LoyaltyRule(min_visits=2, window_months=3, resulting_tier=LoyaltyTier("VIP", 1)),
        ]

    @classmethod
    def get_instance(cls) -> "Config":
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def set_rules(self, rules: List[LoyaltyRule]) -> None:
        # ordenar de mayor a menor min_visits
        self.rules = sorted(rules, key=lambda r: r.min_visits, reverse=True)

    def get_rules(self) -> List[LoyaltyRule]:
        return list(self.rules)
