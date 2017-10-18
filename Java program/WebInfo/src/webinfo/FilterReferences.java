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
            //if(titleEntry.getKey() != 2) continue;
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
            int shortWords = 0;
            for(String word : title.getValue()){
                if(word.length() < 4){
                    shortWords++;
                    continue;
                }
                for(String word2 : refBlock.getValue()){
                    if(word.equals(word2)){
                        counter++;
                        break;
                    }
                }
            }
            if(counter < 2) return false;
            return (title.getValue().length - shortWords) - counter < 3;
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
        refBlock = refBlock.replaceAll("\\(|\\)", " ");
        refBlock = refBlock.replaceAll("\\.|;|:|,|!|\t|\n|\"","");
        return refBlock.replaceAll("\\s\\s", " ");
    }
    
    public static Map<Integer, List<Integer>> reduceMatches(Map<Integer, String[]> references){
        Map<Integer, String[]> normalizedTitles = normalizeTitles(references);
        Map<Integer, String[]> normalizedReferences = normalizeReferences(references);       
        Map<Integer, List<Integer>> matches = potentialMatches(normalizedTitles, normalizedReferences);
        
        Map<Integer, List<Integer>> goodMatches = new HashMap<>();
        
        for(Entry<Integer, List<Integer>> matchList : matches.entrySet()){
            for(Integer paperId : matchList.getValue()){
                if(isGoodMatch(normalizedTitles.get(matchList.getKey()), normalizedReferences.get(paperId))) { //Is this really matchList.getKey() twice???
                    if (!goodMatches.containsKey(matchList.getKey())) {
                        goodMatches.put(matchList.getKey(), new ArrayList<>());
                    }
                    
                    goodMatches.get(matchList.getKey()).add(paperId);
                }
            }
        }
        
        return goodMatches;
        //
    }
        
    private static boolean isGoodMatch(String[] title, String[] referenceBlock){
        if (title.length > 2) {
            for (int i = 0; i < title.length; i++) {
                int k;
                if (title[i].length() > 3) {
                    for (int j = 0; j < referenceBlock.length; j++) {
                        if (title[i].equals(referenceBlock[j])) {
                            k = 1;
                            while (i + k < title.length && j + k < referenceBlock.length) {
                                if (title[i + k].length() > 3 && title[i + k].equals(referenceBlock[j + k])) {
                                    return true;
                                }
                                k++;
                            }
                        }
                    }
                }
            }
        }
        return false;
    }
    
    public static Map<Integer, List<Integer>> exactMatches(Map<Integer, String[]> references){
        Map<Integer, String[]> normalizedTitles = normalizeTitles(references);
        Map<Integer, String[]> normalizedReferences = normalizeReferences(references);       
        Map<Integer, List<Integer>> matches = reduceMatches(references);
        
        Map<Integer, List<Integer>> exactMatches = new HashMap<>();
        
        for(Entry<Integer, List<Integer>> matchList : matches.entrySet()){
            for(Integer paperId : matchList.getValue()){
                if(isExactMatch(normalizedTitles.get(matchList.getKey()), normalizedReferences.get(paperId))) {
                    if (!exactMatches.containsKey(matchList.getKey())) {
                        exactMatches.put(matchList.getKey(), new ArrayList<>());
                    }
                    
                    exactMatches.get(matchList.getKey()).add(paperId);
                }
            }
        }
        
        return exactMatches;
        //
    }
        
    private static boolean isExactMatch(String[] title, String[] referenceBlock){
        if (title.length > 2) {
            for (int i = 0; i < title.length; i++) {
                int k;
                if (title[i].length() > 3) {
                    for (int j = 0; j < referenceBlock.length; j++) {
                        if (title[i].equals(referenceBlock[j])) {
                            k = 1;
                            while (i + k < title.length && j + k < referenceBlock.length) {
                                if (title[i + k].length() > 3 && title[i + k].equals(referenceBlock[j + k])) {
                                    return indexMatch(i, j, k, title, referenceBlock);
                                }
                                k++;
                            }
                        }
                    }
                }
            }
        }
        return false;
    }

    
    /**
     * 
     * @param i index of a match in title
     * @param j index of a match in ref
     * @param k offset between 2 matches
     * @param title
     * @param referenceBlock
     * @return 
     */
    private static boolean indexMatch(int i, int j, int k, String[] title, String[] referenceBlock){
        //For each word in title with > 3 (not i, i+k)
        //j < i return false (ioob)
        if(j < i){
            return false;
        }
        //refBlock.length - j < title.length - i -> no solution (ioob)
        if(referenceBlock.length - j < title.length - i){
            return false;
        }
        int offset;
        Levenshtein l = new Levenshtein();
        int count = 0;
        for(int u = 0; u < title.length; u++){
            if(u == i || u == i+k) continue;
            offset = u-i;
            if(l.distance(title[i+offset], referenceBlock[j+offset]) < 2){
                count++;
            }
        }
        if( title.length - 2 - count == 0){
            return true;
        }
        return false;
    }
    
    /**
     * Given an exact paper-paper match, check if author also appears
     * @param references
     * @return 
     */
    public static Map<Integer, List<Integer>> authorAndPaperMatch(Map<Integer, String[]> references){
        Map<Integer, List<Integer>> matches = exactMatches(references);
        Map<Integer, String[]> normalizedReferences = normalizeReferences(references);
        Map<Integer, List<Integer>> results = new HashMap();
        for(Entry<Integer, List<Integer>> match : matches.entrySet()){
            for(int paperId : match.getValue()){
                if(isAuthorExtactMatch(references.get(match.getKey())[3], normalizedReferences.get(paperId))){
                    if (!results.containsKey(match.getKey())) {
                        results.put(match.getKey(), new ArrayList<>());
                    }
                    
                    results.get(match.getKey()).add(paperId);
                }
            }
        }

        
        return results;
    }
    
    private static boolean isAuthorExtactMatch(String authors, String[] referenceBlock) {
        Levenshtein l = new Levenshtein();
        //Split authors
        String[] author = authors.split(";");
        for(String a : author){
            String[] name = a.split(" ");
            String lastname = name[name.length-1].toLowerCase();
            //Find lastname in reference block
            int maxDist = (int)Math.min(2, Math.floor(0.25*lastname.length()));
            for(String word : referenceBlock){
                if(l.distance(lastname, word) <= maxDist){
                    return true;
                }
            }
        }
        //Find their last name in referenceblock
        return false;
    }
    
    public static void main(String[] args) {
        System.out.println(removeInterpunction("Hello J.Absfasdf \" ;;;::: ,.,.,.,."
                + "\t sdfa(1994)sf,.!"));
        Map<Integer, String[]> references = WebInfo.getReferenceBlocks("C:\\Users\\Arjan\\Documents\\IRProject\\Dataset\\");
        Map<Integer, List<Integer>> matches = authorAndPaperMatch(references);
        List<String> matchList = new ArrayList();
        checkResult(references, matches);
        return;
    }
    
    public static void checkResult(Map<Integer, String[]> references, Map<Integer, List<Integer>> matches){
        List<String> matchList = new ArrayList();
        System.out.println(references.get(1832)[1]);
        System.out.println(references.get(1832)[3]);
        for(Integer id: matches.get(1832)){
            matchList.add(references.get(id)[2]);
        }
        return;
    }
    
}
