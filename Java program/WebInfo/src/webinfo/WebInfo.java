package webinfo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.regex.Pattern;
import org.neo4j.shell.ConnectionConfig;
import org.neo4j.shell.CypherShell;
import org.neo4j.shell.cli.Format;
import org.neo4j.shell.exception.CommandException;
import org.neo4j.shell.log.Logger;

/**
 * Base methods used for reference filtering and graph creation are contained in
 * this class
 *
 * @author Brouwer M.R.
 */
public class WebInfo {

    // Neo4j password, username is assumed to be the default (neo4j)
    private static final String NEO4J_PASS = "neo4j";
    
    /**
     * Get all authors as a mapping from their id to their name
     * 
     * @param path path to the directory containing authors.csv
     * @return mapping of author id's to author name
     */
    private static Map<Integer, String> getAuthors(String path) {
        File csv = new File(path + "authors.csv");
        Map<Integer, String> map = new HashMap<>();
        
        try {
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(new FileInputStream(csv), "UTF-8"))) {
                reader.readLine(); // read line to skip headers

                String line;
                String[] parts;
                String[] replace;

                // read all lines, line by line
                while ((line = reader.readLine()) != null) {
                    parts = line.split(","); // split id,name

                    // check for errors in the author name, for cases like ...\v...
                    // and remove the \v or \? from those cases
                    if (parts[1].contains("\\")) {
                        replace = parts[1].split(Pattern.quote("\\"));
                        replace[0] = replace[0].trim();
                        replace[1] = replace[1].substring(1).trim();
                        parts[1] = replace[0] + " " + replace[1];
                    }
                    
                    // if the author name contains quotes, remove them
                    if (parts[1].contains("\"")) {
                        replace = parts[1].split(Pattern.quote("\""));
                        parts[1] = replace[0].trim();
                        
                        for (int i = 1; i < replace.length; i++) {
                            parts[1] += replace[i].trim();
                        }
                    }
                    
                    // add the id => name to the mapping
                    map.put(Integer.parseInt(parts[0]), parts[1]);
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        // return the mapping
        return map;
    }
    
    /**
     * Get all paper to author relations
     * 
     * @param path path to the directory containing paper_authors.csv
     * @return list of paper to author relations
     */
    private static List<Map.Entry<Integer, Integer>> getPaperAuthors(String path) {
        File csv = new File(path + "paper_authors.csv");
        List<Map.Entry<Integer, Integer>> list = new ArrayList<>();
        
        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(csv))) {
                reader.readLine(); // read line to skip headers
                
                String line;
                String[] parts;
                
                // read all lines, line by line
                while ((line = reader.readLine()) != null) {
                    parts = line.split(","); // split id values
                    
                    // add paper to author relation to list
                    list.add(new AbstractMap.SimpleEntry(Integer.parseInt(parts[1]), Integer.parseInt(parts[2])));
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        // return list of relations
        return list;
    }
    
    /**
     * Get a mapping of all paper id's to author names who wrote the associated 
     * paper
     * 
     * @param path path to the directory containing paper_authors.csv
     * @param authors mapping of author id to author name
     * @return mapping of paper id's to a list of author names
     */
    public static Map<Integer, List<String>> getPaperAuthorsMap(String path, Map<Integer, String> authors) {
        File csv = new File(path + "paper_authors.csv");
        Map<Integer, List<String>> map = new HashMap<>();
        
        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(csv))) {
                reader.readLine(); // read line to skip headers
                
                String line;
                String[] parts;
                int p_id, a_id;
                
                // read all lines, line by line
                while ((line = reader.readLine()) != null) {
                    parts = line.split(",");
                    
                    p_id = Integer.parseInt(parts[1]); // paper id
                    a_id = Integer.parseInt(parts[2]); // author id
                    
                    // if paper id is not in the mapping
                    if (!map.containsKey(p_id)) {
                        // associate an empty list to the currect paper id
                        map.put(p_id, new ArrayList<>());
                    }
                    
                    // add the authors name to the list associated to the paper id
                    map.get(p_id).add(authors.get(a_id));
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        // return the mapping
        return map;
    }
    
    /**
     * Get a mapping of papers to their associated data, that is, year, title,
     * event_type and pdf_name
     * 
     * @param path path to the directory containing database.sqlite, that is,
     * the NIPS SQLite database
     * @return mapping of papers to their associated data
     */
    private static Map<Integer, String[]> getPapersSQLite(String path) {
        String url = "jdbc:sqlite:" + path + "database.sqlite";
        
        // query to obtain data from the SQLite database
        String query = "SELECT id,year,title,event_type,pdf_name FROM papers";
        
        Map<Integer, String[]> map = new HashMap<>();
        
        // connect to the SQLite database
        try (Connection conn = DriverManager.getConnection(url);
                Statement stmt = conn.createStatement()) {
            
            String[] parts, replace;
            ResultSet result = stmt.executeQuery(query); // execute query
            
            // for each result in the result set obtained by querying the
            // SQLite databse, add the data to the mapping
            while (result.next()) {
                
                // create a String array from the result
                parts = new String[]{
                    result.getString("year"),
                    result.getString("title"),
                    result.getString("event_type"),
                    result.getString("pdf_name")};
                
                // remove common errors from the title, starting with \
                if (parts[1].contains("\\")) {
                    replace = parts[1].split(Pattern.quote("\\"));
                    parts[1] = replace[0] + replace[1].substring(1);

                    for (int i = 2; i < replace.length; i += 2) {
                        parts[1] += replace[i] + replace[i + 1].substring(1);
                    }
                }

                // remove quotes from the title if present
                if (parts[1].contains("\"")) {
                    replace = parts[1].split(Pattern.quote("\""));
                    parts[1] = replace[0].trim();

                    for (int i = 1; i < replace.length; i++) {
                        parts[1] += replace[i].trim();
                    }
                }
                
                // add result to mapping
                map.put(result.getInt("id"), parts);
            }

            // close connection to SQLite database
            conn.close();
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        
        // return mapping
        return map;
    }
    
    /**
     * Create Neo4j graph database with authors, papers and author to paper 
     * relations
     * 
     * @param authors mapping of author id's to author names
     * @param papers mapping of paper id's to their associated data
     * @param paperAuthors list of paper to author relations
     * @throws CommandException if an error occurred while configurating 
     * the CypherShell connection or executing a Cypher query
     */
    private static void createGraph(Map<Integer, String> authors, 
            Map<Integer, String[]> papers, 
            List<Map.Entry<Integer, Integer>> paperAuthors) 
            throws CommandException {
        // CypherShell setup with empty logger
        Logger logger = new Logger() {
            @Override
            public PrintStream getOutputStream() {
                return null;
            }

            @Override
            public PrintStream getErrorStream() {
                return null;
            }

            @Override
            public void printError(Throwable thrwbl) {
                
            }

            @Override
            public void printError(String string) {
                
            }

            @Override
            public void printOut(String string) {
                
            }

            @Override
            public Format getFormat() {
                return null;
            }

            @Override
            public void setFormat(Format format) {
                
            }

            @Override
            public boolean isDebugEnabled() {
                return false;
            }
        };
        CypherShell cs = new CypherShell(logger);
        cs.connect(new ConnectionConfig(logger, "bolt://", "127.0.0.1", 7687, "neo4j", NEO4J_PASS, false));
        
        // create a node for each author
        for (Entry<Integer, String> entry : authors.entrySet()) {
            cs.execute("CREATE (A_" + entry.getKey() + ":Author {a_id: " + entry.getKey()
                    + ", name: \"" + entry.getValue() + "\"});\n");
        }
        
        // creata a node for each paper with all associated data 
        // (id => year,title,event_type,pdf_name)
        for (Entry<Integer, String[]> entry : papers.entrySet()) {
            cs.execute("CREATE (P_" + entry.getKey() + ":Paper {p_id: " + entry.getKey()
                    + ", year: " + entry.getValue()[0] + ", title: \"" + entry.getValue()[1]
                    + "\", event_type: \"" + entry.getValue()[2] + "\", pdf_name: \""
                    + entry.getValue()[3] 
                    + "\"});\n");
        }
        
        // create paper to author relations 
        for (Entry<Integer, Integer> entry : paperAuthors) {
            cs.execute("MATCH (p:Paper {p_id: " + entry.getKey() + "}), "
                    + "(a:Author {a_id: " + entry.getValue() + "})"
                    + "CREATE (a)-[:Wrote]->(p);\n");
        }
    }
    
    /**
     * Add paper to paper relations to the Neo4j graph database
     * 
     * @param path path to the directory containing the NIPS csv and SQLite data
     * @throws CommandException if an error occurred while configurating 
     * the CypherShell connection or executing a Cypher query
     */
    private static void addPaperToPaperEdges(String path) throws CommandException {
        // Get relations for (key)-[:ReferencedIn]->(value) edges
        Map<Integer, List<Integer>> authorAndPaperMatch = FilterReferences
                .authorAndPaperMatch(getReferenceBlocks(path));
        
        // setup CypherShell with empty logger
        Logger logger = new Logger() {
            @Override
            public PrintStream getOutputStream() {
                return null;
            }

            @Override
            public PrintStream getErrorStream() {
                return null;
            }

            @Override
            public void printError(Throwable thrwbl) {
                
            }

            @Override
            public void printError(String string) {
                
            }

            @Override
            public void printOut(String string) {
                
            }

            @Override
            public Format getFormat() {
                return null;
            }

            @Override
            public void setFormat(Format format) {
                
            }

            @Override
            public boolean isDebugEnabled() {
                return false;
            }
        };
        CypherShell cs = new CypherShell(logger);
        cs.connect(new ConnectionConfig(logger, "bolt://", "127.0.0.1", 7687, "neo4j", NEO4J_PASS, false));
        
        // for each paper A
        for (Entry<Integer, List<Integer>> entry : authorAndPaperMatch.entrySet()) {
            // for each paper B in which A is referenced
            for (Integer i : entry.getValue()) {
                // create a ReferencedIn relation in the graph database
                cs.execute("MATCH (p1:Paper {p_id: " + entry.getKey() + "}), "
                        + "(p2:Paper {p_id: " + i + "}) "
                        + "CREATE (p1)-[:ReferencedIn]->(p2);\n");
            }
        }
    }
    
    /**
     * Gets all reference blocks from all papers, where it is possible to 
     * determine the reference block
     * 
     * @param path path to the directory containing the NIPS csv and SQLite data
     * @return all reference blocks as map with paper_id => year,title,reference block
     */
    public static Map<Integer, String[]> getReferenceBlocks(String path) {
        String url = "jdbc:sqlite:" + path + "database.sqlite";
        
        // query to obtain data from the SQLite database
        String query = "SELECT id,year,title,paper_text FROM papers";
        
        // paper to authors mapping
        Map<Integer, List<String>> paperAuthors = getPaperAuthorsMap(path, getAuthors(path));
        
        // resulting mapping
        Map<Integer, String[]> map = new HashMap<>();
        
        // connect to the SQLite database
        try (Connection conn = DriverManager.getConnection(url);
                Statement stmt = conn.createStatement()) {
            
            String[] parts, replace;
            ResultSet result = stmt.executeQuery(query); // execute query
            
            // for each result in the result set
            while (result.next()) {
                
                // String array of paper and reference data
                parts = new String[]{
                    result.getString("year"),
                    result.getString("title"),
                    "ref",
                    "authorname"};
                
                // obtain reference block (any splitting cases due to typos)
                replace = result.getString("paper_text").toLowerCase().split("references");
                if (replace[replace.length - 1].contains("bibliography")) {
                    replace = replace[replace.length - 1].split("bibliography");
                } else if (replace[replace.length - 1].contains("referenees")) {
                    replace = replace[replace.length - 1].split("referenees");
                } else if (replace[replace.length - 1].contains("rj:i'j:rj:hcj:s")) {
                    replace = replace[replace.length - 1].split("rj:i'j:rj:hcj:s");
                } else if (replace[replace.length - 1].contains("759")) {
                    replace = replace[replace.length - 1].split("759");
                } else if (replace[replace.length - 1].contains("rererences")) {
                    replace = replace[replace.length - 1].split("rererences");
                } else if (replace[replace.length - 1].contains("reference8")) {
                    replace = replace[replace.length - 1].split("reference8");
                } else if (replace[replace.length - 1].contains("refereneea")) {
                    replace = replace[replace.length - 1].split("refereneea");
                } else if (replace[replace.length - 1].contains("reference")) {
                    replace = replace[replace.length - 1].split("reference");
                } else if (replace[replace.length - 1].contains("during song development.")) {
                    replace = replace[replace.length - 1].split("during song development.");
                } else if (replace[replace.length - 1].contains("been making will\n" + "disappear [29].")) {
                    replace = replace[replace.length - 1].split("been making will\n" + "disappear [29].");
                } else if (replace[replace.length - 1].contains("refereaces")) {
                    replace = replace[replace.length - 1].split("refereaces");
                } else if (replace[replace.length - 1].contains("way\n" + "for further testing.")) {
                    replace = replace[replace.length - 1].split("way\n" + "for further testing.");
                } else if (replace[replace.length - 1].contains("iteferences")) {
                    replace = replace[replace.length - 1].split("iteferences");
                } else if (replace[replace.length - 1].contains("are higher than on bottom.")) {
                    replace = replace[replace.length - 1].split("are higher than on bottom.");
                } else if (replace[replace.length - 1].contains("dorothy hodgkin research fellowship.")) {
                    replace = replace[replace.length - 1].split("dorothy hodgkin research fellowship.");
                } else if (replace[replace.length - 1].contains("considerable improvement in performance.")) {
                    replace = replace[replace.length - 1].split("considerable improvement in performance.");
                } else if (replace[replace.length - 1].contains("literature cited")) {
                    replace = replace[replace.length - 1].split("literature cited");
                } else if (replace[replace.length - 1].contains("ref erences")) {
                    replace = replace[replace.length - 1].split("ref erences");
                } else if (replace[replace.length - 1].contains("refel~ences")) {
                    replace = replace[replace.length - 1].split("refel~ences");
                } else if (replace[replace.length - 1].contains("refe ren ces")) {
                    replace = replace[replace.length - 1].split("refe ren ces");
                } else if (replace[replace.length - 1].contains(", such as error-correction.")) {
                    replace = replace[replace.length - 1].split(", such as error-correction.");
                } else if (replace[replace.length - 1].contains("ref eren ces")) {
                    replace = replace[replace.length - 1].split("ref eren ces");
                } else if (replace[replace.length - 1].contains("r e f er e n ce s")) {
                    replace = replace[replace.length - 1].split("r e f er e n ce s");
                } else if (replace[replace.length - 1].contains("r e f e re n c e s")) {
                    replace = replace[replace.length - 1].split("r e f e re n c e s");
                } else if (replace[replace.length - 1].contains("r ef erence s")) {
                    replace = replace[replace.length - 1].split("r ef erence s");
                } else if (replace[replace.length - 1].contains("algorithm.\n" + "\n" +"8\n" + "\n" + "432\n" + "433")) {
                    replace = replace[replace.length - 1].split("algorithm.\n" + "\n" +"8\n" + "\n" + "432\n" + "433");
                } else if (replace[replace.length - 1].contains("refrences")) {
                    replace = replace[replace.length - 1].split("refrences");
                }
                
                // get reference block and set to String array parts
                String refBlock = replace[replace.length - 1];
                parts[2] = refBlock;
                
                // if a reference block was found (implies the doc is split)
                if (replace.length > 1) {
                    // add authors to String array parts, separated by ;
                    if (paperAuthors.containsKey(result.getInt("id"))) {
                        parts[3] = String.join(";", paperAuthors.get(result.getInt("id")));
                    }
                    
                    // add paper and reference block
                    map.put(result.getInt("id"), parts);
                }
            }

            // close connection
            conn.close();
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        
        // return mapping
        return map;
    }
    
    /**
     * Get authors names split by space
     * 
     * @param path path to the directory containing authors.csv
     * @return mapping of author id to authors name split by space
     */
    public static Map<Integer, String[]> getAuthorNamesSplit(String path) {
        Map<Integer, String> authors = getAuthors(path); // get author mapping
        Map<Integer, String[]> names = new HashMap<>();
        
        // split names and add split names as array to mapping
        authors.entrySet().forEach(entry 
                -> names.put(entry.getKey(), entry.getValue().split(" ")));
        
        // return mapping
        return names;
    }
    
    /**
     * Extract paper titles from the reference block mapping. This limits titles
     * to titles of papers of which a reference block was found rather than 
     * using all titles in the database
     * 
     * @param referenceBlocks reference blocks
     * @return titles extracted from reference block as mapping from paper id to
     * paper title
     */
    public static Map<Integer, String> extractPaperTitles(
            Map<Integer, String[]> referenceBlocks) {
        // mapping of paper id to title
        Map<Integer, String> titles = new HashMap<>();
        
        // extract title and add to mapping
        referenceBlocks.entrySet().forEach(entry -> 
                titles.put(entry.getKey(), entry.getValue()[1]));
        
        // return mapping
        return titles;
    }
    
    /**
     * Create Neo4j graph database with reference relations
     * 
     * @param path path to the directory containing the NIPS csv and SQLite data
     * @throws CommandException if an error occurred while configurating 
     * the CypherShell connection or executing a Cypher query
     */
    public static void createGraphWithReferenceRelations(String path) throws CommandException {
        createGraph(getAuthors(path), getPapersSQLite(path), getPaperAuthors(path));
        addPaperToPaperEdges(path);
    }
    
    /**
     * Executes {@link #createGraphWithReferenceRelations(java.lang.String)}
     * 
     * @param args none required
     */
    public static void main(String[] args) throws Exception {
        createGraphWithReferenceRelations("path");
    }
    
}
