# Quick Start Guide

## Job Tracker

```bash
# Add your first application
python job_tracker.py add --company "Google" --role "Software Engineer" --salary-min 150000 --salary-max 200000

# View all applications
python job_tracker.py list

# Update status
python job_tracker.py update 1 --status "Interview"

# See your stats
python job_tracker.py stats
```

## Cover Letter Generator

```bash
# Basic cover letter
python cover_letter_generator.py generate \
  --company "Google" \
  --role "Software Engineer" \
  --your-name "Jane Doe" \
  --your-email "jane@email.com"

# Save to file
python cover_letter_generator.py generate \
  --company "Acme" --role "Developer" \
  --your-name "Jane Doe" --output cover_letter.txt

# Use a different template
python cover_letter_generator.py generate --company "Startup" --role "PM" --template passionate
```

## Resume Keyword Matcher

```bash
# Create text files first
echo "Your resume content here" > resume.txt
echo "Job description here" > job.txt

# Find missing keywords
python resume_keyword_matcher.py match --resume resume.txt --job-desc job.txt
```

## Salary Calculator

```bash
# Single salary
python salary_calculator.py calc --salary 120000 --state CA

# Compare offers
python salary_calculator.py compare \
  --offer "Google:180000:CA:remote" \
  --offer "Startup:150000:NY:onsite:30:4"
```

## Interview Prep

```bash
# Generate questions
python interview_prep.py generate --role "Software Engineer" --company "Google"

# Track your prep
python interview_prep.py track --add "Explain REST APIs"
python interview_prep.py track --list
python interview_prep.py track --update 1 --status done
```

## Follow-up Emails

```bash
# After interview
python followup_email.py generate --type after-interview --company "Google" --interviewer "Jane"

# Check-in after 7 days
python followup_email.py generate --type check-in --company "Acme" --days 7

# Accept an offer
python followup_email.py generate --type offer-accept --company "Google" --role "SWE"
```
