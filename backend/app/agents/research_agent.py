"""Main research agent using LangChain"""
import asyncio
import logging
from datetime import datetime
from typing import Any
import re
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from app.services.llm_service import LLMService
from app.schemas.research import ResearchStep
from app.agents.report_builder import ReportBuilder
from app.tools.search_tool import search_web
from app.tools.content_extractor_tool import extract_content
from app.tools.insight_extractor_tool import extract_insights
from app.tools.report_generator_tool import generate_report
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Main research agent for autonomous research"""

    def __init__(self):
        """Initialize research agent"""
        self.llm_service = LLMService()
        self.tools = self._create_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.report_builder = ReportBuilder()
        self.steps: list[ResearchStep] = []

    def _create_tools(self) -> list[StructuredTool]:
        """Create tools for the agent"""
        return [
            StructuredTool.from_function(search_web),
            StructuredTool.from_function(extract_content),
            StructuredTool.from_function(extract_insights),
            StructuredTool.from_function(generate_report),
        ]

    def _add_step(self, action: str, status: str, message: str) -> None:
        """Append a tracked execution step."""
        self.steps.append(
            ResearchStep(
                step_number=len(self.steps) + 1,
                action=action,
                status=status,
                message=message,
                timestamp=datetime.now(),
            )
        )

    async def run_research(
        self,
        topic: str,
        max_iterations: int = 5,
    ) -> dict:
        """
        Run research on a topic.
        
        Args:
            topic: Research topic
            max_iterations: Maximum iterations
            
        Returns:
            Research results
        """
        logger.info(f"Starting research on topic: {topic}")
        self.steps = []

        try:
            search_results = await asyncio.to_thread(
                self.tool_map["search_web"].invoke,
                {"query": topic, "max_results": max_iterations},
            )
            self._add_step(
                action="search_web",
                status="completed",
                message=f"Found {len(search_results)} search results.",
            )

            tasks = [
                self._analyze_search_result(result)
                for result in search_results[:max_iterations]
            ]
            analyzed_batches = await asyncio.gather(*tasks, return_exceptions=True)

            findings: list[dict[str, Any]] = []
            explored_sources = 0
            for batch in analyzed_batches:
                if isinstance(batch, Exception):
                    logger.warning("Source analysis error: %s", batch)
                    continue
                if not batch:
                    continue
                explored_sources += 1
                findings.extend(batch)

            self._add_step(
                action="analyze_sources",
                status="completed",
                message=f"Analyzed {explored_sources} sources and extracted {len(findings)} findings.",
            )

            if not findings:
                for result in search_results:
                    source = result.get("url")
                    findings.append(
                        {
                            "title": result.get("title", "Search finding"),
                            "content": result.get("snippet", ""),
                            "source": source,
                            "confidence": 0.5,
                            "citations": [source] if source else [],
                        }
                    )

            findings = self._deduplicate_findings(findings)
            findings = self._annotate_evidence_strength(findings)
            self._add_step(
                action="validate_findings",
                status="completed",
                message=f"Validated findings quality: {len(findings)} unique findings retained.",
            )

            synthesis_prompt = self._build_synthesis_prompt(topic, findings)

            if not settings.OPENROUTER_API_KEY:
                summary = self._fallback_summary(topic, findings)
                self._add_step(
                    action="synthesize_answer",
                    status="completed",
                    message="OPENROUTER_API_KEY not configured, generated fallback summary from findings.",
                )
            else:
                try:
                    response = await self.llm_service.ainvoke(
                        [
                            SystemMessage(content=self._get_system_prompt()),
                            HumanMessage(content=synthesis_prompt),
                        ]
                    )
                    summary = str(response.content)
                    if not summary.strip():
                        raise RuntimeError("Empty LLM response content")
                    self._add_step(
                        action="synthesize_answer",
                        status="completed",
                        message="Generated final synthesis using LLM.",
                    )
                except Exception as llm_error:
                    logger.warning("LLM synthesis failed, using fallback summary: %s", llm_error)
                    summary = self._fallback_summary(topic, findings)
                    self._add_step(
                        action="synthesize_answer",
                        status="completed",
                        message="LLM synthesis unavailable, generated fallback summary from findings.",
                    )

            conclusion = summary
            _ = await asyncio.to_thread(
                self.tool_map["generate_report"].invoke,
                {
                    "topic": topic,
                    "findings": findings,
                    "summary": summary,
                    "conclusion": conclusion,
                },
            )
            report = await asyncio.to_thread(
                self.report_builder.build_report,
                topic,
                findings,
                summary,
                [step.model_dump() for step in self.steps],
                conclusion,
            )
            self._add_step(
                action="generate_report",
                status="completed",
                message=f"Built structured report and generated PDF: {report.get('pdf_filename', 'n/a')}",
            )

            return {
                "topic": topic,
                "steps": [step.model_dump() for step in self.steps],
                "summary": summary,
                "findings": findings,
                "report": report,
            }

        except Exception as e:
            logger.error(f"Error during research: {e}")
            raise

    async def _analyze_search_result(self, result: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze one search result and extract structured findings."""
        url = result.get("url")
        if not url:
            return []

        raw_content = await asyncio.to_thread(
            self.tool_map["extract_content"].invoke,
            {"url": url},
        )
        if not raw_content:
            return []

        insights = await asyncio.to_thread(
            self.tool_map["extract_insights"].invoke,
            {"content": raw_content},
        )

        findings: list[dict[str, Any]] = []
        for insight in insights[:1]:
            findings.append(
                {
                    "title": insight.get("title", "Insight"),
                    "content": insight.get("description", ""),
                    "source": url,
                    "confidence": float(insight.get("confidence", 0.7)),
                    "citations": [url],
                }
            )
        return findings

    def _get_system_prompt(self) -> str:
        """Get system prompt for research"""
        return """You are a thorough research assistant. 
            Conduct comprehensive research providing detailed analysis, multiple perspectives, 
            and well-sourced information."""

    def _build_synthesis_prompt(self, topic: str, findings: list[dict[str, Any]]) -> str:
        """Create synthesis prompt from collected findings."""
        findings_text = []
        for idx, finding in enumerate(findings, start=1):
            citations = ", ".join(finding.get("citations", [])[:3]) or "No source"
            findings_text.append(
                f"{idx}. Title: {finding.get('title', 'Insight')}\n"
                f"Content: {finding.get('content', '')}\n"
                f"Evidence: {finding.get('evidence_strength', 'medium')} "
                f"(confidence={finding.get('confidence', 0.0)})\n"
                f"Citations: {citations}"
            )

        return (
            f"Topic: {topic}\n\n"
            "Using the findings below, produce a concise but substantive research summary.\n"
            "Rules:\n"
            "- Every major claim must include at least one URL citation in parentheses.\n"
            "- Separate the response into: Key Insights, Risks, and Practical Takeaways.\n"
            "- Do not invent sources.\n\n"
            "Findings:\n"
            + "\n\n".join(findings_text)
        )

    def _fallback_summary(self, topic: str, findings: list[dict[str, Any]]) -> str:
        """Generate deterministic summary if LLM is unavailable."""
        if not findings:
            return f"No reliable findings were extracted for topic: {topic}."

        lines = [
            f"Research summary for '{topic}':",
            "Key Insights:",
        ]
        for idx, finding in enumerate(findings[:5], start=1):
            source = finding.get("source") or "unknown source"
            evidence = finding.get("evidence_strength", "medium")
            lines.append(f"{idx}. {finding.get('content', '')} ({source}, evidence: {evidence})")
        return "\n".join(lines)

    def _deduplicate_findings(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge duplicated findings based on normalized content signatures."""
        deduped: dict[str, dict[str, Any]] = {}

        for finding in findings:
            signature = self._finding_signature(finding)
            if signature not in deduped:
                base = dict(finding)
                base["citations"] = list(
                    dict.fromkeys(
                        c for c in (finding.get("citations", []) + [finding.get("source")]) if c
                    )
                )
                deduped[signature] = base
                continue

            existing = deduped[signature]
            existing["confidence"] = max(
                float(existing.get("confidence", 0.0)),
                float(finding.get("confidence", 0.0)),
            )

            existing_citations = existing.get("citations", [])
            merged_citations = existing_citations + finding.get("citations", [])
            if finding.get("source"):
                merged_citations.append(finding["source"])
            existing["citations"] = list(dict.fromkeys(c for c in merged_citations if c))

            if not existing.get("source") and finding.get("source"):
                existing["source"] = finding["source"]

        return list(deduped.values())

    def _finding_signature(self, finding: dict[str, Any]) -> str:
        """Build deduplication signature for finding content."""
        source = (finding.get("source") or "").strip().lower()
        content = re.sub(r"[^a-z0-9 ]+", " ", finding.get("content", "").lower())
        content = re.sub(r"\s+", " ", content).strip()
        snippet = content[:180]
        return f"{source}|{snippet}"

    def _annotate_evidence_strength(
        self,
        findings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Tag findings with low/medium/high evidence strength."""
        for finding in findings:
            confidence = float(finding.get("confidence", 0.0))
            citations = finding.get("citations", [])
            citation_count = len(citations)

            if confidence >= 0.82 and citation_count >= 2:
                strength = "high"
            elif confidence >= 0.68 and citation_count >= 1:
                strength = "medium"
            else:
                strength = "low"

            finding["evidence_strength"] = strength
            if not finding.get("citations") and finding.get("source"):
                finding["citations"] = [finding["source"]]
        return findings
