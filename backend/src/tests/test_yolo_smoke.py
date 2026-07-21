"""REQ-04: Smoke test — real YOLO inference on a sample image (no service mock)."""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("GITHUB_ACTIONS") == "true",
        reason="YOLO smoke runs locally; CI validates inference via Cypress E2E",
    ),
]

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_IMAGE = FIXTURES_DIR / "diagram.png"


@pytest.mark.skipif(not SAMPLE_IMAGE.exists(), reason="Sample diagram image not found")
async def test_yolo_smoke_real_image():
    pytest.importorskip("cv2")

    from modules.inference.services import inference_service

    image_data = SAMPLE_IMAGE.read_bytes()
    mock_inference = MagicMock()
    mock_inference.id = "smoke-test-id"
    mock_inference.insert = AsyncMock()
    mock_inference.save = AsyncMock()

    with patch(
        "modules.inference.services.inference_service.InferenceResult",
        return_value=mock_inference,
    ):
        result = await inference_service.analyze_diagram(
            image_data=image_data,
            filename="diagram.png",
            user_id="smoke-test-user",
        )

    assert result.status == "completed"
    assert len(result.components) > 0
    assert all(c.confidence > 0 for c in result.components)
