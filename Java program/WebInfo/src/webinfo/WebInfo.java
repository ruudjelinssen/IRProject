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
 *
 * @author Brouwer M.R.
 */
public class WebInfo {

    //private static final String PATH = "D:\\marcbrouwer\\Documents\\TUe\\2IMM15 - Web information retrieval and data mining\\nips-papers\\";
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        //createGraph(getAuthors(), getPapersSQLite(), getPaperAuthors());
        Map<Integer, String[]> references = getReferenceBlocks("C:\\Users\\Arjan\\Documents\\IRProject\\Dataset\\");
        FilterReferences filter = new FilterReferences();
        Map<Integer, String> authors = getAuthors("C:\\Users\\Arjan\\Documents\\IRProject\\Dataset\\");
        List<Map.Entry<Integer, Integer>> results = filter.filter(references, authors);
    }
    
    private static Map<Integer, String> getAuthors(String path) {
        File csv = new File(path + "authors.csv");
        Map<Integer, String> map = new HashMap<>();
        
        try {
            try (BufferedReader reader = new BufferedReader( new InputStreamReader(new FileInputStream(csv), "UTF-8"))) {
                reader.readLine();
                
                String line;
                String[] parts;
                String[] replace;
                
                while ((line = reader.readLine()) != null) {
                    parts = line.split(",");
                    
                    if (parts[1].contains("\\")) {
                        replace = parts[1].split(Pattern.quote("\\"));
                        replace[0] = replace[0].trim();
                        replace[1] = replace[1].substring(1).trim();
                        parts[1] = replace[0] + " " + replace[1];
                    }
                    
                    if (parts[1].contains("\"")) {
                        replace = parts[1].split(Pattern.quote("\""));
                        parts[1] = replace[0].trim();
                        
                        for (int i = 1; i < replace.length; i++) {
                            parts[1] += replace[i].trim();
                        }
                    }
                    
                    map.put(Integer.parseInt(parts[0]), parts[1]);
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        return map;
    }
    
    private static List<Map.Entry<Integer, Integer>> getPaperAuthors(String path) {
        File csv = new File(path + "paper_authors.csv");
        List<Map.Entry<Integer, Integer>> list = new ArrayList<>();
        
        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(csv))) {
                reader.readLine();
                
                String line;
                String[] parts;
                
                while ((line = reader.readLine()) != null) {
                    parts = line.split(",");
                    
                    list.add(new AbstractMap.SimpleEntry(Integer.parseInt(parts[1]), Integer.parseInt(parts[2])));
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        return list;
    }
    
    public static Map<Integer, List<String>> getPaperAuthorsMap(String path, Map<Integer, String> authors) {
        File csv = new File(path + "paper_authors.csv");
        Map<Integer, List<String>> map = new HashMap<>();
        
        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(csv))) {
                reader.readLine();
                
                String line;
                String[] parts;
                int p_id, a_id;
                
                while ((line = reader.readLine()) != null) {
                    parts = line.split(",");
                    
                    p_id = Integer.parseInt(parts[1]);
                    a_id = Integer.parseInt(parts[2]);
                    
                    if (!map.containsKey(p_id)) {
                        map.put(p_id, new ArrayList<>());
                    }
                    
                    map.get(p_id).add(authors.get(a_id));
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        return map;
    }
    
    private static Map<Integer, String[]> getPapers(String path) {
        File csv = new File(path + "papers.csv");
        Map<Integer, String[]> map = new HashMap<>();
        
        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(csv))) {
                reader.readLine();
                
                String line;
                String paper = "";
                String[] parts;
                
                while ((line = reader.readLine()) != null) {
                    if (!line.equals("\"")) {
                        paper += line;
                    } else {
                        parts = paper.split(",", 7);
                        parts[6] = parts[6].substring(1);
                        
                        map.put(Integer.parseInt(parts[0]), Arrays.copyOfRange(parts, 1, 7));
                        paper = "";
                    }
                }
            }
        } catch (IOException e) {
            System.err.println(e);
        }
        
        return map;
    }
    
    private static final void createGraph(Map<Integer, String> authors, 
            Map<Integer, String[]> papers, List<Map.Entry<Integer, Integer>> paperAuthors) 
            throws CommandException {
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
        cs.connect(new ConnectionConfig(logger, "bolt://", "127.0.0.1", 7687, "neo4j", "****", false));
        
        // authors
        for (Entry<Integer, String> entry : authors.entrySet()) {
            cs.execute("CREATE (A_" + entry.getKey() + ":Author {a_id: " + entry.getKey()
                    + ", name: \"" + entry.getValue() + "\"});\n");
        }
        
        // papers (id => year,title,event_type,pdf_name)
        for (Entry<Integer, String[]> entry : papers.entrySet()) {
            cs.execute("CREATE (P_" + entry.getKey() + ":Paper {p_id: " + entry.getKey()
                    + ", year: " + entry.getValue()[0] + ", title: \"" + entry.getValue()[1]
                    + "\", event_type: \"" + entry.getValue()[2] + "\", pdf_name: \""
                    + entry.getValue()[3] 
                    + "\"});\n");
                    //+ "\", abstract: \"" + entry.getValue()[4]
                    //+ "\", paper_text: \"" + entry.getValue()[5] + "\"});\n");
        }
        
        // paper <-> author relations 
        for (Entry<Integer, Integer> entry : paperAuthors) {
            cs.execute("MATCH (p:Paper {p_id: " + entry.getKey() + "}), "
                    + "(a:Author {a_id: " + entry.getValue() + "})"
                    + "CREATE (a)-[:Wrote]->(p);\n");
        }
    }
    
    private static Map<Integer, String[]> getPapersSQLite(String path) {
        String url = "jdbc:sqlite:" + path + "database.sqlite";
        String query = "SELECT id,year,title,event_type,pdf_name FROM papers";
        
        Map<Integer, String[]> map = new HashMap<>();
        
        try (Connection conn = DriverManager.getConnection(url);
                Statement stmt = conn.createStatement()) {
            
            String[] parts, replace;
            ResultSet result = stmt.executeQuery(query);
            while (result.next()) {
                
                parts = new String[]{
                    result.getString("year"),
                    result.getString("title"),
                    result.getString("event_type"),
                    result.getString("pdf_name")};
                
                if (parts[1].contains("\\")) {
                        replace = parts[1].split(Pattern.quote("\\"));
                        parts[1] = replace[0] + replace[1].substring(1);
                        
                        for (int i = 2; i < replace.length; i += 2) {
                            parts[1] += replace[i] + replace[i + 1].substring(1);
                        }
                    }
                
                if (parts[1].contains("\"")) {
                    replace = parts[1].split(Pattern.quote("\""));
                    parts[1] = replace[0].trim();

                    for (int i = 1; i < replace.length; i++) {
                        parts[1] += replace[i].trim();
                    }
                }
                
                map.put(result.getInt("id"), parts);
            }

            conn.close();
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        
        return map;
    }
    
    /**
     * Gets all reference blocks from all papers where possible
     * 
     * @return all reference blocks as map with paper_id => year,title,reference block
     */
    public static Map<Integer, String[]> getReferenceBlocks(String path) {
        String url = "jdbc:sqlite:" + path + "database.sqlite";
        String query = "SELECT id,year,title,paper_text FROM papers";
        
        Map<Integer, List<String>> paperAuthors = getPaperAuthorsMap(path, getAuthors(path));
        
        Map<Integer, String[]> map = new HashMap<>();
        
        try (Connection conn = DriverManager.getConnection(url);
                Statement stmt = conn.createStatement()) {
            
            String[] parts, replace;
            ResultSet result = stmt.executeQuery(query);
            while (result.next()) {
                
                parts = new String[]{
                    result.getString("year"),
                    result.getString("title"),
                    "ref",
                    "authorname"};
                
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
                
                String refBlock = replace[replace.length - 1];
                parts[2] = refBlock;
                
                if (replace.length > 1) {
                    if (paperAuthors.containsKey(result.getInt("id"))) {
                        parts[3] = String.join(";", paperAuthors.get(result.getInt("id")));
                    }
                    map.put(result.getInt("id"), parts);
                }
            }

            conn.close();
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        
        return map;
    }
    
    public static Map<Integer, String[]> getAuthorNamesSplit(String path) {
        Map<Integer, String> authors = getAuthors(path);
        Map<Integer, String[]> names = new HashMap<>();
        
        authors.entrySet().forEach(entry 
                -> names.put(entry.getKey(), entry.getValue().split(" ")));
        
        return names;
    }
    
    public static Map<Integer, String> extractPaperTitles(
            Map<Integer, String[]> referenceBlocks) {
        Map<Integer, String> titles = new HashMap<>();
        
        referenceBlocks.entrySet().forEach(entry -> 
                titles.put(entry.getKey(), entry.getValue()[1]));
        
        return titles;
    }
    
}
