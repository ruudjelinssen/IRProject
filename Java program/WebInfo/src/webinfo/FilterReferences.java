package webinfo;

import java.util.AbstractMap;
import java.util.AbstractMap.SimpleEntry;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author Arjan
 */
public class FilterReferences {

    public List<Map.Entry<Integer, Integer>> filter(Map<Integer, String[]> references, Map<Integer, String> authors) {
        //For each author, find occurrences in references of all papers
        List<Map.Entry<Integer, Integer>> results = new ArrayList();
        for (Entry<Integer, String> author : authors.entrySet()) {
            //Change author to lowercase and initials
            String[] authParts = author.getValue().toLowerCase().split(" ");
            authParts[0] = authParts[0].substring(0,1) + ".";
            String auth = String.join(" ", authParts);
            //Escape point from initals and replace question marks with wildcard
            Pattern p = Pattern.compile(auth.replace(".", "\\.").replace("?", "."));
            for (Entry<Integer, String[]> reference : references.entrySet()) {
                Matcher m = p.matcher(reference.getValue()[2]);
                if(m.find()){
                    results.add(new AbstractMap.SimpleEntry<>(author.getKey(), reference.getKey()));
                }
            }
        }
        return results;
    }
}
