from __future__ import annotations

import operator
import re
from collections.abc import Callable
from typing import Any, cast

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition
from maa.define import RectType
from utils import logger
from utils.maa_types import is_hit, ocr_text
from utils.params import parse_params


@AgentServer.custom_recognition("ExampleRecognition")
class ExampleRecognition(CustomRecognition):
    """Demonstrates a minimal custom recognition flow.

    Examples:
        Reuse an existing recognition node::

            {
                "node": "ExistingRecognitionNode",
                "detail": {"source": "example"}
            }

        Return a static box::

            {
                "box": [0, 0, 100, 100],
                "detail": {"source": "static-box"}
            }
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult | None:
        try:
            params = parse_params(argv.custom_recognition_param)
            node_name = params.get("node")
            if node_name is None:
                node_name = params.get("template_node")

            if node_name is not None and (not isinstance(node_name, str) or not node_name):
                raise ValueError("node must be a non-empty string.")

            box_value = params.get("box")
            if box_value is not None and not (
                isinstance(box_value, list) and len(box_value) == 4 and all(isinstance(item, int) for item in box_value)
            ):
                raise ValueError("box must be [x, y, w, h].")
            box = cast(RectType | None, box_value)

            detail_value = params.get("detail", {})
            if detail_value is None:
                detail_value = {}
            if not isinstance(detail_value, dict):
                raise ValueError("detail must be an object.")
            detail = cast(dict[str, Any], detail_value)
        except ValueError as error:
            logger.error("ExampleRecognition: %s", error)
            return None

        if node_name:
            reco_detail = context.run_recognition(node_name, argv.image)
            if not is_hit(reco_detail):
                return None
            reco_box = getattr(reco_detail, "box", None)
            if reco_box is None:
                return None

            result_detail: dict[str, Any] = {
                "source": "run_recognition",
                "node": node_name,
                "detail": getattr(reco_detail, "detail", None),
            }
            result_detail.update(detail)
            return CustomRecognition.AnalyzeResult(
                box=cast(RectType, reco_box),
                detail=result_detail,
            )

        if box is not None:
            return CustomRecognition.AnalyzeResult(box=box, detail=detail)

        logger.info("ExampleRecognition has no node or box configured; replace it with project logic.")
        return None


NUMBER_PATTERN = r"\d+(?:\.\d+)?"

COMPARISONS: dict[str, Callable[[float, float], bool]] = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


def _as_number(value: Any, key: str) -> float:
    """Read a pipeline param as float, accepting numeric strings (client type lowering)."""
    if isinstance(value, bool):
        raise ValueError(f"{key} must be a number, got bool")
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError as error:
            raise ValueError(f"{key} must be a number, got {value!r}") from error
    raise ValueError(f"{key} must be a number, got {type(value).__name__}")


def _extract_numbers(text: str, pattern: re.Pattern[str]) -> list[float]:
    """Return every *pattern* match in *text* that can be read as a number."""
    numbers: list[float] = []
    for match in pattern.finditer(text):
        try:
            numbers.append(float(match.group()))
        except ValueError:
            continue
    return numbers


@AgentServer.custom_recognition("NumberThreshold")
class NumberThreshold(CustomRecognition):
    """Hit when a number read by a reused OCR node satisfies a comparison.

    The OCR node named by ``ocr_node`` is recognized against the incoming
    screenshot; the numbers found in its text are compared with ``threshold``.
    On a hit the OCR box is returned, so a ``Click`` action with ``target: true``
    clicks the recognized text itself.

    Examples:
        `custom_recognition_param`::

            {
                "ocr_node": "OutpostDefense.ReadPercent",
                "threshold": 50,
                "comparison": ">",
                "pattern": "\\d+(?:\\.\\d+)?",
                "index": 0
            }
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult | None:
        try:
            params = parse_params(argv.custom_recognition_param, "ocr_node", "threshold")

            ocr_node = params["ocr_node"]
            if not isinstance(ocr_node, str) or not ocr_node:
                raise ValueError("ocr_node must be a non-empty string.")

            threshold = _as_number(params["threshold"], "threshold")

            comparison = params.get("comparison", ">")
            if comparison not in COMPARISONS:
                raise ValueError(f"comparison must be one of {sorted(COMPARISONS)}, got {comparison!r}")

            raw_pattern = params.get("pattern", NUMBER_PATTERN)
            if not isinstance(raw_pattern, str) or not raw_pattern:
                raise ValueError("pattern must be a non-empty string.")
            try:
                pattern = re.compile(raw_pattern)
            except re.error as error:
                raise ValueError(f"pattern is not a valid regex: {error}") from error

            index = params.get("index", 0)
            if isinstance(index, bool) or not isinstance(index, int):
                raise ValueError("index must be an int.")
        except ValueError as error:
            logger.error("NumberThreshold: {}", error)
            return None

        compare = COMPARISONS[str(comparison)]

        reco_detail = context.run_recognition(ocr_node, argv.image)
        if not is_hit(reco_detail):
            logger.debug("NumberThreshold: OCR node {} did not hit.", ocr_node)
            return None

        text = ocr_text(reco_detail)
        numbers = _extract_numbers(text, pattern)
        if not numbers:
            logger.info("NumberThreshold: no number in OCR text {!r} (node {}).", text, ocr_node)
            return None

        if not -len(numbers) <= index < len(numbers):
            logger.error("NumberThreshold: index {} is out of range for {} number(s).", index, len(numbers))
            return None

        value = numbers[index]
        if not compare(value, threshold):
            logger.debug("NumberThreshold: [{}] {} {} is false (text {!r}).", value, comparison, threshold, text)
            return None

        return CustomRecognition.AnalyzeResult(
            box=cast(RectType, reco_detail.box),
            detail={
                "ocr_node": ocr_node,
                "text": text,
                "value": value,
                "threshold": threshold,
                "comparison": comparison,
            },
        )
