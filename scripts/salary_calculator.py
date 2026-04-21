#!/usr/bin/env python3
"""Salary Calculator - Calculate take-home pay and compare job offers.

Factors in taxes, benefits, commute costs, and remote vs on-site to
compare total compensation across job offers.

Usage:
    python salary_calculator.py calc --salary 120000 --state CA
    python salary_calculator.py calc --salary 120000 --state CA --format json
    python salary_calculator.py compare --offer1 "CompanyA:120000:CA:remote" --offer2 "CompanyB:130000:NY:onsite:20:10"
"""
import argparse
import json
import sys

# Simplified 2024 federal tax brackets (single filer)
FEDERAL_BRACKETS = [
    (11600, 0.10),
    (47150, 0.12),
    (100525, 0.22),
    (191950, 0.24),
    (243725, 0.32),
    (609350, 0.35),
    (float("inf"), 0.37)
]

# Simplified state tax rates (approximate)
STATE_RATES = {
    "CA": 0.093, "NY": 0.0882, "TX": 0.0, "FL": 0.0, "WA": 0.0,
    "NV": 0.0, "SD": 0.0, "WY": 0.0, "AK": 0.0, "TN": 0.0,
    "NH": 0.0, "IL": 0.0495, "PA": 0.0307, "IN": 0.0323,
    "OH": 0.0399, "MI": 0.0425, "NC": 0.0475, "GA": 0.0575,
    "VA": 0.0575, "MA": 0.05, "NJ": 0.0897, "CT": 0.0699,
    "MD": 0.0575, "CO": 0.0463, "AZ": 0.045, "OR": 0.099,
}

FICA_RATE = 0.0765  # Social Security + Medicare


def calc_federal_tax(salary):
    tax = 0
    prev = 0
    for limit, rate in FEDERAL_BRACKETS:
        if salary > prev:
            taxable = min(salary, limit) - prev
            tax += taxable * rate
            prev = limit
        else:
            break
    return tax


def calc_take_home(args):
    salary = args.salary
    state = args.state.upper() if args.state else ""
    state_rate = STATE_RATES.get(state, 0.05)
    federal = calc_federal_tax(salary)
    state = salary * state_rate
    fica = salary * FICA_RATE
    total_tax = federal + state + fica
    take_home = salary - total_tax
    monthly = take_home / 12
    biweekly = take_home / 26
    if args.format == "json":
        result = {
            "gross_salary": salary,
            "state": state,
            "federal_tax": round(federal, 2),
            "state_tax": round(state, 2),
            "fica": round(fica, 2),
            "total_tax": round(total_tax, 2),
            "effective_rate": round(total_tax / salary * 100, 1),
            "take_home_annual": round(take_home, 2),
            "take_home_monthly": round(monthly, 2),
            "take_home_biweekly": round(biweekly, 2)
        }
        print(json.dumps(result, indent=2))
    else:
        print("=== Salary Breakdown ===")
        print(f"Gross salary: ${salary:,}")
        print(f"State: {state}")
        print(f"  Federal tax: ${federal:,.2f}")
        print(f"  State tax:   ${state:,.2f}")
        print(f"  FICA:        ${fica:,.2f}")
        print(f"  Total tax:   ${total_tax:,.2f}")
        print(f"  Effective rate: {total_tax/salary*100:.1f}%")
        print(f"\nTake-home pay:")
        print(f"  Annual:   ${take_home:,.2f}")
        print(f"  Monthly:  ${monthly:,.2f}")
        print(f"  Biweekly: ${biweekly:,.2f}")


def parse_offer(offer_str):
    parts = offer_str.split(":")
    name = parts[0]
    salary = int(parts[1])
    state = parts[2] if len(parts) > 2 else ""
    remote = len(parts) > 3 and parts[3].lower() == "remote"
    commute_miles = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
    commute_cost = int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0
    return name, salary, state, remote, commute_miles, commute_cost


def cmd_compare(args):
    offers = []
    for offer_str in args.offer:
        name, salary, state, remote, miles, cost = parse_offer(offer_str)
        state_rate = STATE_RATES.get(state.upper(), 0.05)
        federal = calc_federal_tax(salary)
        state_tax = salary * state_rate
        fica = salary * FICA_RATE
        total_tax = federal + state_tax + fica
        take_home = salary - total_tax
        annual_commute = 0
        if not remote:
            annual_commute = (miles * 2 * 250 * cost / 20) if cost else miles * 2 * 250 * 0.67
        annual_value = take_home - annual_commute
        offers.append({
            "name": name,
            "salary": salary,
            "state": state,
            "remote": remote,
            "take_home": round(take_home, 2),
            "commute_cost": round(annual_commute, 2),
            "net_value": round(annual_value, 2),
            "hourly": round(take_home / 2080, 2)
        })
    offers.sort(key=lambda x: x["net_value"], reverse=True)
    if args.format == "json":
        print(json.dumps(offers, indent=2))
    else:
        print("=== Job Offer Comparison ===\n")
        for i, o in enumerate(offers):
            marker = ">> BEST << " if i == 0 else ""
            print(f"{marker}{o['name']}")
            print(f"  Salary:      ${o['salary']:,}")
            print(f"  Take-home:   ${o['take_home']:,.2f}")
            print(f"  Commute:     ${o['commute_cost']:,.2f}/year")
            print(f"  Net value:   ${o['net_value']:,.2f}")
            print(f"  Hourly:      ${o['hourly']:.2f}")
            if o['remote']:
                print(f"  Remote:      Yes")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="Calculate take-home pay and compare job offers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    calc_p = subparsers.add_parser("calc", help="Calculate take-home pay")
    calc_p.add_argument("--salary", type=int, required=True)
    calc_p.add_argument("--state", help="State code (e.g., CA, NY, TX)")
    calc_p.add_argument("--format", choices=["text", "json"], default="text")
    calc_p.set_defaults(func=calc_take_home)

    comp_p = subparsers.add_parser("compare", help="Compare job offers")
    comp_p.add_argument("--offer", required=True, nargs="+",
        help="Format: Name:Salary:State:remote/onsite:commute_miles:cost_per_gallon")
    comp_p.add_argument("--format", choices=["text", "json"], default="text")
    comp_p.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
