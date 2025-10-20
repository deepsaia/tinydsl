"""Tests for TinySQL DSL."""

from tinydsl.tinysql.tinysql import TinySQLInterpreter


class TestTinySQL:
    """Test TinySQL DSL."""

    def test_tinysql_initialization(self):
        """Test TinySQL initializes correctly."""
        sql = TinySQLInterpreter()
        assert sql.name == "tinysql"

    def test_select_query(self):
        """Test select statement."""
        sql = TinySQLInterpreter()
        code = "select name, age"
        result = sql.execute(code)
        assert isinstance(result, str)

    def test_load_and_filter(self):
        """Test load and filter statements."""
        sql = TinySQLInterpreter()
        code = """load table users from "users.json"
filter users where age > 25"""
        result = sql.execute(code)
        assert isinstance(result, str)

    def test_sort_statement(self):
        """Test sort statement."""
        sql = TinySQLInterpreter()
        code = """load table users from "data.json"
sort by age desc"""
        result = sql.execute(code)
        assert isinstance(result, str)

    def test_limit_statement(self):
        """Test limit statement."""
        sql = TinySQLInterpreter()
        code = """load table users from "data.json"
limit 10"""
        result = sql.execute(code)
        assert isinstance(result, str)

    def test_show_tables(self):
        """Test show tables statement."""
        sql = TinySQLInterpreter()
        code = "show tables"
        result = sql.execute(code)
        assert isinstance(result, str)

    def test_invalid_query(self):
        """Test handling of invalid SQL."""
        sql = TinySQLInterpreter()
        code = "INVALID QUERY"
        try:
            result = sql.execute(code)
            # If it returns a result, it should be a string
            assert isinstance(result, str)
        except (ValueError, Exception) as e:
            # Or it should raise an error
            assert "error" in str(e).lower() or "unexpected" in str(e).lower()
