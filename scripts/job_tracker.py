#!/usr/bin/env python3
"""Job Application Tracker - Track job applications in CSV format.

Track applications with company, role, date, status, follow-up dates, salary range, and notes.
All data stored in a simple CSV file for portability.

Usage:
    python job_tracker.py add --company "Google" --role "SWE" --salary-min 150000 --salary-max 200000
    python job_tracker.py list
    python job_tracker.py list --status "Applied"
    python job_tracker.py update 3 --status "Interview" --notes "Great culture fit"
    python job_tracker.py stats
    python job_tracker.py export --format json
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

DEFAULT_DB = os.path.expanduser("~/.job_tracker.csv")

FIELDS = [
    "id", "date_applied", "company", "role", "location", "url",
    "salary_min", "salary_max", "status", "follow_up_date",
    "contact_name", "contact_email", "notes", "date_updated"
]

STATUSES = [
    "Researching", "Applied", "Screening", "Interview",
    "Offer", "Rejected", "Withdrawn", "Accepted"
]


def get_db_path(args):
    return args.db if args.db else DEFAULT_DB


def ensure_db(db_path):
    if not os.path.exists(db_path):
        with open(db_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
    return db_path


def next_id(db_path):
    rows = read_all(db_path)
    if not rows:
        return 1
    return max(int(r["id"]) for r in rows) + 1


def read_all(db_path):
    ensure_db(db_path)
    with open(db_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_all(db_path, rows):
    with open(db_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def cmd_add(args):
    db_path = get_db_path(args)
    ensure_db(db_path)
    new_id = next_id(db_path)
    row = {
        "id": str(new_id),
        "date_applied": args.date or date.today().isoformat(),
        "company": args.company,
        "role": args.role,
        "location": args.location or "",
        "url": args.url or "",
        "salary_min": str(args.salary_min or ""),
        "salary_max": str(args.salary_max or ""),
        "status": args.status or "Applied",
        "follow_up_date": args.follow_up or "",
        "contact_name": args.contact or "",
        "contact_email": args.contact_email or "",
        "notes": args.notes or "",
        "date_updated": datetime.now().isoformat()
    }
    with open(db_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(row)
    print(f"Added job #{new_id}: {row['company']} - {row['role']}")


def cmd_list(args):
    db_path = get_db_path(args)
    rows = read_all(db_path)
    if args.status:
        rows = [r for r in rows if r["status"].lower() == args.status.lower()]
    if args.company:
        rows = [r for r in rows if args.company.lower() in r["company"].lower()]
    if args.sort_by == "date":
        rows.sort(key=lambda r: r["date_applied"], reverse=True)
    elif args.sort_by == "salary":
        rows.sort(key=lambda r: int(r["salary_max"] or 0), reverse=True)
    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print("No applications found.")
        return
    print(f"{'ID':<5} {'Date':<12} {'Company':<25} {'Role':<20} {'Status':<12} {'Salary':<15}")
    print("-" * 90)
    for r in rows:
        salary = ""
        if r["salary_min"] and r["salary_max"]:
            salary = f"${int(r['salary_min'])/1000:.0f}k-${int(r['salary_max'])/1000:.0f}k"
        elif r["salary_min"]:
            salary = f"${int(r['salary_min'])/1000:.0f}k+"
        print(f"{r['id']:<5} {r['date_applied']:<12} {r['company']:<25} {r['role']:<20} {r['status']:<12} {salary}")
    print(f"\nTotal: {len(rows)} application(s)")


def cmd_update(args):
    db_path = get_db_path(args)
    rows = read_all(db_path)
    target_id = str(args.id)
    found = False
    for row in rows:
        if row["id"] == target_id:
            found = True
            if args.status:
                row["status"] = args.status
            if args.notes:
                row["notes"] = args.notes
            if args.follow_up:
                row["follow_up_date"] = args.follow_up
            if args.salary_min is not None:
                row["salary_min"] = str(args.salary_min)
            if args.salary_max is not None:
                row["salary_max"] = str(args.salary_max)
            row["date_updated"] = datetime.now().isoformat()
            break
    if found:
        write_all(db_path, rows)
        print(f"Updated job #{target_id}")
    else:
        print(f"Job #{target_id} not found", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args):
    db_path = get_db_path(args)
    rows = read_all(db_path)
    new_rows = [r for r in rows if r["id"] != str(args.id)]
    if len(new_rows) == len(rows):
        print(f"Job #{args.id} not found", file=sys.stderr)
        sys.exit(1)
    write_all(db_path, new_rows)
    print(f"Deleted job #{args.id}")


def cmd_stats(args):
    db_path = get_db_path(args)
    rows = read_all(db_path)
    if not rows:
        print("No applications tracked yet.")
        return
    total = len(rows)
    status_counts = {}
    for r in rows:
        status = r["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    salaries = [int(r["salary_max"]) for r in rows if r["salary_max"]]
    print("=== Job Search Statistics ===")
    print(f"Total applications: {total}")
    print()
    print("By Status:")
    for status in STATUSES:
        if status in status_counts:
            print(f"  {status}: {status_counts[status]}")
    print()
    if salaries:
        avg_salary = sum(salaries) / len(salaries)
        print(f"Salary ranges found: {len(salaries)} postings")
        print(f"Average max salary: ${avg_salary:,.0f}")
        print(f"Highest: ${max(salaries):,.0f}")
        print(f"Lowest: ${min(salaries):,.0f}")
    today = date.today().isoformat()
    followups = [r for r in rows if r["follow_up_date"] and r["follow_up_date"] <= today]
    if followups:
        print(f"\nOverdue follow-ups ({len(followups)}):")
        for r in followups:
            print(f"  #{r['id']} {r['company']} - {r['role']} (due: {r['follow_up_date']})")


def cmd_export(args):
    db_path = get_db_path(args)
    rows = read_all(db_path)
    if args.format == "json":
        print(json.dumps(rows, indent=2))
    else:
        print(f"{'ID':<5} {'Date':<12} {'Company':<25} {'Role':<20} {'Status':<12}")
        print("-" * 75)
        for r in rows:
            print(f"{r['id']:<5} {r['date_applied']:<12} {r['company']:<25} {r['role']:<20} {r['status']:<12}")


def main():
    parser = argparse.ArgumentParser(
        description="Track job applications in CSV format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--db", help="Path to CSV database (default: ~/.job_tracker.csv)")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    add_p = subparsers.add_parser("add", help="Add a job application")
    add_p.add_argument("--company", required=True)
    add_p.add_argument("--role", required=True)
    add_p.add_argument("--location")
    add_p.add_argument("--url")
    add_p.add_argument("--salary-min", type=int)
    add_p.add_argument("--salary-max", type=int)
    add_p.add_argument("--date", help="YYYY-MM-DD")
    add_p.add_argument("--status", choices=STATUSES, default="Applied")
    add_p.add_argument("--follow-up", help="YYYY-MM-DD")
    add_p.add_argument("--contact")
    add_p.add_argument("--contact-email")
    add_p.add_argument("--notes")
    add_p.set_defaults(func=cmd_add)

    list_p = subparsers.add_parser("list", help="List applications")
    list_p.add_argument("--status")
    list_p.add_argument("--company")
    list_p.add_argument("--sort-by", choices=["date", "salary"], default="date")
    list_p.add_argument("--format", choices=["text", "json"], default="text")
    list_p.set_defaults(func=cmd_list)

    update_p = subparsers.add_parser("update", help="Update application")
    update_p.add_argument("id", type=int)
    update_p.add_argument("--status", choices=STATUSES)
    update_p.add_argument("--notes")
    update_p.add_argument("--follow-up")
    update_p.add_argument("--salary-min", type=int)
    update_p.add_argument("--salary-max", type=int)
    update_p.set_defaults(func=cmd_update)

    delete_p = subparsers.add_parser("delete", help="Delete application")
    delete_p.add_argument("id", type=int)
    delete_p.set_defaults(func=cmd_delete)

    stats_p = subparsers.add_parser("stats", help="Show statistics")
    stats_p.set_defaults(func=cmd_stats)

    export_p = subparsers.add_parser("export", help="Export data")
    export_p.add_argument("--format", choices=["text", "json"], default="text")
    export_p.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
