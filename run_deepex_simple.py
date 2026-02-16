#!/usr/bin/env python3
"""
DEEPEX Audit Script for MW-Vision (Windows-compatible, no emojis)
Runs DEEPEX v4 with 2 iterations on MW-Vision project
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add DEEPEX to path
deepex_path = Path("l:/nicedev-Project/MindWarehouse-Project/DEEPEX")
if str(deepex_path) not in sys.path:
    sys.path.insert(0, str(deepex_path))

from DEEPEX_v4_IMPLEMENTATION import DEEPEXv4, Project

def count_loc(path: str) -> int:
    """Count lines of code in MW-Vision project"""
    total_loc = 0
    exclude_dirs = {'.venv', 'venv', '.git', '__pycache__', 'node_modules', 'dist', 'build'}
    exclude_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.mp4', '.mp3', '.pdf'}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in exclude_extensions:
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    total_loc += len(lines)
            except (UnicodeDecodeError, IOError):
                continue

    return total_loc

async def run_deepex_iteration(evaluator: DEEPEXv4, project: Project, iteration: int) -> dict:
    """Run a single DEEPEX iteration"""
    print(f"\n{'='*60}")
    print(f"[DEEPEX] Iteration {iteration}")
    print(f"{'='*60}")

    result = evaluator.evaluate(project)

    iteration_result = {
        'iteration': iteration,
        'timestamp': datetime.now().isoformat(),
        'overall_score': result.overall_score,
        'category_scores': result.category_scores,
        'confidence': result.confidence,
        'recommendations': result.recommendations,
        'findings': result.findings,
        'qualitative_assessment': result.qualitative_assessment,
        'warnings': result.warnings
    }

    print(f"\n[SCORE] Overall: {result.overall_score:.1f}%")
    print(f"[CONFIDENCE] {result.confidence:.2f}")
    print(f"[VERSION] {result.version}")

    print("\n[CATEGORY SCORES]")
    for category, score in sorted(result.category_scores.items(), key=lambda x: x[1]):
        print(f"  {category.replace('_', ' ').title():25} {score:6.1f}%")

    print("\n[RECOMMENDATIONS]")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i:2}. {rec}")

    if result.findings:
        print("\n[FINDINGS]")
        for i, finding in enumerate(result.findings, 1):
            severity = finding.get('severity', 'INFO')
            issue = finding.get('issue', 'Unknown')
            print(f"  {i:2}. [{severity}] {issue}")

    return iteration_result

async def main():
    """Main function to run DEEPEX audit on MW-Vision"""
    project_path = Path("L:/nicedev-Project/MW-Vision")

    print(f"{'='*60}")
    print(f"DEEPEX v4 AUDIT - MW-VISION")
    print(f"{'='*60}")
    print(f"Project Path: {project_path}")

    print("\n[ANALYZING] Project structure...")
    loc = count_loc(str(project_path))
    print(f"  Total LOC: {loc:,}")

    print("\n[CREATING] DEEPEX Project object...")
    project = Project(
        name="MW-Vision",
        path=str(project_path),
        language="Mixed (TypeScript/Python)",
        size_loc=loc,
        context="production",
        metadata={
            "description": "Visual Command Center for Multi-Agent AI Development",
            "tech_stack": "React 18.3.1 + TypeScript + Vite + FastAPI"
        }
    )

    print("\n[INITIALIZING] DEEPEX v4 evaluator...")
    evaluator = DEEPEXv4(context="production")

    print("\n[RUNNING] 2 DEEPEX iterations...")
    results = []

    for iteration in range(1, 3):
        iteration_result = await run_deepex_iteration(evaluator, project, iteration)
        results.append(iteration_result)

    print(f"\n{'='*60}")
    print(f"DEEPEX AUDIT COMPLETE - SUMMARY")
    print(f"{'='*60}")

    if len(results) >= 2:
        first_score = results[0]['overall_score']
        second_score = results[1]['overall_score']
        delta = second_score - first_score
        direction = "+" if delta >= 0 else ""

        print(f"\n[SCORE PROGRESSION]")
        print(f"  Iteration 1: {first_score:.1f}%")
        print(f"  Iteration 2: {second_score:.1f}%")
        print(f"  Delta: {direction}{delta:.1f}%")

        if delta > 0:
            print(f"  [OK] Score improved by {delta:.1f}%")
        elif delta < 0:
            print(f"  [WARNING] Score decreased by {abs(delta):.1f}%")
        else:
            print(f"  [INFO] Score unchanged")

    if results:
        last_result = results[-1]
        category_scores = last_result['category_scores']
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])

        print(f"\n[TOP 3 IMPROVEMENT AREAS]")
        for i, (category, score) in enumerate(sorted_categories[:3], 1):
            print(f"  {i}. {category.replace('_', ' ').title()} ({score:.1f}%)")

    print(f"\n[SUCCESS] DEEPEX audit completed!")
    return results

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        print(f"\n[DONE] Audit generated {len(results)} iterations")
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Audit stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
