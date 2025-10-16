
from __future__ import annotations
from datetime import date
from typing import List

from models import LoyaltyRule, LoyaltyTier, Customer
from repositories import CsvVisitRepository, InMemoryCustomerRepository
from strategies import VisitsInWindowStrategy
from engine import LoyaltyEngine
from report import ReportService
from config import Config

def pause():
    input("\nPresiona ENTER para continuar...")

def load_csv(repo: CsvVisitRepository, customers_repo: InMemoryCustomerRepository | None):
    try:
        repo.load()
        customers = repo.get_customers()
        if customers_repo is None:
            customers_repo = InMemoryCustomerRepository(customers)
        else:
            customers_repo._customers = customers  # refrescar
        print(f"Cargadas {len(repo.get_reservations())} reservas y {len(customers)} clientes.")
        return customers_repo
    except Exception as e:
        print(f"Error al cargar CSV: {e}")
        return customers_repo

def print_rules():
    cfg = Config.get_instance()
    print("\nReglas actuales (ordenadas por prioridad):")
    for i, r in enumerate(cfg.get_rules(), start=1):
        print(f"{i}. window={r.window_months}m min_visits={r.min_visits} -> {r.resulting_tier.name}")

def configure_rules():
    print_rules()
    print("\nConfigurar nuevas reglas (deja vacío para terminar).")
    rules: List[LoyaltyRule] = []
    while True:
        s = input("Ventana en meses (ej. 3) [ENTER para terminar]: ").strip()
        if not s:
            break
        try:
            w = int(s)
            mv = int(input("Min visitas en la ventana: ").strip())
            tier_name = input("Nombre de la categoría (ej. VIP, Super VIP): ").strip() or "VIP"
            priority = int(input("Prioridad (entero, mayor = más alto) [sugerido 1..3]: ").strip() or "1")
            rules.append(LoyaltyRule(min_visits=mv, window_months=w, resulting_tier=LoyaltyTier(tier_name, priority)))
        except ValueError:
            print("Entrada inválida, intenta nuevamente.")
    if rules:
        Config.get_instance().set_rules(rules)
        print("Reglas actualizadas.")
    else:
        print("No se modificaron reglas.")

def ensure_engine(repo: CsvVisitRepository, customers_repo: InMemoryCustomerRepository | None) -> LoyaltyEngine | None:
    if customers_repo is None:
        print("Primero carga el CSV (opción 1).")
        return None
    cfg = Config.get_instance()
    strategy = VisitsInWindowStrategy(rules_desc=cfg.get_rules(), window_months=3, unique_per_day=True)
    return LoyaltyEngine(strategy=strategy, repo=repo, customers=customers_repo)

def main():
    path = input("Ruta del CSV de reservas (ej. sample_data/reservas.csv): ").strip() or "sample_data/reservas.csv"
    repo = CsvVisitRepository(path)
    customers_repo = None

    while True:
        print("\n=== Sistema de Fidelización de Clientes (Python/POO) ===")
        print("[1] Importar reservas (CSV)")
        print("[2] Configurar reglas de fidelización")
        print("[3] Buscar cliente por ID y ver categoría actual")
        print("[4] Listar clientes por categoría actual")
        print("[5] Reporte: visitas por mes (últimos N) de un cliente")
        print("[6] Ranking top clientes (últimos N meses)")
        print("[7] Exportar ranking a CSV")
        print("[0] Salir")

        choice = input("Elige una opción: ").strip()
        if choice == "1":
            customers_repo = load_csv(repo, customers_repo); pause()
        elif choice == "2":
            configure_rules(); pause()
        elif choice == "3":
            eng = ensure_engine(repo, customers_repo)
            if eng:
                cid = input("ID del cliente: ").strip()
                c = customers_repo.find_by_id(cid)
                if not c:
                    print("Cliente no encontrado.")
                else:
                    tier = eng.classify(c, date.today())
                    print(f"Cliente {c.name} -> Categoría actual: {tier.name}")
            pause()
        elif choice == "4":
            eng = ensure_engine(repo, customers_repo)
            if eng:
                as_of = date.today()
                tiers = {}
                for c in customers_repo.find_all():
                    t = eng.classify(c, as_of).name
                    tiers.setdefault(t, []).append(c)
                for tname, lst in sorted(tiers.items(), key=lambda kv: kv[0]):
                    print(f"\n[{tname}]")
                    for c in lst:
                        print(f"- {c.id} {c.name}")
            pause()
        elif choice == "5":
            if customers_repo is None:
                print("Primero carga el CSV (opción 1)."); pause(); continue
            cid = input("ID del cliente: ").strip()
            c = customers_repo.find_by_id(cid)
            if not c:
                print("Cliente no encontrado."); pause(); continue
            months = int(input("¿Cuántos meses atrás? (ej. 6): ").strip() or "6")
            svc = ReportService(repo, customers_repo)
            data = svc.visits_by_month(c, months, date.today())
            print(f"\nVisitas por mes de {c.name}:")
            for (y, m), cnt in sorted(data.items()):
                print(f"- {y}-{m:02d}: {cnt}")
            pause()
        elif choice == "6":
            if customers_repo is None:
                print("Primero carga el CSV (opción 1)."); pause(); continue
            months = int(input("¿Últimos N meses? (ej. 3): ").strip() or "3")
            svc = ReportService(repo, customers_repo)
            rows = svc.ranking_top_customers(months, date.today())
            print("\nRanking:")
            for i, (c, v) in enumerate(rows, start=1):
                print(f"{i}. {c.name} ({c.id}) - {v} visitas")
            pause()
        elif choice == "7":
            if customers_repo is None:
                print("Primero carga el CSV (opción 1)."); pause(); continue
            months = int(input("¿Últimos N meses? (ej. 3): ").strip() or "3")
            out_path = input("Ruta de salida CSV (ej. ranking.csv): ").strip() or "ranking.csv"
            svc = ReportService(repo, customers_repo)
            rows = svc.ranking_top_customers(months, date.today())
            svc.export_ranking_csv(rows, out_path)
            print(f"Exportado a {out_path}")
            pause()
        elif choice == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
