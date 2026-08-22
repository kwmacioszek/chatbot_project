
from __future__ import annotations

from dataclasses import dataclass, field

from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import RunUsage
from pydantic_graph import BaseNode, End, Graph, GraphBuilder, GraphRunContext

from agents.faq.agent import create_agent
from agents.faq.knowledge_base import FAQ
from agents.triage.agent import create_triage_agent
from agents.config import Settings


@dataclass
class HandoffResult:
    """Final answer plus the messages exchanged, so callers can keep history."""

    output: str
    messages: list[ModelMessage]


@dataclass
class HandoffInput:
    """Question plus prior conversation history, fed into the graph."""

    question: str
    message_history: list[ModelMessage] = field(default_factory=list)


@dataclass
class TriageNode(BaseNode[None, Settings, HandoffResult]):
    """Runs the triage agent and routes to the FAQ agent or a human hand-off."""

    question: str
    message_history: list[ModelMessage]

    async def run(
        self, ctx: GraphRunContext[None, Settings]
    ) -> "FaqNode | HumanHandoffNode | ComplaintNode":
        result = await create_triage_agent(ctx.deps).run(
            self.question, message_history=self.message_history
        )
        triage = result.output
        if triage.target == "human":
            return HumanHandoffNode(reason=triage.reason)
        if triage.target == "complaint":
            return ComplaintNode(reason=triage.reason)
        return FaqNode(question=self.question, usage=result.usage)


@dataclass
class FaqNode(BaseNode[None, Settings, HandoffResult]):
    """Runs the FAQ agent (with usage carried over from triage) and ends the graph."""

    question: str
    usage: RunUsage

    async def run(self, ctx: GraphRunContext[None, Settings]) -> End[HandoffResult]:
        result = await create_agent(ctx.deps).run(self.question, usage=self.usage)
        return End(HandoffResult(result.output, result.all_messages()))


@dataclass
class HumanHandoffNode(BaseNode[None, Settings, HandoffResult]):
    """Ends the graph with a canned message pointing to the helpline."""

    reason: str

    async def run(self, ctx: GraphRunContext[None, Settings]) -> End[HandoffResult]:
        return End(
            HandoffResult(
                f"To pytanie wymaga kontaktu z konsultantem ({self.reason}).\n\n"
                f"{FAQ['helpline contact']}",
                [],
            )
        )

@dataclass
class ComplaintNode(BaseNode[None, Settings, HandoffResult]):
    reason: str

    async def run(
        self, ctx: GraphRunContext[None, Settings]
    ) -> End[HandoffResult]:
        return End(
            HandoffResult(
                f"Przekazuję zgłoszenie do działu reklamacji ({self.reason}).\n\n"
                f"{FAQ['helpline contact']}",
                [],
            )
        )


def build_handoff_graph() -> Graph[None, Settings, HandoffResult, HandoffInput]:
    builder = GraphBuilder(
        name="handoff_graph",
        input_type=HandoffInput,
        output_type=HandoffResult,
        deps_type=Settings,
    )

    @builder.step
    async def start(ctx) -> TriageNode:
        return TriageNode(ctx.inputs.question, ctx.inputs.message_history)

    builder.add(
        builder.node(TriageNode),
        builder.node(FaqNode),
        builder.node(HumanHandoffNode),
        builder.node(ComplaintNode),
        builder.edge_from(builder.start_node).to(start),
    )
    return builder.build()


def ask(
    question: str,
    settings: Settings | None = None,
    message_history: list[ModelMessage] | None = None,
) -> HandoffResult:
    """Runs the hand-off graph and returns the answer plus updated history."""
    handoff_graph = build_handoff_graph()

    settings = settings or Settings()
    return handoff_graph.run_sync(
        inputs=HandoffInput(question, message_history or []), deps=settings
    )
