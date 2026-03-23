"""Report builder for research results with rich PDF generation via ReportLab."""
import logging
from datetime import datetime
from pathlib import Path
import re
import uuid
from typing import List, Dict
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Table,
    TableStyle,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Builds comprehensive research reports."""

    def __init__(self):
        """Initialize report builder."""
        self.reports_dir = settings.reports_dir_path
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def build_report(
        self,
        topic: str,
        findings: List[Dict],
        summary: str,
        steps: List[Dict],
        conclusion: str,
    ) -> Dict:
        """
        Build a comprehensive report and generate a rich PDF artifact.
        """
        logger.info("Building report for: %s", topic)
        generated_at = datetime.now().isoformat()

        pdf_path = self._generate_pdf(
            topic=topic,
            summary=summary,
            findings=findings,
            conclusion=conclusion,
            steps=steps,
            generated_at=generated_at,
        )

        return {
            "topic": topic,
            "summary": summary,
            "findings": findings,
            "conclusion": conclusion,
            "steps_taken": len(steps),
            "generated_at": generated_at,
            "status": "completed",
            "pdf_path": str(pdf_path),
            "pdf_filename": pdf_path.name,
        }

    def _generate_pdf(
        self,
        topic: str,
        summary: str,
        findings: List[Dict],
        conclusion: str,
        steps: List[Dict],
        generated_at: str,
    ) -> Path:
        """Generate a polished PDF report using reportlab platypus."""
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", topic.strip()).strip("-").lower() or "research-report"
        filename = f"{safe_name}-{uuid.uuid4().hex[:8]}.pdf"
        pdf_path = self.reports_dir / filename

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=LETTER,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.7 * inch,
            title=f"Research Report - {topic}",
            author="Autonomous Research Agent",
        )

        styles = self._build_styles()
        story = []

        story.append(Paragraph("Autonomous Research Report", styles["report_title"]))
        story.append(Spacer(1, 0.08 * inch))
        story.append(Paragraph(self._to_paragraph_text(topic), styles["report_subtitle"]))
        story.append(Spacer(1, 0.16 * inch))
        story.append(HRFlowable(width="100%", color=colors.HexColor("#CBD5E1"), thickness=1))
        story.append(Spacer(1, 0.16 * inch))

        metadata_rows = [
            [Paragraph("<b>Topic</b>", styles["report_meta_key"]), Paragraph(self._to_paragraph_text(topic), styles["report_meta_value"])],
            [Paragraph("<b>Generated</b>", styles["report_meta_key"]), Paragraph(self._to_paragraph_text(generated_at), styles["report_meta_value"])],
            [Paragraph("<b>Insights</b>", styles["report_meta_key"]), Paragraph(str(len(findings)), styles["report_meta_value"])],
            [Paragraph("<b>Workflow Steps</b>", styles["report_meta_key"]), Paragraph(str(len(steps)), styles["report_meta_value"])],
        ]
        meta_table = Table(metadata_rows, colWidths=[1.35 * inch, 5.8 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6DEE8")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(meta_table)
        story.append(Spacer(1, 0.18 * inch))

        story.append(Paragraph("Executive Summary", styles["report_section"]))
        story.append(Paragraph(self._to_paragraph_text(summary or "No summary available."), styles["report_body"]))
        story.append(Spacer(1, 0.16 * inch))

        story.append(Paragraph("Key Insights", styles["report_section"]))
        if findings:
            for idx, finding in enumerate(findings, start=1):
                title = finding.get("title", f"Insight {idx}")
                content = finding.get("content", "")
                confidence = finding.get("confidence", "N/A")
                strength = finding.get("evidence_strength", "N/A")
                source = finding.get("source") or "N/A"

                source_display = self._truncate_middle(source, 110)
                block_rows = [
                    [Paragraph(f"<b>{idx}. {self._to_paragraph_text(title)}</b>", styles["report_insight_title"])],
                    [Paragraph(self._to_paragraph_text(content or "No content available."), styles["report_body"])],
                    [
                        Paragraph(
                            self._to_paragraph_text(
                                f"Confidence: {confidence} | Evidence: {strength} | Source: {source_display}"
                            ),
                            styles["report_muted"],
                        )
                    ],
                ]

                insight_table = Table(block_rows, colWidths=[7.15 * inch])
                insight_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CDD6E1")),
                            ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#3D5AD8")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ("TOPPADDING", (0, 0), (-1, -1), 7),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                        ]
                    )
                )
                story.append(insight_table)
                story.append(Spacer(1, 0.1 * inch))
        else:
            story.append(Paragraph("No insights were extracted for this run.", styles["report_body"]))
            story.append(Spacer(1, 0.08 * inch))

        if steps:
            story.append(Paragraph("Execution Steps", styles["report_section"]))
            for step in steps:
                label = f"Step {step.get('step_number', '?')} - {step.get('action', 'unknown')}"
                message = step.get("message", "")
                story.append(Paragraph(f"<b>{self._to_paragraph_text(label)}</b>", styles["report_body"]))
                if message:
                    story.append(Paragraph(self._to_paragraph_text(message), styles["report_muted"]))
                story.append(Spacer(1, 0.04 * inch))
            story.append(Spacer(1, 0.12 * inch))

        story.append(Paragraph("Conclusion", styles["report_section"]))
        story.append(Paragraph(self._to_paragraph_text(conclusion or "No conclusion available."), styles["report_body"]))

        doc.build(
            story,
            onFirstPage=self._make_page_decorator(topic),
            onLaterPages=self._make_page_decorator(topic),
        )
        return pdf_path

    def _build_styles(self):
        """Create reportlab paragraph styles."""
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                "report_title",
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                textColor=colors.HexColor("#1E293B"),
                spaceAfter=0,
            )
        )
        styles.add(
            ParagraphStyle(
                "report_subtitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=12,
                leading=16,
                textColor=colors.HexColor("#475569"),
                spaceAfter=0,
            )
        )
        styles.add(
            ParagraphStyle(
                "report_section",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#1F2937"),
                spaceBefore=6,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                "report_body",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor("#334155"),
            )
        )
        styles.add(
            ParagraphStyle(
                "report_muted",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#64748B"),
            )
        )
        styles.add(
            ParagraphStyle(
                "report_meta_key",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#334155"),
            )
        )
        styles.add(
            ParagraphStyle(
                "report_meta_value",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#334155"),
            )
        )
        styles.add(
            ParagraphStyle(
                "report_insight_title",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#1E293B"),
            )
        )
        return styles

    def _to_paragraph_text(self, text: str) -> str:
        """Escape/sanitize text for reportlab Paragraph."""
        value = text if isinstance(text, str) else str(text)
        value = re.sub(r"\s+", " ", value).strip()
        if not value:
            return ""
        return escape(value)

    def _truncate_middle(self, text: str, max_length: int) -> str:
        """Shorten long strings preserving prefix and suffix."""
        if len(text) <= max_length:
            return text
        keep = (max_length - 3) // 2
        return f"{text[:keep]}...{text[-keep:]}"

    def _make_page_decorator(self, topic: str):
        """Create page decorator callback with header/footer."""

        def _decorate(canvas_obj, doc):
            canvas_obj.saveState()
            width, height = LETTER

            canvas_obj.setStrokeColor(colors.HexColor("#E2E8F0"))
            canvas_obj.setLineWidth(0.6)
            canvas_obj.line(0.75 * inch, height - 0.58 * inch, width - 0.75 * inch, height - 0.58 * inch)

            canvas_obj.setFont("Helvetica", 8.5)
            canvas_obj.setFillColor(colors.HexColor("#64748B"))
            canvas_obj.drawString(0.75 * inch, height - 0.47 * inch, f"Topic: {self._truncate_middle(topic, 75)}")

            canvas_obj.line(0.75 * inch, 0.58 * inch, width - 0.75 * inch, 0.58 * inch)
            canvas_obj.drawString(0.75 * inch, 0.42 * inch, "Autonomous Research Agent")
            canvas_obj.drawRightString(width - 0.75 * inch, 0.42 * inch, f"Page {canvas_obj.getPageNumber()}")
            canvas_obj.restoreState()

        return _decorate
