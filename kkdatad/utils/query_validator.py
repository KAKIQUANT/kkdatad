import sqlparse
from typing import Tuple, Set

class QueryValidator:
    FORBIDDEN_KEYWORDS = {
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 
        'ALTER', 'CREATE', 'GRANT', 'REVOKE'
    }
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate SQL query for security"""
        # Parse the SQL query
        parsed = sqlparse.parse(query.upper())[0]
        
        # Check for forbidden keywords
        tokens = {token.value.upper() for token in parsed.tokens}
        forbidden = tokens.intersection(self.FORBIDDEN_KEYWORDS)
        if forbidden:
            return False, f"Query contains forbidden keywords: {forbidden}"
            
        # Check if it's a SELECT query
        if not query.strip().upper().startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
            
        return True, "Query is valid"

    def get_tables(self, query: str) -> Set[str]:
        """Extract table names from query"""
        parsed = sqlparse.parse(query)[0]
        tables = set()
        
        for token in parsed.tokens:
            if token.ttype is None and token.get_name() is not None:
                tables.add(token.get_name())
                
        return tables

query_validator = QueryValidator() 