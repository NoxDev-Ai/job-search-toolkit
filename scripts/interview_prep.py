#!/usr/bin/env python3
"""Interview Prep Generator - Generate interview questions from job descriptions.

Creates role-specific interview questions and tracks your preparation progress.

Usage:
    python interview_prep.py generate --role "Software Engineer" --company "Google"
    python interview_prep.py generate --role "SWE" --job-desc job.txt
    python interview_prep.py generate --role "PM" --type behavioral
    python interview_prep.py track --add "Explain REST APIs" --done
    python interview_prep.py track --list
"""
import argparse
import csv
import json
import os
import random
import sys

TRACKER_FILE = os.path.expanduser("~/.interview_prep.csv")

QUESTION_BANKS = {
    "technical": [
        "Walk me through how you would design a {domain} system from scratch.",
        "How would you optimize a slow {domain} process?",
        "Explain the difference between {concept_a} and {concept_b}.",
        "Describe a time you had to debug a complex {domain} issue.",
        "How do you ensure code quality in your {domain} projects?",
        "What {domain} tools and technologies are you most proficient in?",
        "Explain how you would handle scaling a {domain} application to 1M users.",
        "What is your approach to testing {domain} systems?",
        "Describe your experience with {concept_a} in production.",
        "How do you stay current with {domain} best practices?"
    ],
    "behavioral": [
        "Tell me about a time you disagreed with a teammate. How did you handle it?",
        "Describe a project you led from start to finish.",
        "Tell me about a time you failed. What did you learn?",
        "Describe a situation where you had to learn something quickly.",
        "Tell me about a time you had to deal with a difficult stakeholder.",
        "Describe a time you went above and beyond for a project.",
        "Tell me about a time you had to prioritize competing deadlines.",
        "Describe a time you received critical feedback. How did you respond?",
        "Tell me about a time you had to convince someone of your approach.",
        "Describe a situation where you had to work with incomplete information."
    ],
    "company": [
        "Why do you want to work at {company}?",
        "What do you know about {company}'s products/services?",
        "How does your experience align with {company}'s mission?",
        "What excites you most about this role at {company}?",
        "Where do you see yourself in 5 years, and how does {company} fit?",
        "What questions do you have for us about {company}?",
        "How would you contribute to {company}'s culture?",
        "What do you think is {company}'s biggest challenge right now?"
    ],
    "role_specific": {
        "engineer": [
            "Explain the difference between REST and GraphQL.",
            "How would you design a URL shortening service?",
            "What is your experience with microservices architecture?",
            "How do you approach code reviews?",
            "Explain how you would implement authentication and authorization.",
            "Describe your CI/CD pipeline experience.",
            "How do you handle database migrations in production?",
            "What monitoring and alerting tools have you used?"
        ],
        "manager": [
            "How do you handle underperforming team members?",
            "Describe your approach to sprint planning.",
            "How do you balance technical debt with feature delivery?",
            "Tell me about your experience with stakeholder management.",
            "How do you measure team success?"
        ],
        "designer": [
            "Walk me through your design process.",
            "How do you handle design criticism?",
            "Describe a project where user research changed your design.",
            "How do you collaborate with engineers on implementation?",
            "What design systems have you worked with?"
        ],
        "data": [
            "How do you handle missing or dirty data?",
            "Explain the bias-variance tradeoff.",
            "Describe your experience with A/B testing.",
            "How do you communicate technical results to non-technical stakeholders?",
            "What is your approach to feature engineering?"
        ]
    }
}


def get_questions(args):
    questions = []
    role_lower = args.role.lower()
    qtype = args.type or "all"
    if qtype in ("all", "technical"):
        domain = "software" if "engineer" in role_lower or "developer" in role_lower else role_lower
        concept_a = "SQL" if "engineer" in role_lower else "strategy"
        concept_b = "NoSQL" if "engineer" in role_lower else "tactics"
        for q in QUESTION_BANKS["technical"]:
            questions.append(q.format(domain=domain, concept_a=concept_a, concept_b=concept_b))
    if qtype in ("all", "behavioral"):
        questions.extend(QUESTION_BANKS["behavioral"])
    if qtype in ("all", "company") and args.company:
        for q in QUESTION_BANKS["company"]:
            questions.append(q.format(company=args.company))
    if qtype in ("all", "role"):
        role_key = None
        for key in QUESTION_BANKS["role_specific"]:
            if key in role_lower:
                role_key = key
                break
        if role_key:
            questions.extend(QUESTION_BANKS["role_specific"][role_key])
    if args.job_desc:
        try:
            with open(args.job_desc, "r") as f:
                text = f.read()
                questions.append(f"Based on the job description, how would you approach [key requirement]?")
        except FileNotFoundError:
            print(f"Job description file not found: {args.job_desc}", file=sys.stderr)
            sys.exit(1)
    if args.num and args.num < len(questions):
        questions = random.sample(questions, args.num)
    if args.format == "json":
        print(json.dumps(questions, indent=2))
    else:
        print(f"=== Interview Questions for {args.role}{' at ' + args.company if args.company else ''} ===")
        print(f"(Type: {qtype})\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        print(f"\nTotal: {len(questions)} questions")


def ensure_tracker():
    if not os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "question", "status", "notes", "date"])
            writer.writeheader()


def cmd_track(args):
    ensure_tracker()
    if args.add:
        with open(TRACKER_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "question", "status", "notes", "date"])
            rows = list(csv.DictReader(open(TRACKER_FILE)))
            new_id = len(rows) + 1
            writer.writerow({
                "id": new_id,
                "question": args.add,
                "status": "done" if args.done else "pending",
                "notes": args.notes or "",
                "date": ""
            })
        print(f"Added question #{len(csv.DictReader(open(TRACKER_FILE)))+1}: {args.add[:50]}...")
    elif args.list:
        with open(TRACKER_FILE, "r") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            print("No tracked questions.")
            return
        if args.status:
            rows = [r for r in rows if r["status"] == args.status]
        if args.format == "json":
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'ID':<5} {'Status':<10} {'Question'}")
            print("-" * 60)
            for r in rows:
                print(f"{r['id']:<5} {r['status']:<10} {r['question'][:50]}")
    elif args.update:
        with open(TRACKER_FILE, "r") as f:
            rows = list(csv.DictReader(f))
        updated = False
        for row in rows:
            if row["id"] == str(args.update):
                if args.status:
                    row["status"] = args.status
                if args.notes:
                    row["notes"] = args.notes
                updated = True
        if updated:
            with open(TRACKER_FILE, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "question", "status", "notes", "date"])
                writer.writeheader()
                writer.writerows(rows)
            print(f"Updated question #{args.update}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate interview questions and track preparation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    gen_p = subparsers.add_parser("generate", help="Generate questions")
    gen_p.add_argument("--role", required=True)
    gen_p.add_argument("--company")
    gen_p.add_argument("--job-desc")
    gen_p.add_argument("--type", choices=["technical", "behavioral", "company", "role", "all"], default="all")
    gen_p.add_argument("--num", type=int, help="Number of questions")
    gen_p.add_argument("--format", choices=["text", "json"], default="text")
    gen_p.set_defaults(func=get_questions)

    track_p = subparsers.add_parser("track", help="Track prep progress")
    track_p.add_argument("--add", help="Add a question to track")
    track_p.add_argument("--list", action="store_true")
    track_p.add_argument("--update", type=int, help="Update question ID")
    track_p.add_argument("--status", choices=["pending", "done"], help="New status")
    track_p.add_argument("--done", action="store_true", help="Mark as done (with --add)")
    track_p.add_argument("--notes")
    track_p.add_argument("--format", choices=["text", "json"], default="text")
    track_p.set_defaults(func=cmd_track)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
