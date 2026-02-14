#!/usr/bin/env python3
"""
DEEPEX Audit Script for MW-Vision
Runs DEEPEX v4 with 2 iterations on MW-Vision project
"""

import sys
import os
import asyncio
from pathlib import Path

# Add DEEPEX to path
deepex_path = Path("l:/nicedev-Project/MindWarehouse-Project/DEEPEX")
if str(deepex_path) not in sys.path:
    sys.path.insert(0, str(deepex_path))

from DEEPEX_v4_IMPLEMENTATION import DEEPEXv4, Project
from datetime import datetime

def count_loc(path: str) -> int:
    """Count lines of code in MW-Vision project"""
    total_loc = 0
    exclude_dirs = {'.venv', 'venv', '.git', '__pycache__', 'node_modules', 'dist', 'build'}
    exclude_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.mp4', '.mp3', '.pdf'}
    
    for root, dirs, files in os.walk(path):
        # Filter excluded directories
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
                # Skip binary files
                continue
    
    return total_loc

def analyze_project_structure(path: str) -> dict:
    """Analyze MW-Vision project structure"""
    structure = {
        'frontend': {'files': 0, 'extensions': set()},
        'backend': {'files': 0, 'extensions': set()},
        'docs': {'files': 0, 'extensions': set()},
        'config': {'files': 0, 'extensions': set()},
        'other': {'files': 0, 'extensions': set()}
    }
    
    for root, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, path)
        
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            
            # Categorize by path
            if 'mw-vision-app' in rel_root or 'frontend' in rel_root.lower():
                category = 'frontend'
            elif 'backend' in rel_root.lower() or 'api' in rel_root.lower():
                category = 'backend'
            elif 'docs' in rel_root.lower() or 'documentation' in rel_root.lower():
                category = 'docs'
            elif 'config' in rel_root.lower() or '.env' in file or 'package.json' == file:
                category = 'config'
            else:
                category = 'other'
            
            structure[category]['files'] += 1
            structure[category]['extensions'].add(file_ext if file_ext else 'no_ext')
    
    return structure

async def run_deepex_iteration(evaluator: DEEPEXv4, project: Project, iteration: int) -> dict:
    """Run a single DEEPEX iteration"""
    print(f"\n{'='*60}")
    print(f"🧪 DEEPEX Iteration {iteration}")
    print(f"{'='*60}")
    
    # Run evaluation
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
    
    # Print results
    print(f"\n📊 Overall Score: {result.overall_score:.1f}%")
    print(f"🎯 Confidence: {result.confidence:.2f}")
    print(f"📈 Version: {result.version}")
    
    print("\n📋 Category Scores:")
    for category, score in sorted(result.category_scores.items(), key=lambda x: x[1]):
        print(f"  {category.replace('_', ' ').title():25} {score:6.1f}%")
    
    print("\n💡 Recommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i:2}. {rec}")
    
    if result.findings:
        print("\n🔍 Findings:")
        for i, finding in enumerate(result.findings, 1):
            severity = finding.get('severity', 'INFO')
            issue = finding.get('issue', 'Unknown')
            print(f"  {i:2}. [{severity}] {issue}")
    
    return iteration_result

async def main():
    """Main function to run DEEPEX audit on MW-Vision"""
    project_path = Path("L:/nicedev-Project/MW-Vision")
    
    print(f"{'='*60}")
    print(f"🚀 DEEPEX v4 AUDIT - MW-VISION")
    print(f"{'='*60}")
    print(f"Project Path: {project_path}")
    
    # 1. Analyze project structure
    print("\n📁 Analyzing project structure...")
    structure = analyze_project_structure(str(project_path))
    total_files = sum(cat['files'] for cat in structure.values())
    
    print(f"\n📊 Project Structure Analysis:")
    for category, data in structure.items():
        if data['files'] > 0:
            percentage = (data['files'] / total_files) * 100
            extensions = ', '.join(sorted(data['extensions'])[:5])
            print(f"  {category.upper():10} {data['files']:4d} files ({percentage:.1f}%) - Extensions: {extensions}")
    
    # 2. Count LOC
    print("\n📈 Counting lines of code...")
    loc = count_loc(str(project_path))
    print(f"  Total LOC: {loc:,}")
    
    # 3. Create Project object
    print("\n🎯 Creating DEEPEX Project object...")
    project = Project(
        name="MW-Vision",
        path=str(project_path),
        language="Mixed (TypeScript/Python)",
        size_loc=loc,
        context="production",
        metadata={
            "total_files": total_files,
            "structure": structure,
            "description": "Visual Command Center for Multi-Agent AI Development",
            "target_users": "AI Developers, Team Leads, Product Managers",
            "deployment_target": "Cloud/Self-hosted",
            "tech_stack": "React 18.3.1 + TypeScript + Vite + FastAPI + PostgreSQL"
        }
    )
    
    # 4. Initialize DEEPEX evaluator
    print("\n🔧 Initializing DEEPEX v4 evaluator...")
    evaluator = DEEPEXv4(context="production")
    
    # 5. Run 2 iterations
    print("\n🔄 Running 2 DEEPEX iterations...")
    results = []
    
    for iteration in range(1, 3):
        iteration_result = await run_deepex_iteration(evaluator, project, iteration)
        results.append(iteration_result)
        
        # Update project metadata with findings from this iteration
        if iteration == 1 and 'findings' in iteration_result:
            project.metadata['num_findings'] = len(iteration_result['findings'])
    
    # 6. Generate final report
    print(f"\n{'='*60}")
    print(f"📋 DEEPEX AUDIT COMPLETE - SUMMARY")
    print(f"{'='*60}")
    
    if len(results) >= 2:
        first_score = results[0]['overall_score']
        second_score = results[1]['overall_score']
        delta = second_score - first_score
        direction = "+" if delta >= 0 else ""
        
        print(f"\n📈 Score Progression:")
        print(f"  Iteration 1: {first_score:.1f}%")
        print(f"  Iteration 2: {second_score:.1f}%")
        print(f"  Delta: {direction}{delta:.1f}%")
        
        if delta > 0:
            print(f"  ✅ IMPROVEMENT: Score increased by {delta:.1f}%")
        elif delta < 0:
            print(f"  ⚠️  REGRESSION: Score decreased by {abs(delta):.1f}%")
        else:
            print(f"  🔄 STABLE: Score unchanged")
    
    # 7. Identify top 3 improvement areas
    if results:
        last_result = results[-1]
        category_scores = last_result['category_scores']
        
        # Sort by score (lowest first)
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])
        
        print(f"\n🎯 Top 3 Improvement Areas:")
        for i, (category, score) in enumerate(sorted_categories[:3], 1):
            print(f"  {i}. {category.replace('_', ' ').title()} ({score:.1f}%)")
    
    # 8. Save report to file
    report_path = project_path / "DEEPEX_AUDIT_REPORT.md"
    save_report(results, report_path, project)
    
    print(f"\n💾 Report saved to: {report_path}")
    print(f"\n✅ DEEPEX audit completed successfully!")
    
    return results

def save_report(results: list, report_path: Path, project: Project):
    """Save DEEPEX audit report to markdown file"""
    
    report_content = f"""# DEEPEX v4 Audit Report - MW-Vision

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Auditor:** DEEPEX v4.0.0
**Project:** {project.name}
**Context:** {project.context}

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **Project Name** | {project.name} |
| **Total Lines of Code** | {project.size_loc:,} |
| **Programming Language** | {project.language} |
| **Audit Context** | {project.context} |
| **Number of Iterations** | {len(results)} |

"""

    if len(results) >= 2:
        first_score = results[0]['overall_score']
        second_score = results[1]['overall_score']
        delta = second_score - first_score
        direction = "+" if delta >= 0 else ""
        
        report_content += f"""
### 🎯 Score Evolution
- **Iteration 1:** {first_score:.1f}%
- **Iteration 2:** {second_score:.1f}%
- **Delta:** {direction}{delta:.1f}%

**Interpretation:** {'Score improved' if delta > 0 else 'Score regressed' if delta < 0 else 'Score stable'} across iterations.
"""

    # Add project metadata
    if project.metadata:
        report_content += "\n### 📊 Project Metadata\n\n"
        for key, value in project.metadata.items():
            if key != 'structure':
                report_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
    
    # Add detailed iteration results
    for i, result in enumerate(results, 1):
        report_content += f"""
---

## ITERATION {i}: {result['overall_score']:.1f}%

**Timestamp:** {result['timestamp']}
**Confidence:** {result['confidence']:.2f}

### 📈 Category Scores

| Category | Score | Status |
|----------|-------|--------|
"""
        
        for category, score in sorted(result['category_scores'].items(), key=lambda x: x[1]):
            category_name = category.replace('_', ' ').title()
            
            if score >= 90:
                status = "✅ Excellent"
            elif score >= 80:
                status = "🟢 Good"
            elif score >= 70:
                status = "🟡 Moderate"
            elif score >= 60:
                status = "🟠 Needs Work"
            else:
                status = "🔴 Critical"
            
            report_content += f"| {category_name} | {score:.1f}% | {status} |\n"
        
        # Add recommendations
        if result['recommendations']:
            report_content += "\n### 💡 Recommendations\n\n"
            for j, rec in enumerate(result['recommendations'], 1):
                report_content += f"{j}. {rec}\n"
        
        # Add findings
        if result.get('findings'):
            report_content += "\n### 🔍 Findings\n\n"
            for j, finding in enumerate(result['findings'], 1):
                severity = finding.get('severity', 'INFO')
                issue = finding.get('issue', 'Unknown')
                details = finding.get('details', '')
                
                report_content += f"**{j}. [{severity}] {issue}**\n"
                if details:
                    if isinstance(details, list):
                        for detail in details[:3]:  # Limit details
                            report_content += f"   - {detail}\n"
                    else:
                        report_content += f"   {details}\n"
                report_content += "\n"
    
    # Add improvement roadmap
    if results:
        last_result = results[-1]
        category_scores = last_result['category_scores']
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])
        
        report_content += """
---

## 🎯 IMPROVEMENT ROADMAP

### Priority 1: Critical Improvements (Score < 60%)
"""
        
        critical = [(cat, score) for cat, score in sorted_categories if score < 60]
        for category, score in critical:
            report_content += f"- **{category.replace('_', ' ').title()}** ({score:.1f}%)\n"
            report_content += f"  - Immediate action required\n"
            report_content += f"  - Suggested focus: Review implementation, add tests, improve documentation\n"
        
        report_content += "\n### Priority 2: Moderate Improvements (60-75%)\n"
        
        moderate = [(cat, score) for cat, score in sorted_categories if 60 <= score < 75]
        for category, score in moderate:
            report_content += f"- **{category.replace('_', ' ').title()}** ({score:.1f}%)\n"
            report_content += f"  - Improvement recommended\n"
            report_content += f"  - Suggested focus: Incremental improvements, optimization\n"
        
        report_content += "\n### Priority 3: Optimization (75-90%)\n"
        
        optimize = [(cat, score) for cat, score in sorted_categories if 75 <= score < 90]
        for category, score in optimize:
            report_content += f"- **{category.replace('_', ' ').title()}** ({score:.1f}%)\n"
            report_content += f"  - Already good, can be excellent\n"
            report_content += f"  - Suggested focus: Fine-tuning, performance optimization\n"
    
    report_content += f"""
---

## 🚀 NEXT STEPS

1. **Review Critical Findings** - Address issues with scores below 60%
2. **Implement Recommendations** - Apply DEEPEX suggestions from audit
3. **Re-audit** - Run DEEPEX again after improvements to measure progress
4. **Document Improvements** - Update project documentation with audit insights

---

*This audit was conducted by DEEPEX v4.0.0, an autonomous code excellence evaluator.*
*For questions or further analysis, consult the DEEPEX documentation.*
"""
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n🔥 Error during DEEPEX audit: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)