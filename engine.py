
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Dict

from models import LoyaltyTier, Customer
from repositories import VisitRepository, InMemoryCustomerRepository
from strategies import RuleStrategy

@dataclass
class LoyaltyEngine:
    strategy: RuleStrategy
    repo: VisitRepository
    customers: InMemoryCustomerRepository

    def classify(self, customer: Customer, as_of: date) -> LoyaltyTier:
        return self.strategy.classify(customer, as_of, self.repo)

    def classify_all(self, as_of: date) -> Dict[str, LoyaltyTier]:
        out = {}
        for c in self.customers.find_all():
            out[c.id] = self.classify(c, as_of)
        return out
