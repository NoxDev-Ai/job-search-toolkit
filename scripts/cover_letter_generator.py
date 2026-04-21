#!/usr/bin/env python3
"""Cover Letter Generator - Generate customized cover letters from templates.

Creates professional cover letters by combining your background info with
job-specific details from the job description.

Usage:
    python cover_letter_generator.py generate --company "Google" --role "Software Engineer"
    python cover_letter_generator.py generate --company "Google" --role "SWE" --job-desc job.txt
    python cover_letter_generator.py generate --company "Google" --role "SWE" --format html
    python cover_letter_generator.py template --show
"""
import argparse
import json
import os
import sys

DEFAULT_TEMPLATE_DIR = os.path.expanduser("~/.job_search_toolkit")
TEMPLATES_FILE = os.path.join(DEFAULT_TEMPLATE_DIR, "cover_templates.json")

DEFAULT_TEMPLATES = {
    "standard": {
        "name": "Standard Professional",
        "body": """Dear {hiring_manager},

I am writing to express my strong interest in the {role} position at {company}. {opening}

With my background in {skills}, I believe I am well-suited to contribute to your team. {experience}

{company_connection}

I would welcome the opportunity to discuss how my skills and experience align with {company}'s needs. Thank you for your time and consideration.

Sincerely,
{your_name}
{your_phone}
{your_email}"""
    },
    "passionate": {
        "name": "Passionate & Enthusiastic",
        "body": """Dear {hiring_manager},

When I saw the {role} opening at {company}, I knew I had to apply. {opening}

I have been following {company}'s work for some time, and I am particularly excited about {company_connection}. Here is why I believe I am the right fit:

{experience}

I would love to bring my passion for {skills} to {company}. Thank you for considering my application.

Warm regards,
{your_name}
{your_phone}
{your_email}"""
    },
    "brief": {
        "name": "Short & Direct",
        "body": """Dear {hiring_manager},

I am applying for the {role} position at {company}. {opening}

My relevant experience includes {experience}.

I would welcome a chance to discuss how I can contribute to your team. Thank you for your consideration.

Best,
{your_name}
{your_phone}
{your_email}"""
    }
}


def get_templates():
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_TEMPLATES


def ensure_template_dir():
    os.makedirs(DEFAULT_TEMPLATE_DIR, exist_ok=True)


def generate_letter(args):
    templates = get_templates()
    template_name = args.template
    if template_name not in templates:
        print(f"Template '{template_name}' not found. Available: {', '.join(templates.keys())}")
        sys.exit(1)
    template = templates[template_name]
    variables = {
        "hiring_manager": args.hiring_manager or "Hiring Manager",
        "role": args.role,
        "company": args.company,
        "your_name": args.your_name or "[Your Name]",
        "your_phone": args.your_phone or "[Your Phone]",
        "your_email": args.your_email or "[Your Email]",
        "opening": args.opening or f"With {args.years_exp or 'X'} years of experience in [your field], I am excited about the opportunity to join {args.company} as a {args.role}.",
        "skills": args.skills or "[Your key skills]",
        "experience": args.experience or "[Your relevant experience]",
        "company_connection": args.company_connection or "[Why you are excited about this company]"
    }
    if args.job_desc:
        try:
            with open(args.job_desc, "r") as f:
                variables["job_description"] = f.read()
        except FileNotFoundError:
            print(f"Job description file not found: {args.job_desc}", file=sys.stderr)
            sys.exit(1)
    letter = template["body"].format(**variables)
    if args.format == "html":
        letter = "<html><head><style>body{{font-family:Arial,sans-serif;max-width:700px;margin:40px auto;line-height:1.6;}}</style></head><body><pre>" + letter + "</pre></body></html>"
    if args.output:
        with open(args.output, "w") as f:
            f.write(letter)
        print(f"Cover letter saved to {args.output}")
    else:
        print(letter)


def cmd_template(args):
    templates = get_templates()
    if args.show:
        print("Available cover letter templates:\n")
        for name, tmpl in templates.items():
            print(f"  {name}: {tmpl['name']}")
            print(f"    {tmpl['body'][:100]}...\n")
    elif args.edit:
        ensure_template_dir()
        print("To edit templates, modify:", TEMPLATES_FILE)
        if not os.path.exists(TEMPLATES_FILE):
            with open(TEMPLATES_FILE, "w") as f:
                json.dump(DEFAULT_TEMPLATES, f, indent=2)
            print(f"Created default templates file: {TEMPLATES_FILE}")
    elif args.list:
        for name in templates:
            print(name)


def main():
    parser = argparse.ArgumentParser(
        description="Generate customized cover letters from templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    gen_p = subparsers.add_parser("generate", help="Generate a cover letter")
    gen_p.add_argument("--company", required=True)
    gen_p.add_argument("--role", required=True)
    gen_p.add_argument("--hiring-manager")
    gen_p.add_argument("--your-name")
    gen_p.add_argument("--your-phone")
    gen_p.add_argument("--your-email")
    gen_p.add_argument("--years-exp", help="Years of experience")
    gen_p.add_argument("--skills", help="Your key skills")
    gen_p.add_argument("--experience", help="Your relevant experience")
    gen_p.add_argument("--opening", help="Opening sentence")
    gen_p.add_argument("--company-connection")
    gen_p.add_argument("--job-desc", help="Path to job description file")
    gen_p.add_argument("--template", default="standard")
    gen_p.add_argument("--format", choices=["text", "html"], default="text")
    gen_p.add_argument("--output", help="Output file path")
    gen_p.set_defaults(func=generate_letter)

    tmpl_p = subparsers.add_parser("template", help="Manage templates")
    tmpl_p.add_argument("--show", action="store_true")
    tmpl_p.add_argument("--edit", action="store_true")
    tmpl_p.add_argument("--list", action="store_true")
    tmpl_p.set_defaults(func=cmd_template)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
