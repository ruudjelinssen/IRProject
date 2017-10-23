# 2IMM15 Web information retrieval and data mining

# DOWNLOAD NIPS DATA TO ONE DIRECTORY (both SQLite and CSV)


# Installing Neo4j and creating th graph database
## Installation
- Download and install JDK 8 with NetBeans 8.2 via [Oracle](http://www.oracle.com/technetwork/java/javase/downloads/jdk-netbeans-jsp-142931.html)
- Download and install Neo4j 3.1.4 via [Neo4j]( https://neo4j.com/download-thanks/?edition=community&release=3.1.4)

## Graph creation
- Open the WebInfo NetBeans project in NetBeans
- Update the password in WebInfo.java if changed in the config (default: neo4j) ```private static final String NEO4J_PASS = "neo4j";```
- In the main method in WebInfo.java, update the path with the path to the directory where the NIPS data is located ```createGraphWithReferenceRelations("path");```
- Run Neo4j
- Execute WebInfo.java to created the graph database
- Once the Java code is finished executing, Neo4j should be running for API access