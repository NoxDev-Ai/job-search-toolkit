# Job Search Toolkit

6 standalone Python scripts to automate and streamline your job search. No dependencies, no accounts, no subscriptions -- just practical tools that work offline.

## What's Inside

| Script | What It Does |
|--------|-------------|
| `job_tracker.py` | Track all your applications in CSV with status, salary, follow-ups |
| `cover_letter_generator.py` | Generate customized cover letters from templates |
| `resume_keyword_matcher.py` | Compare your resume against job descriptions, find missing keywords |
| `salary_calculator.py` | Calculate take-home pay and compare job offers |
| `interview_prep.py` | Generate role-specific interview questions, track prep progress |
| `followup_email.py` | Professional email templates for every job search scenario |

## Quick Start

```bash
# Track a job application
python job_tracker.py add --company "Google" --role "SWE" --salary-min 150000 --salary-max 200000

# List all applications
python job_tracker.py list

# Generate a cover letter
python cover_letter_generator.py generate --company "Google" --role "Software Engineer" --your-name "Jane Doe"

# Match resume against job description
python resume_keyword_matcher.py match --resume my_resume.txt --job-desc job_posting.txt

# Calculate take-home pay
python salary_calculator.py calc --salary 120000 --state CA

# Generate interview questions
python interview_prep.py generate --role "Software Engineer" --company "Google"

# Generate a follow-up email
python followup_email.py generate --type after-interview --company "Google" --interviewer "Jane Smith"
```

## Requirements

Python 3.6+ (stdlib only, no pip install needed)

## Each Script Has

- `--help` flag with full documentation
- `--format json` option for data export
- Error handling for missing files and invalid input

## Pricing

- **Launch price**: $9
- **Standard price**: $19
- "Name a fair price" option available (minimum $0)

## License

Personal use license. Share with friends but don't resell.
