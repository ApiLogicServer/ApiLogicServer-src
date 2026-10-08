#!/usr/bin/env python3
"""
Verify Behave step ordering for multi-param patterns.

Usage:
    cd test/api_logic_server_behave
    python check_step_order.py

This script checks if Behave step patterns are ordered from most specific
to most general, preventing Rule #0.5 violations that cause silent test failures.

Rule #0.5: Behave matches steps by FIRST pattern that fits.
More specific patterns MUST come before general ones.
"""
import re
import sys
from pathlib import Path


def check_step_order(steps_file):
    """
    Check if multi-item patterns come before single-item patterns.
    
    Returns list of issues found, or empty list if order is correct.
    """
    with open(steps_file) as f:
        lines = f.readlines()
    
    issues = []
    when_patterns = []
    
    for i, line in enumerate(lines, 1):
        # Look for @when patterns with parameters
        if match := re.match(r"@when\('.*with.*\{", line):
            # Calculate specificity score
            param_count = line.count('{')  # More parameters = more specific
            has_and = ' and ' in line  # "and" keyword = multi-item pattern
            
            # Check for special keywords that make patterns more specific
            special_keywords = ['carbon neutral', 'shipped', 'unshipped']
            has_special_keyword = any(k in line for k in special_keywords)
            
            # Specificity score: higher = more specific
            specificity = param_count + (2 if has_and else 0) + (3 if has_special_keyword else 0)
            
            when_patterns.append((i, specificity, line.strip()))
    
    # Check if patterns are in descending specificity order
    for i in range(len(when_patterns) - 1):
        curr_line, curr_spec, curr_text = when_patterns[i]
        next_line, next_spec, next_text = when_patterns[i + 1]
        
        # Check if patterns are mutually exclusive (both have unique keywords)
        curr_has_unique = any(k in curr_text for k in ['carbon neutral', 'shipped'])
        next_has_unique = any(k in next_text for k in [' and '])
        mutually_exclusive = curr_has_unique and next_has_unique
        
        # If next pattern is MORE specific than current AND not mutually exclusive
        if next_spec > curr_spec and not mutually_exclusive:
            issues.append(f"❌ Line {next_line} (specificity={next_spec}) should come BEFORE line {curr_line} (specificity={curr_spec})")
            issues.append(f"   More specific: {next_text}")
            issues.append(f"   Less specific: {curr_text}")
            issues.append(f"   FIX: Move line {next_line} to BEFORE line {curr_line}")
        
        # CRITICAL CHECK: Multi-item must come before single-item (same base pattern)
        curr_has_and = ' and ' in curr_text
        next_has_and = ' and ' in next_text
        curr_param_count = curr_text.count('{')
        next_param_count = next_text.count('{')
        
        # If current is single-item (2 params, no 'and') and next is multi-item (4+ params, has 'and')
        if (not curr_has_and and curr_param_count == 2 and 
            next_has_and and next_param_count >= 4):
            issues.append(f"❌ CRITICAL: Line {next_line} (multi-item) MUST come BEFORE line {curr_line} (single-item)")
            issues.append(f"   This causes silent failures: orders not created, balance=0")
            issues.append(f"   Multi-item: {next_text}")
            issues.append(f"   Single-item: {curr_text}")
            issues.append(f"   FIX: Move line {next_line} to BEFORE line {curr_line}")
    
    return issues


def main():
    """Check all step files in features/steps directory."""
    steps_dir = Path('features/steps')
    
    if not steps_dir.exists():
        print(f"❌ Directory not found: {steps_dir}")
        print("   Run this script from: test/api_logic_server_behave/")
        sys.exit(1)
    
    all_issues = []
    files_checked = 0
    
    for steps_file in steps_dir.glob('*_steps.py'):
        files_checked += 1
        issues = check_step_order(steps_file)
        if issues:
            all_issues.extend([f"\n📁 {steps_file}:"] + issues)
    
    if all_issues:
        print("=" * 70)
        print("Step Ordering Issues Found (Rule #0.5 Violation)")
        print("=" * 70)
        print('\n'.join(all_issues))
        print("\n" + "=" * 70)
        print("IMPACT: Tests may pass but produce wrong results (e.g., balance=0)")
        print("ACTION: Reorder @when patterns from most→least specific")
        print("=" * 70)
        sys.exit(1)
    else:
        print("=" * 70)
        print(f"✅ All step patterns correctly ordered ({files_checked} files checked)")
        print("   Rule #0.5: Most specific → Most general ✓")
        print("=" * 70)
        sys.exit(0)


if __name__ == '__main__':
    main()
