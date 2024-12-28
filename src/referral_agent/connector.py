from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        """
        Initialize the Neo4j connection.
        Args:
            uri (str): The connection string for the Neo4j database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the Neo4j connection.
        """
        self.driver.close()

    def query(self, cypher_query, parameters=None):
        """
        Execute a Cypher query with optional parameters.
        Args:
            cypher_query (str): The Cypher query to execute.
            parameters (dict, optional): Parameters for the query.

        Returns:
            list[dict]: A list of query results where each result is a dictionary.
        """
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [record.data() for record in result][:1]
