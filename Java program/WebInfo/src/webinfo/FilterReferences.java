package webinfo;

import info.debatty.java.stringsimilarity.Levenshtein;
import java.util.AbstractMap;
import java.util.AbstractMap.SimpleEntry;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
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
        int i = 0;
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
            i++;
            if(i > 10){
                break;
            }
        }
        checkResults(results, references, authors.entrySet().iterator().next());
        return results;
    }
    
    public void checkResults(List<Map.Entry<Integer, Integer>> relations, Map<Integer, String[]> references, Map.Entry<Integer, String> author) {
        System.out.println(author.getValue() + " occurs in the following references: ");
        for (Entry<Integer, Integer> rel : relations) {
            if (Objects.equals(rel.getKey(), author.getKey())) {
                System.out.println(references.get(rel.getValue())[2]);
            }
        }
    }
    
    /**
     * Use paper->author relation to figure out the references to other papers from a paper
     * @return 
     */
    public List<Map.Entry<Integer, Integer>> paperToPaper(Map<Integer, String[]> references, Map<Integer, String> authors){
        //From paper->author relation, check all papers that author made, and try to find its title in reference block
        return null;
    }
    
    /**
     * Normalize reference block to set of words, remove all punctuation
     */
    public static Map<Integer, String[]> normalizeReferences(Map<Integer, String[]> references){
        Map<Integer, String[]> results = new HashMap();
        for(Entry<Integer, String[]> rel : references.entrySet()){
            results.put(rel.getKey(), removeInterpunction(rel.getValue()[2]).toLowerCase().split(" "));
        }
        return results;
    }

    /**
     * Normalize titles to set of words, remove all punctuation
     */
    public static Map<Integer, String[]> normalizeTitles(Map<Integer, String[]> references){
        Map<Integer, String[]> results = new HashMap();
        for(Entry<Integer, String[]> rel : references.entrySet()){
            results.put(rel.getKey(), removeInterpunction(rel.getValue()[1]).toLowerCase().split(" "));
        }
        return results;
    }
    
    public static Map<Integer, List<Integer>> potentialMatches(Map<Integer, String[]> titles, Map<Integer, String[]> refBlocks){
        Map<Integer, List<Integer>> results = new HashMap();
        for(Entry<Integer, String[]> titleEntry : titles.entrySet()){
            for(Entry<Integer, String[]> refBlockEntry : refBlocks.entrySet()){
                if(isMatch(titleEntry, refBlockEntry)){
                    if(!results.containsKey(titleEntry.getKey())){
                        results.put(titleEntry.getKey(), new ArrayList());
                    }
                    results.get(titleEntry.getKey()).add(refBlockEntry.getKey());
                }
            }
        }
        return results;
    }
    
    public static boolean isMatch(Entry<Integer, String[]> title, Entry<Integer, String[]> refBlock){
        if(title.getKey() == refBlock.getKey()){
            return false;
        }
        if(title.getValue().length > 2){
            int counter = 0;
            for(String word : title.getValue()){
                if(word.length() < 4){
                    continue;
                }
                for(String word2 : refBlock.getValue()){
                    if(word.equals(word2)){
                        counter++;
                    }
                }
            }
            return title.getValue().length - counter < 3;
        }
        //In case of 1 word
        if(title.getValue().length == 1){
            Levenshtein l = new Levenshtein();
            for(String word : refBlock.getValue()){
                if(l.distance(title.getValue()[0], word) < 3){
                    return true;
                }
            }
        }
        if(title.getValue().length == 2){
            String word1;
            String word2;
            Levenshtein l = new Levenshtein();
            for(int i = 0; i < refBlock.getValue().length -1; i++){
                word1 = refBlock.getValue()[i];
                word2 = refBlock.getValue()[i+1];
                if(l.distance(title.getValue()[0], word1) < 3 && l.distance(title.getValue()[1], word2) < 3){
                    return true;
                }
            }
        }
        return false;
    }
    
    private static String removeInterpunction(String refBlock) {
        return refBlock.replaceAll("\\.|;|:|,|!|\t|\n|\"","");
    }
    
    /**
     * Titel: 1,2 woord(en) -> Altijd lievenstein
     * Titel > 2 woorden -> Maximaal 2 woorden met 2 typos per woord (Er is dus altijd minstens 1 exacte match)
     * -> Extacte match moet een woord zijn met tenminste 4 tekens
     */
    
    public static void main(String[] args) {
        System.out.println(removeInterpunction("Hello J.Absfasdf \" ;;;::: ,.,.,.,."
                + "\t sdfasf,.!"));
        Map<Integer, String[]> references = WebInfo.getReferenceBlocks("C:\\Users\\Arjan\\Documents\\IRProject\\Dataset\\");
        Map<Integer, List<Integer>> matches = potentialMatches(normalizeTitles(references), normalizeReferences(references));
        System.out.println(references.get(1)[1]);
        List<String> matchList = new ArrayList();
        for(Integer id : matches.get(1)){
            matchList.add(references.get(id)[2]);
        }
        return;
    }
    
}
