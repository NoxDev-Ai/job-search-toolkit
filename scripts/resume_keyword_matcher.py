#!/usr/bin/env python3
"""Resume Keyword Matcher - Compare resume against job descriptions.

Identifies missing keywords and skills from job postings to help tailor
your resume for ATS systems and hiring managers.

Usage:
    python resume_keyword_matcher.py match --resume resume.txt --job-desc job.txt
    python resume_keyword_matcher.py match --resume resume.txt --job-desc job.txt --format json
    python resume_keyword_matcher.py extract --resume resume.txt
    python resume_keyword_matcher.py extract --job-desc job.txt
"""
import argparse
import json
import re
import sys
from collections import Counter

COMMON_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "has", "have", "been", "with", "this",
    "that", "from", "they", "will", "each", "about", "how", "their", "which",
    "when", "what", "where", "who", "why", "would", "make", "like", "just",
    "over", "such", "than", "them", "very", "also", "into", "time", "work",
    "more", "some", "other", "use", "may", "need", "use", "using", "used",
    "ability", "skills", "experience", "role", "team", "company", "position",
    "job", "candidate", "requirements", "qualifications", "preferred",
    "responsibilities", "including", "related", "required", "strong",
    "excellent", "proficient", "familiar", "knowledge", "understanding",
    "plus", "desired", "must", "should", "minimum", "years", "level",
    "ensure", "support", "develop", "manage", "lead", "create", "build",
    "design", "implement", "maintain", "improve", "analyze", "review",
    "provide", "collaborate", "communicate", "demonstrate", "drive",
    "apply", "help", "participate", "contribute"
}

TECH_KEYWORDS = {
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "ruby", "swift", "kotlin", "php", "sql", "html", "css", "react", "angular",
    "vue", "node", "django", "flask", "fastapi", "spring", "rails",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins",
    "git", "linux", "macos", "windows", "agile", "scrum", "kanban",
    "ml", "ai", "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
    "rest", "graphql", "api", "microservices", "serverless",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "ci/cd", "devops", "sre", "security", "testing", "tdd", "bdd"
}


def extract_words(text):
    words = re.findall(r'[a-zA-Z][a-zA-Z+\-#.]+[a-zA-Z]', text.lower())
    return [w for w in words if w not in COMMON_WORDS and len(w) > 2]


def extract_phrases(text):
    phrases = []
    for tech in TECH_KEYWORDS:
        if tech.lower() in text.lower():
            phrases.append(tech)
    return phrases


def cmd_extract(args):
    if args.resume:
        with open(args.resume, "r") as f:
            text = f.read()
    elif args.job_desc:
        with open(args.job_desc, "r") as f:
            text = f.read()
    else:
        print("Provide --resume or --job-desc", file=sys.stderr)
        sys.exit(1)
    words = extract_words(text)
    tech = extract_phrases(text)
    word_counts = Counter(words).most_common(args.top or 30)
    if args.format == "json":
        print(json.dumps({"words": dict(word_counts), "tech_keywords": tech}, indent=2))
    else:
        print("=== Top Keywords ===")
        for word, count in word_counts:
            print(f"  {word}: {count}")
        print(f"\n=== Tech Keywords Found ({len(tech)}) ===")
        for t in tech:
            print(f"  {t}")


def cmd_match(args):
    with open(args.resume, "r") as f:
        resume_text = f.read()
    with open(args.job_desc, "r") as f:
        job_text = f.read()
    resume_words = set(extract_words(resume_text))
    resume_tech = set(extract_phrases(resume_text))
    job_words = set(extract_words(job_text))
    job_tech = set(extract_phrases(job_text))
    missing_words = job_words - resume_words
    missing_tech = job_tech - resume_tech
    matched_words = job_words & resume_words
    matched_tech = job_tech & resume_tech
    all_job_keywords = job_words | job_tech
    all_matched = matched_words | matched_tech
    match_rate = len(all_matched) / len(all_job_keywords) * 100 if all_job_keywords else 0
    if args.format == "json":
        result = {
            "match_rate": round(match_rate, 1),
            "matched_tech": sorted(matched_tech),
            "missing_tech": sorted(missing_tech),
            "matched_keywords": sorted(matched_words)[:20],
            "missing_keywords": sorted(missing_words)[:30]
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Resume vs Job Description Match ===")
        print(f"Match rate: {match_rate:.1f}%")
        print(f"\nMatched Tech ({len(matched_tech)}):")
        for t in sorted(matched_tech):
            print(f"  [x] {t}")
        print(f"\nMissing Tech ({len(missing_tech)}):")
        for t in sorted(missing_tech):
            print(f"  [ ] {t}")
        print(f"\nMissing Keywords (top {min(20, len(missing_words))}):")
        for w in sorted(missing_words)[:20]:
            print(f"  [ ] {w}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare resume against job descriptions for keyword matching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    match_p = subparsers.add_parser("match", help="Match resume to job description")
    match_p.add_argument("--resume", required=True, help="Resume text file")
    match_p.add_argument("--job-desc", required=True, help="Job description file")
    match_p.add_argument("--format", choices=["text", "json"], default="text")
    match_p.set_defaults(func=cmd_match)

    extract_p = subparsers.add_parser("extract", help="Extract keywords")
    extract_p.add_argument("--resume", help="Resume text file")
    extract_p.add_argument("--job-desc", help="Job description file")
    extract_p.add_argument("--top", type=int, default=30)
    extract_p.add_argument("--format", choices=["text", "json"], default="text")
    extract_p.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
