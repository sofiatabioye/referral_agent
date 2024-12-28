from langchain.agents import Tool
from connector import Neo4jConnector
import json

def create_neo4j_tool(uri, user, password):
    """
    Create a LangChain tool that queries Neo4j using the Neo4jConnector.
    """
    connector = Neo4jConnector(uri, user, password)

    def neo4j_query_tool(input_data):
        """
        Tool function to run Cypher queries via Neo4jConnector.
        Expects input_data to be a dictionary with 'provided_conditions'.
        """
        print(f"Debug: Received input_data -> {input_data}")  # Debugging log
        data = json.loads(input_data)
        if not isinstance(data, dict):
            raise ValueError(f"Input must be a dictionary with 'provided_conditions'. Received: {type(data)} -> {data}")
        
        provided_conditions = data.get("provided_conditions")
        if not isinstance(provided_conditions, list):
            raise ValueError(f"'provided_conditions' must be a list. Received: {type(provided_conditions)} -> {provided_conditions}")
        print(f"Debug: Provided conditions -> {provided_conditions}")  # Debugging log
        # Cypher query
        cypher_query = """
            MATCH (rule:Rule)-[:HAS_CONDITION]->(condition:Condition)
            WHERE condition.name IN $provided_conditions
            WITH rule, COLLECT(condition.name) AS MatchedConditions

            // Get all conditions for the rule
            MATCH (rule)-[:HAS_CONDITION]->(allConditions:Condition)
            WITH rule, MatchedConditions, COLLECT(allConditions.name) AS AllConditions

            // Ensure all required conditions are matched
            WHERE ALL(name IN MatchedConditions WHERE name IN AllConditions)

            // Find associated actions and outcomes
            MATCH (rule)-[:LEADS_TO]->(action:Action)-[:RESULTS_IN]->(outcome:Outcome)
            RETURN DISTINCT 
                rule.name AS RuleName,
                MatchedConditions,
                AllConditions,
                action.name AS ActionDescription,
                outcome.name AS OutcomeDescription,
                SIZE(MatchedConditions) AS MatchCount
            ORDER BY MatchCount DESC;
        """
        results = connector.query(cypher_query, {"provided_conditions": provided_conditions})
        
        # Ensure the results are in a structured format
        if not results:
            return "No recommendations were found for the provided conditions."
        return results  # Return structured data (list of dictionaries)

    return Tool(
        name="Neo4jGuidelineQuery",
        func=neo4j_query_tool,
        description="Query Neo4j for guideline-based recommendations."
    )
