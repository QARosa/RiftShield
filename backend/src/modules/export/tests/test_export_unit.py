import pytest
import json
from unittest.mock import AsyncMock, patch


class TestExportServiceUnit:
    @pytest.mark.asyncio
    async def test_export_json_format(self):
        from modules.export.services.export_service import export_data
        with patch("modules.export.services.export_service._get_inferences", new_callable=AsyncMock) as mock_inf:
            mock_inf.return_value = [{"id": "1", "filename": "test.png", "status": "completed", "components": [], "processing_time_ms": 100, "fallback_used": False, "created_at": "2026-01-01"}]
            with patch("modules.export.services.export_service._get_threats", new_callable=AsyncMock) as mock_thr:
                mock_thr.return_value = []
                with patch("modules.export.services.export_service._get_dataset", new_callable=AsyncMock) as mock_ds:
                    mock_ds.return_value = []
                    result = await export_data(
                        user_id="user123",
                        sections=["inferences"],
                        fmt="json",
                        zip_output=False,
                    )
                    assert "filename" in result
                    assert result["filename"].endswith(".json")
                    content = json.loads(result["content"])
                    assert "analise_de_diagramas" in content

    @pytest.mark.asyncio
    async def test_export_empty_sections(self):
        from modules.export.services.export_service import export_data
        with patch("modules.export.services.export_service._get_inferences", new_callable=AsyncMock) as mock_inf:
            mock_inf.return_value = []
            with patch("modules.export.services.export_service._get_threats", new_callable=AsyncMock) as mock_thr:
                mock_thr.return_value = []
                with patch("modules.export.services.export_service._get_dataset", new_callable=AsyncMock) as mock_ds:
                    mock_ds.return_value = []
                    result = await export_data(
                        user_id="user123",
                        sections=[],
                        fmt="json",
                    )
                    content = json.loads(result["content"])
                    assert content == {}

    @pytest.mark.asyncio
    async def test_export_pdf_generation(self):
        from modules.export.services.export_service import export_data
        with patch("modules.export.services.export_service._get_inferences", new_callable=AsyncMock) as mock_inf:
            mock_inf.return_value = []
            with patch("modules.export.services.export_service._get_threats", new_callable=AsyncMock) as mock_thr:
                mock_thr.return_value = []
                with patch("modules.export.services.pdf_generator.generate_pdf") as mock_pdf:
                    mock_pdf.return_value = b"%PDF-1.4 fake pdf content"
                    with patch("modules.export.services.pdf_generator.build_pdf_sections") as mock_build:
                        mock_build.return_value = []
                        result = await export_data(
                            user_id="user123",
                            sections=["inferences"],
                            fmt="pdf",
                        )
                        assert "filename" in result
                        assert result["filename"].endswith(".pdf")

    @pytest.mark.asyncio
    async def test_export_unsupported_format(self):
        from modules.export.services.export_service import export_data
        with patch("modules.export.services.export_service._get_inferences", new_callable=AsyncMock, return_value=[]), \
             patch("modules.export.services.export_service._get_threats", new_callable=AsyncMock, return_value=[]), \
             patch("modules.export.services.export_service._get_dataset", new_callable=AsyncMock, return_value=[]), \
             patch("modules.export.services.export_service._get_vulnerabilities", new_callable=AsyncMock, return_value=[]), \
             patch("modules.export.services.export_service._get_countermeasures", new_callable=AsyncMock, return_value=[]), \
             patch("modules.export.services.export_service._get_training_logs", new_callable=AsyncMock, return_value=[]):
            result = await export_data(
                user_id="user123",
                sections=["inferences"],
                fmt="xml",
            )
        assert "error" in result
        assert "não suportado" in result["error"]

    def test_pick_pt_label(self):
        from modules.export.services.export_service import _pick
        obj = {"title_pt": "Título PT", "title_en": "Title EN"}
        result = _pick(obj, "pt-BR", "title")
        assert result == "Título PT"

    def test_pick_en_label(self):
        from modules.export.services.export_service import _pick
        obj = {"title_pt": "Título PT", "title_en": "Title EN"}
        result = _pick(obj, "en-US", "title")
        assert result == "Title EN"

    def test_pick_fallback_to_pt(self):
        from modules.export.services.export_service import _pick
        obj = {"title_pt": "Título PT"}
        result = _pick(obj, "fr-FR", "title")
        assert result == "Título PT"

    def test_pick_empty(self):
        from modules.export.services.export_service import _pick
        obj = {}
        result = _pick(obj, "pt-BR", "title")
        assert result == ""
