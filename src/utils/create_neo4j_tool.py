from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def query(self, cypher_query, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [record.data() for record in result]

# Define the Neo4j query tool for LangChain
def create_neo4j_tool(uri, user, password):
    connector = Neo4jConnector(uri, user, password)

    def neo4j_query_tool(input_query):
        """
        This function takes input queries, runs them on Neo4j, and returns results.
        Modify the Cypher query to align with your Neo4j schema.
        """
        cypher_query = """
            MATCH (rule:Rule)-[:HAS_CONDITION]->(condition:Condition)
            WHERE condition.name IN $provided_conditions
            WITH rule, COLLECT(condition.name) AS MatchedConditions

            // Get all conditions for the rule
            MATCH (rule)-[:HAS_CONDITION]->(allConditions:Condition)
            WITH rule, MatchedConditions, COLLECT(allConditions.name) AS AllConditions

            // Ensure all required conditions are matched
            WHERE ALL(name IN MatchedConditions WHERE name IN AllConditions)

            // Check for optional conditions and ensure at least one is matched
            MATCH (rule)-[:HAS_CONDITION]->(optionalCondition:Condition)
            WITH rule, MatchedConditions, AllConditions, COLLECT(optionalCondition.name) AS OptionalConditions

            // Ensure at least one optional condition is matched
            WHERE ANY(name IN OptionalConditions WHERE name IN MatchedConditions)

            // Find associated actions and outcomes
            MATCH (rule)-[:LEADS_TO]->(action:Action)-[:RESULTS_IN]->(outcome:Outcome)
            WITH rule, MatchedConditions, AllConditions, action, outcome

            RETURN DISTINCT 
                rule.name AS RuleName,
                MatchedConditions,
                AllConditions,
                action.name AS ActionDescription,
                outcome.name AS OutcomeDescription,
                SIZE(MatchedConditions) AS MatchCount
            ORDER BY MatchCount DESC;
        """

        results = connector.query(cypher_query, {"input": input_query})
        return results

    return Tool(
        name="Neo4jGuidelineQuery",
        func=neo4j_query_tool,
        description="Search Neo4j for colorectal cancer guidelines and recommendations."
    )
