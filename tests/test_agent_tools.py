"""Tests for agent tools."""
import pytest
from unittest.mock import Mock, patch
from tinydsl.agent_tools.generic_dsl_client import GenericDSLClient, DSLTester
from tinydsl.agent_tools.tinydsl_tool import TinyDSLTool
from tinydsl.agent_tools.kait_agent import KAITAgent


# ====================
# Unit Tests (Mocked)
# ====================

class TestGenericDSLClient:
    """Test GenericDSLClient."""

    def test_client_initialization(self):
        """Test client initializes with base URL."""
        client = GenericDSLClient(base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"

    @patch('requests.get')
    def test_list_dsls(self, mock_get):
        """Test listing available DSLs."""
        mock_get.return_value.json.return_value = {
            "dsls": ["tinycalc", "tinysql", "gli", "lexi"]
        }

        client = GenericDSLClient(base_url="http://localhost:8000")
        dsls = client.list_dsls()

        assert "tinycalc" in dsls
        assert "tinysql" in dsls
        assert "gli" in dsls
        assert "lexi" in dsls

    @patch('requests.post')
    def test_run_code(self, mock_post):
        """Test running DSL code."""
        mock_post.return_value.json.return_value = {
            "success": True,
            "output": "5.0 grobble"
        }

        client = GenericDSLClient(base_url="http://localhost:8000")
        result = client.run("tinycalc", "convert 5 flurb to grobble")

        assert result["success"] is True
        assert "grobble" in result["output"]

    @patch('requests.post')
    def test_run_all_tasks(self, mock_post):
        """Test running all tasks for a DSL."""
        mock_post.return_value.json.return_value = {
            "evaluation": {
                "results": [
                    {"task_id": "001", "success": True}
                ],
                "summary": {
                    "total_tasks": 1,
                    "accuracy": 1.0
                }
            }
        }

        client = GenericDSLClient(base_url="http://localhost:8000")
        result = client.run_all_tasks("tinycalc", ["001"])

        assert "evaluation" in result
        assert result["evaluation"]["summary"]["accuracy"] == 1.0


class TestKAITAgent:
    """Test KAITAgent."""

    @patch('tinydsl.agent_tools.kait_agent.GenericDSLClient')
    def test_kait_agent_initialization(self, mock_client_class):
        """Test KAIT agent initializes correctly."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        agent = KAITAgent("tinycalc", base_url="http://localhost:8000")

        assert agent.dsl_name == "tinycalc"
        assert agent.client == mock_client

    @patch('tinydsl.agent_tools.kait_agent.GenericDSLClient')
    def test_run_baseline(self, mock_client_class):
        """Test running baseline evaluation."""
        mock_client = Mock()
        mock_client.run_all_tasks.return_value = {
            "evaluation": {
                "summary": {"accuracy": 0.5}
            }
        }
        mock_client_class.return_value = mock_client

        agent = KAITAgent("tinycalc")
        result = agent.run_baseline(["001", "002"])

        assert "accuracy" in result
        assert result["accuracy"] == 0.5

    @patch('tinydsl.agent_tools.kait_agent.GenericDSLClient')
    def test_expose(self, mock_client_class):
        """Test exposure phase."""
        mock_client = Mock()
        mock_client.run.return_value = {"success": True, "output": "result"}
        mock_client_class.return_value = mock_client

        agent = KAITAgent("tinycalc")
        result = agent.expose(["code1", "code2"], token_budget=100)

        assert "episodes_seen" in result
        assert result["episodes_seen"] == 2

    @patch('tinydsl.agent_tools.kait_agent.GenericDSLClient')
    def test_evaluate_post_exposure(self, mock_client_class):
        """Test post-exposure evaluation."""
        mock_client = Mock()
        mock_client.run_all_tasks.return_value = {
            "evaluation": {
                "summary": {"accuracy": 0.7}
            }
        }
        mock_client_class.return_value = mock_client

        agent = KAITAgent("tinycalc")
        agent.baseline_results = {"accuracy": 0.5}
        result = agent.evaluate_post_exposure(["003", "004"])

        assert "accuracy" in result
        assert "acquisition_gain" in result

    @patch('tinydsl.agent_tools.kait_agent.GenericDSLClient')
    def test_evaluate_transfer(self, mock_client_class):
        """Test transfer evaluation."""
        mock_client = Mock()
        mock_client.run_all_tasks.return_value = {
            "evaluation": {
                "summary": {"accuracy": 0.6}
            }
        }
        mock_client_class.return_value = mock_client

        agent = KAITAgent("tinycalc")
        result = agent.evaluate_transfer(["005", "006"])

        assert "transfer_accuracy" in result

    @patch('tinydsl.agent_tools.kait_agent.GenericDSLClient')
    def test_calculate_kait_metrics(self, mock_client_class):
        """Test calculating KAIT metrics."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        agent = KAITAgent("tinycalc")
        agent.baseline_results = {"accuracy": 0.4}
        agent.post_exposure_results = {"accuracy": 0.7}
        agent.transfer_results = {"transfer_accuracy": 0.6}

        metrics = agent.calculate_kait_metrics()

        assert "acquisition_gain" in metrics
        assert "transfer_score" in metrics
        assert metrics["acquisition_gain"] == pytest.approx(0.3)
        assert metrics["transfer_score"] == 0.6


# ====================
# Integration Tests (Require Server)
# ====================

@pytest.mark.integration
@pytest.mark.requires_server
class TestTinyDSLToolIntegration:
    """Integration tests for TinyDSLTool. Requires running server."""

    @pytest.fixture
    def tool(self):
        """Create TinyDSLTool instance."""
        return TinyDSLTool()

    def test_tinycalc_run(self, tool):
        """Test TinyCalc execution."""
        result = tool.run_tinycalc("define 1 flurb = 3.5 grobble\nconvert 4 flurb to grobble")
        assert result.get("status") == "ok"
        assert "14.0 grobble" in result.get("output", "")

    def test_tinysql_run(self, tool):
        """Test TinySQL execution."""
        result = tool.run_tinysql("show tables")
        assert result.get("status") == "ok"

    def test_lexi_run(self, tool):
        """Test Lexi execution."""
        result = tool.run_lexi('say "Hello world!"')
        assert result.get("status") == "ok"
        assert "Hello world!" in result.get("output", "")

    def test_lexi_memory(self, tool):
        """Test Lexi memory operations."""
        # Clear memory
        tool.clear_memory()

        # Set memory
        tool.set_memory("test_key", "test_value")

        # Get memory
        mem = tool.get_memory()
        assert mem.get("memory", {}).get("test_key") == "test_value"

        # Clear again
        tool.clear_memory()
        mem = tool.get_memory()
        assert mem.get("memory", {}) == {}

    def test_gli_run(self, tool):
        """Test Gli execution."""
        result = tool.run_code("set color red\nset size 10\ndraw circle x=50 y=50", save=False)
        assert result.get("status") == "ok"

    def test_gli_list_examples(self, tool):
        """Test Gli examples listing."""
        examples = tool.list_examples()
        assert isinstance(examples, list)


@pytest.mark.integration
@pytest.mark.requires_server
class TestGenericDSLClientIntegration:
    """Integration tests for GenericDSLClient. Requires running server."""

    @pytest.fixture
    def client(self):
        """Create GenericDSLClient instance."""
        return GenericDSLClient()

    def test_list_dsls(self, client):
        """Test listing available DSLs."""
        dsls = client.list_dsls()
        assert "gli" in dsls
        assert "lexi" in dsls
        assert "tinycalc" in dsls
        assert "tinysql" in dsls

    def test_run_tinycalc(self, client):
        """Test running TinyCalc code."""
        result = client.run("tinycalc", "define 1 flurb = 5 grobble\nconvert 2 flurb to grobble")
        assert result.get("status") == "ok"
        assert "10.0 grobble" in result.get("output", "")

    def test_run_tinysql(self, client):
        """Test running TinySQL code."""
        result = client.run("tinysql", "show tables")
        assert result.get("status") == "ok"

    def test_run_lexi(self, client):
        """Test running Lexi code."""
        result = client.run("lexi", 'say "Hello from generic client!"')
        assert result.get("status") == "ok"
        assert "Hello from generic client!" in result.get("output", "")

    def test_run_gli(self, client):
        """Test running Gli code."""
        result = client.run("gli", "set color blue\ndraw circle x=50 y=50", save=False)
        assert result.get("status") == "ok"

    def test_dsl_tester(self, client):
        """Test DSLTester helper class."""
        tester = DSLTester(client)

        # Test basic DSL execution
        success = tester.test_dsl_basic("lexi", 'say "test"')
        assert success is True


# ====================
# Test Runner
# ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
