<?php


namespace App\Http\Controllers;

use App\Query;
use GuzzleHttp\Client;
use Illuminate\Http\Request;

class APIController extends Controller{

    private $_client;
    private $_query_types;
    private $_search_uri;
    private $_author_search_uri;
    private $_all_topics_uri;
    private $_single_topic_uri;
    private $_topics_of_paper_uri;
    private $_topics_of_author_uri;
    private $_topics_search_uri;

    /**
     * APIController constructor.
     */

    public function __construct(){

        $this->_client = new Client();
        $this->_query_types = [
        	'paper_by' => "MATCH (a0:Author)-[r0:Wrote]-(p0:Paper {p_id: %%%})<-[r1:ReferencedIn*0..&&&&]-(p1:Paper)-[w1:Wrote]-(a1:Author) RETURN p0,r0,r1,p1,a0,w1,a1",
        	'author_by' => "MATCH (a0:Author {a_id: %%%})-[w0:Wrote]-(p0:Paper)<-[r1:ReferencedIn*0..&&&&]-(p1:Paper)-[w1:Wrote]-(a1:Author) RETURN p0,r1,w0,w1,p1,a0,a1",
        	'paper_on' => "MATCH (a0:Author)-[r0:Wrote]-(p0:Paper {p_id: %%%})-[r2:ReferencedIn*0..&&&&]->(p1:Paper)-[r1:Wrote]-(a1:Author) RETURN r0,r1,r2,p0,p1,a0,a1",
        	'author_on' => "MATCH (a0:Author {a_id: %%%})-[r0:Wrote]-(p0:Paper)-[r2:ReferencedIn*0..&&&&]->(p1:Paper)-[r1:Wrote]-(a1:Author) RETURN r0,r1,r2,p0,p1,a0,a1",
        	'cluster_paper' => "MATCH (a1:Author)-[w1:Wrote]-(p1:Paper)-[r1:ReferencedIn*0..&&&&]-(p0:Paper {p_id: %%%})-[w0:Wrote]-(a0:Author) RETURN r1,w1,w0,a0,a1,p0,p1",
        	'cluster_author' => "MATCH (a1:Author)-[r1:Wrote]-(p1:Paper)-[r2:ReferencedIn*0..&&&&]-(p0:Paper)-[r0:Wrote]-(a0:Author {a_id: %%%}) RETURN r1,r2,r0,a0,a1,p0,p1",
        ];
        $this->_search_uri = 'http://127.0.0.1:5002/papers';
        $this->_author_search_uri = 'http://127.0.0.1:5002/authors';
        $this->_all_topics_uri = 'http://127.0.0.1:5003/topics/';
        $this->_single_topic_uri = 'http://127.0.0.1:5003/topic/';
        $this->_topics_of_paper_uri = 'http://127.0.0.1:5003/paper/';
        $this->_topics_of_author_uri = 'http://127.0.0.1:5003/author/';
        $this->_topics_search_uri = 'http://127.0.0.1:5003/topics/search/';
    }

	/**
	 * Retrieve evolution data
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showHome(){

		$res = $this->_client->request('GET', $this->_all_topics_uri);
		$all_topics = (\GuzzleHttp\json_decode($res->getBody()))->topics;
		$query_model = new Query;

		return view('pages.home', [
			'query' => $query_model,
			'all_topics' => $all_topics
		]);
	}

    /**
     * Retrieve search data for the given query parameters
     *
     * @param Request $request
     * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
     */

    public function showSearch(Request $request){

        $search_uri = $this->_search_uri . '?';

        foreach($request->query() as $key => $value){

            $search_uri = $search_uri . $key . '=' . $value . '&';
        }

        $res = $this->_client->request('GET', $search_uri);
	    $res_decoded = \GuzzleHttp\json_decode($res->getBody());

	    // Get the related topics to this query

	    $related_topics = [];

	    if($request->query('query')){

		    $res = $this->_client->request('GET', $this->_topics_search_uri . '?query=' . $request->query('query'));
		    $related_topics = (\GuzzleHttp\json_decode($res->getBody()))->topics;
	    }

        $query_model = new Query;

        return view('pages.search', [
        	'meta' => $res_decoded->meta,
            'results' => $res_decoded->results,
            'related_topics' => $related_topics,
            'query' => $query_model
        ]);
    }

	/**
	 * Retrieve data for 1 particular topic
	 *
	 * @param integer $topicID
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showTopics($topicID){

		// Get the information for the topic with the specified ID

		$res = $this->_client->request('GET', $this->_single_topic_uri . $topicID);
		$topic_info = \GuzzleHttp\json_decode($res->getBody());

		$query_model = new Query;

		return view('pages.topics', [
			'query' => $query_model,
			'topic_info' => $topic_info,
			'topic_id' => $topicID
		]);
	}

	/**
	 * Show LDA view
	 *
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showLDA(){

		return view('pages.topicviz');
	}

	/**
	 * Retrieve evolution data
	 *
	 * @param Request $request
	 * @param integer $paperID
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showPaper(Request $request, $paperID = 6117){

		$query_type = $request->query('query_type');
		$max_ref_count = $request->query('max_ref_count');

		$res = $this->_client->request('GET', $this->_search_uri . '?id=' . $paperID);
		$paper = ((\GuzzleHttp\json_decode($res->getBody()))->results)[0];

		$query_model = new Query;

		$statement = $this->_query_types[$query_type];
		$statement = str_replace('%%%', $paperID, $statement);
		$statement = str_replace('&&&&', $max_ref_count, $statement);

		$query = [
			"statements" => [
				[
					"statement" => $statement,
					"resultDataContents" => ["graph"]
				]
			]
		];

		$uri = 'http://localhost:7474/db/data/transaction/commit';

		$client = new Client();

		$res = $client->post($uri, [
			'json' => $query
		]);

		// Get the entity titles from the result

		$results = \GuzzleHttp\json_decode($res->getBody())->results;
		$titles = [];
		$authors = [];

		foreach($results[0]->data as $result){
			foreach($result->graph->nodes as $node){

				if($node->labels[0] == 'Author' && !in_array($node->properties->name, $titles)){

					array_push($titles, $node->properties->name);
					array_push($authors, ['title' => $node->properties->name, 'id' => $node->properties->a_id]);
				}
			}
		}

		// Get the topics related to this paper

		$topics_res = $this->_client->request('GET', $this->_topics_of_paper_uri . $paperID);
		$topics = (\GuzzleHttp\json_decode($topics_res->getBody()))->topics;

		return view('pages.paper', [
			'query' => $query_model,
			'paper_info' => $paper,
			'json' => $res->getBody(),
			'authors' => $authors,
			'topics' => $topics
		]);
	}

	/**
	 * Retrieve evolution data
	 *
	 * @param Request $request
	 * @param integer $authorID
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showAuthor(Request $request, $authorID = 6117){

		$query_type = $request->query('query_type');
		$max_ref_count = $request->query('max_ref_count');

		$res = $this->_client->request('GET', $this->_author_search_uri . '?id='. $authorID);
		$author = ((\GuzzleHttp\json_decode($res->getBody()))->results)[0];

		$query_model = new Query;

		$statement = $this->_query_types[$query_type];
		$statement = str_replace('%%%', $authorID, $statement);
		$statement = str_replace('&&&&', $max_ref_count, $statement);

		$query = [
			"statements" => [
				[
					"statement" => $statement,
					"resultDataContents" => ["graph"]
				]
			]
		];

		$uri = 'http://localhost:7474/db/data/transaction/commit';

		$client = new Client();

		$res = $client->post($uri, [
			'json' => $query
		]);

		// Get the entity titles from the result

		$results = \GuzzleHttp\json_decode($res->getBody())->results;
		$titles = [];
		$authors = [];

		foreach($results[0]->data as $result){
			foreach($result->graph->nodes as $node){

				if($node->labels[0] == 'Author' && !in_array($node->properties->name, $titles)){

					array_push($titles, $node->properties->name);
					array_push($authors, ['title' => $node->properties->name, 'id' => $node->properties->a_id]);
				}
			}
		}

		// Get the topics related to this author

		$topics_res = $this->_client->request('GET', $this->_topics_of_author_uri . $authorID);
		$topics = (\GuzzleHttp\json_decode($topics_res->getBody()))->topics;

		return view('pages.author', [
			'query' => $query_model,
			'author_info' => $author,
			'json' => $res->getBody(),
			'authors' => $authors,
			'topics' => $topics
		]);
	}
}