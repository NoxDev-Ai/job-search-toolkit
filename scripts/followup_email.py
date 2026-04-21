#!/usr/bin/env python3
"""Follow-up Email Generator - Generate professional follow-up emails.

Creates templates for various job search scenarios: after applying,
after interview, status check-in, thank you, and more.

Usage:
    python followup_email.py generate --type "after-interview" --company "Google"
    python followup_email.py generate --type "after-interview" --company "Google" --interviewer "Jane Smith"
    python followup_email.py generate --type "check-in" --company "Acme" --days 7
    python followup_email.py list
"""
import argparse
import json
import sys
from datetime import date

EMAIL_TEMPLATES = {
    "after-applying": {
        "name": "After Applying",
        "subject": "Application for {role} - {your_name}",
        "body": """Dear {hiring_manager},

I recently applied for the {role} position at {company} and wanted to briefly introduce myself.

{personal_connection}

I am very enthusiastic about the opportunity to join {company} and contribute to your team. My experience in {key_skills} aligns well with the requirements of this role.

I have attached my resume for your reference. I would welcome the opportunity to discuss how I can add value to {company}.

Thank you for your time and consideration.

Best regards,
{your_name}
{your_email}
{your_phone}
{your_linkedin}"""
    },
    "after-interview": {
        "name": "After Interview (Thank You)",
        "subject": "Thank You - {role} Interview - {your_name}",
        "body": """Dear {interviewer},

Thank you so much for taking the time to speak with me today about the {role} position at {company}.

{specific_discussion}

Our conversation reinforced my interest in joining {company}. I am particularly excited about {excitement_point} and I am confident that my background in {key_skills} would allow me to contribute meaningfully to your team.

Please feel free to reach out if you need any additional information from me. I look forward to hearing about the next steps.

Thank you again for the opportunity.

Best regards,
{your_name}
{your_email}
{your_phone}"""
    },
    "check-in": {
        "name": "Status Check-in",
        "subject": "Following Up - {role} Application - {your_name}",
        "body": """Dear {hiring_manager},

I hope this message finds you well. I am writing to follow up on my application for the {role} position at {company}, which I submitted {days_ago} days ago.

I remain very interested in this opportunity and would love to know if there are any updates on the hiring timeline. I am happy to provide any additional information that might be helpful.

Thank you for your time and consideration.

Best regards,
{your_name}
{your_email}
{your_phone}"""
    },
    "offer-accept": {
        "name": "Accept Offer",
        "subject": "Offer Acceptance - {role} - {your_name}",
        "body": """Dear {hiring_manager},

I am delighted to formally accept the offer for the {role} position at {company}.

{offer_details}

I am excited to join the team and look forward to contributing to {company}'s success. Please let me know if there is any additional paperwork or information you need from me before my start date.

Thank you again for this wonderful opportunity.

Best regards,
{your_name}
{your_email}
{your_phone}"""
    },
    "offer-decline": {
        "name": "Decline Offer (Professional)",
        "subject": "Regarding {role} Offer - {your_name}",
        "body": """Dear {hiring_manager},

Thank you very much for offering me the {role} position at {company}. I truly appreciate the time and effort you and the team invested in the interview process.

After careful consideration, I have decided to pursue another opportunity that more closely aligns with my current career goals.

This was not an easy decision, as I was very impressed with {company} and the team. I hope our paths may cross again in the future.

Wishing you and the team continued success.

Best regards,
{your_name}
{your_email}"""
    },
    "networking": {
        "name": "Networking / Referral Request",
        "subject": "Connecting - {your_name} / {role} at {company}",
        "body": """Hi {contact_name},

{connection_context}

I noticed that {company} has an opening for a {role} position and I am very interested in learning more. Given your experience at the company, I would love to hear your perspective on the team and culture.

{ask}

I completely understand if you are too busy, but even a brief 15-minute chat would be incredibly helpful. I have attached my resume for reference.

Thank you for your time,
{your_name}
{your_email}
{your_phone}
{your_linkedin}"""
    }
}


def generate_email(args):
    templates = EMAIL_TEMPLATES
    email_type = args.type
    if email_type not in templates:
        print(f"Email type '{email_type}' not found. Available:")
        for name, tmpl in templates.items():
            print(f"  {name}: {tmpl['name']}")
        sys.exit(1)
    template = templates[email_type]
    variables = {
        "hiring_manager": args.hiring_manager or "Hiring Manager",
        "interviewer": args.interviewer or args.hiring_manager or "Interview Team",
        "role": args.role or "[Role]",
        "company": args.company or "[Company]",
        "your_name": args.your_name or "[Your Name]",
        "your_email": args.your_email or "[Your Email]",
        "your_phone": args.your_phone or "[Your Phone]",
        "your_linkedin": args.your_linkedin or "[LinkedIn URL]",
        "contact_name": args.contact or "[Contact Name]",
        "days_ago": str(args.days or 7),
        "personal_connection": args.personal_connection or "[How you found the role / referral]",
        "key_skills": args.skills or "[Your key skills]",
        "specific_discussion": args.discussion or "[Something specific you discussed in the interview]",
        "excitement_point": args.excitement or "[What excites you about the role]",
        "offer_details": args.offer_details or "[Salary, start date, any negotiated terms]",
        "connection_context": args.connection_context or "[How you know this person / met]",
        "ask": args.ask or "Would you be open to a quick chat about your experience at the company?"
    }
    subject = template["subject"].format(**variables)
    body = template["body"].format(**variables)
    if args.format == "json":
        print(json.dumps({"subject": subject, "body": body, "type": template["name"]}, indent=2))
    else:
        print(f"Subject: {subject}\n")
        print(body)
    if args.output:
        with open(args.output, "w") as f:
            f.write(f"Subject: {subject}\n\n{body}")
        print(f"\nEmail saved to {args.output}")


def cmd_list(args):
    print("Available follow-up email templates:\n")
    for name, tmpl in EMAIL_TEMPLATES.items():
        print(f"  {name}: {tmpl['name']}")
        print(f"    Subject: {tmpl['subject'][:60]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate professional follow-up emails for job search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    gen_p = subparsers.add_parser("generate", help="Generate an email")
    gen_p.add_argument("--type", required=True, choices=list(EMAIL_TEMPLATES.keys()))
    gen_p.add_argument("--company")
    gen_p.add_argument("--role")
    gen_p.add_argument("--hiring-manager")
    gen_p.add_argument("--interviewer")
    gen_p.add_argument("--contact")
    gen_p.add_argument("--your-name")
    gen_p.add_argument("--your-email")
    gen_p.add_argument("--your-phone")
    gen_p.add_argument("--your-linkedin")
    gen_p.add_argument("--days", type=int, help="Days since application")
    gen_p.add_argument("--skills")
    gen_p.add_argument("--discussion")
    gen_p.add_argument("--excitement")
    gen_p.add_argument("--personal-connection")
    gen_p.add_argument("--offer-details")
    gen_p.add_argument("--connection-context")
    gen_p.add_argument("--ask")
    gen_p.add_argument("--format", choices=["text", "json"], default="text")
    gen_p.add_argument("--output", help="Output file path")
    gen_p.set_defaults(func=generate_email)

    list_p = subparsers.add_parser("list", help="List email templates")
    list_p.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
