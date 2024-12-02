from typing import Dict
import re
from kkdatad.utils.exceptions import QuotaExceededException

class QueryComplexityLimiter:
    def __init__(self):
        self.complexity_weights = {
            'JOIN': 2,
            'GROUP BY': 1.5,
            'ORDER BY': 1.2,
            'HAVING': 1.5,
            'UNION': 2,
            'DISTINCT': 1.3
        }

    def calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score"""
        complexity = 1.0
        query_upper = query.upper()
        
        for keyword, weight in self.complexity_weights.items():
            if keyword in query_upper:
                complexity *= weight
                
        # Add weight for each table in JOIN
        join_count = len(re.findall(r'JOIN', query_upper))
        if join_count > 0:
            complexity *= (1 + (0.5 * join_count))
            
        return complexity

    async def check_limit(self, user_id: int, query: str) -> bool:
        """Check if query complexity is within user's limits"""
        complexity = self.calculate_complexity(query)
        
        # Example threshold - should be configurable per user
        if complexity > 10:
            raise QuotaExceededException()
            
        return True

complexity_limiter = QueryComplexityLimiter() 