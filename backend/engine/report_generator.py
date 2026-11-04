import io
import json
from typing import Dict, Any, List
from models import ReviewResult, RepositorySummary, IssueItem
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGenerator:
    @staticmethod
    def to_markdown(result: ReviewResult) -> str:
        s = result.summary
        md = []
        md.append(f"# Automated Code Review & Reusability Audit: {s.project_name}\n")
        md.append(f"**Date:** {result.analyzed_at} | **Balanced Health Grade:** {s.grade} ({s.health_score}/100)\n\n")
        
        md.append("## Executive Summary\n")
        md.append(f"{s.executive_summary}\n\n")
        md.append(f"> *Fairness Guarantee:* {s.fairness_statement}\n\n")
        
        md.append("## Balanced Health Scorecard\n")
        md.append(f"| Metric | Score | Status |\n")
        md.append(f"| :--- | :--- | :--- |\n")
        md.append(f"| **Overall Code Health** | {s.health_score} / 100 | Grade {s.grade} |\n")
        md.append(f"| **Reusability & Modularity** | {s.reusability_score} / 100 | {s.reusability_rating} |\n")
        md.append(f"| **Security Hardening** | {s.security_score} / 100 | {'Optimal' if s.security_score > 80 else 'Enhancements Advised'} |\n")
        md.append(f"| **Efficiency & Big-O** | {s.efficiency_score} / 100 | {'Optimal' if s.efficiency_score > 80 else 'Bottlenecks Found'} |\n")
        md.append(f"| **Maintainability** | {s.maintainability_score} / 100 | {'Clean' if s.maintainability_score > 70 else 'Refactoring Advised'} |\n")
        md.append(f"| **Reliability & Bugs** | {s.reliability_score} / 100 | {'Stable' if s.reliability_score > 80 else 'Action Items'} |\n\n")

        # Code Strengths & Commendations
        if s.strengths:
            md.append("## 🌟 Code Strengths & Commendations\n")
            for st in s.strengths:
                md.append(f"- **{st.title}** (`{st.file}`): {st.description} *({st.impact})*\n")
            md.append("\n")

        # Multi-Form Optimization Pathways
        if result.optimizations:
            md.append("## ⚡ Multi-Form Optimization Pathways\n\n")
            for opt in result.optimizations:
                md.append(f"### Target: `{opt.target_name}` in `{opt.file}`\n\n")
                for path in opt.pathways:
                    md.append(f"#### {path.title}\n")
                    md.append(f"- **Tagline:** {path.tagline}\n")
                    md.append(f"- **Complexity:** {path.time_complexity} | {path.space_complexity}\n")
                    md.append(f"- **Best Suited For:** {path.best_suited_for}\n")
                    md.append(f"- **Tradeoffs:** {path.tradeoffs}\n")
                    md.append("```python\n" + path.code + "\n```\n\n")
            md.append("---\n\n")

        md.append("## Detailed Actionable Findings\n\n")
        for idx, issue in enumerate(result.issues, 1):
            md.append(f"### {idx}. [{issue.severity.upper()}] {issue.title}\n")
            md.append(f"- **File:** `{issue.file}` (Line {issue.line})\n")
            md.append(f"- **Category:** {issue.category.title()} | **Rule:** `{issue.rule_id}`\n")
            md.append(f"- **Description:** {issue.description}\n")
            md.append(f"- **Impact:** {issue.impact}\n\n")
            
            if issue.original_code:
                md.append("```python\n# Current Code\n" + issue.original_code + "\n```\n\n")
            if issue.suggested_fix:
                md.append("```python\n# Suggested Remediated Code\n" + issue.suggested_fix + "\n```\n\n")
            
            md.append(f"> **Why this fix works:** {issue.explanation}\n\n")
            md.append("---\n\n")

        return "".join(md)

    @staticmethod
    def to_pdf_bytes(result: ReviewResult) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0F172A')
        )
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#64748B')
        )
        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=5
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#334155')
        )

        elements = []
        elements.append(Paragraph(f"Code Review & Reusability Audit: {result.summary.project_name}", title_style))
        elements.append(Paragraph(f"Generated at {result.analyzed_at} | Balanced Health: Grade {result.summary.grade} ({result.summary.health_score}/100) • Reusability: {result.summary.reusability_score}/100", subtitle_style))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

        # Executive Summary
        elements.append(Paragraph("Executive Summary & Balanced Assessment", h2_style))
        elements.append(Paragraph(result.summary.executive_summary, body_style))
        elements.append(Spacer(1, 8))

        # Scorecard Table
        elements.append(Paragraph("Balanced Quality Scorecard", h2_style))
        score_data = [
            ["Metric", "Score", "Grade / Status"],
            ["Overall Code Health", f"{result.summary.health_score} / 100", f"Grade {result.summary.grade}"],
            ["Reusability & Modularity", f"{result.summary.reusability_score} / 100", result.summary.reusability_rating[:25]],
            ["Security Hardening", f"{result.summary.security_score} / 100", "Compliant" if result.summary.security_score > 75 else "Action Items"],
            ["Algorithm Efficiency", f"{result.summary.efficiency_score} / 100", "Optimal" if result.summary.efficiency_score > 75 else "Optimizations Advised"],
            ["Maintainability Index", f"{result.summary.maintainability_score} / 100", "Clean Architecture"],
            ["Reliability / Bugs", f"{result.summary.reliability_score} / 100", "Reviewed"],
        ]
        t = Table(score_data, colWidths=[180, 110, 210])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

        # Top Strengths
        if result.summary.strengths:
            elements.append(Paragraph("Recognized Code Strengths", h2_style))
            for st in result.summary.strengths[:4]:
                elements.append(Paragraph(f"• <b>{st.title}</b> ({st.file}): {st.description}", body_style))
                elements.append(Spacer(1, 3))
            elements.append(Spacer(1, 6))

        # Top Priority Action Items
        elements.append(Paragraph("Actionable Optimization & Security Findings", h2_style))
        for idx, issue in enumerate(result.issues[:8], 1):
            item_text = f"<b>{idx}. [{issue.severity.upper()}] {issue.title}</b> ({issue.file}:{issue.line})<br/><font color='#64748B'>{issue.description}</font>"
            elements.append(Paragraph(item_text, body_style))
            elements.append(Spacer(1, 3))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
