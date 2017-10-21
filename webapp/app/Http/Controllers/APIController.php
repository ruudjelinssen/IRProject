<?php


namespace App\Http\Controllers;

use App\Query;
use GuzzleHttp\Client;
use Illuminate\Http\Request;

class APIController extends Controller{

    private $_client;
    private $_query_types;

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
    }

    /**
     * Retrieve search data for the given query parameters
     *
     * @param Request $request
     * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
     */

    public function showSearch(Request $request){

        $search_uri = 'http://127.0.0.1:5002/papers?';

        foreach($request->query() as $key => $value){

            $search_uri = $search_uri . $key . '=' . $value . '&';
        }

        $res = $this->_client->request('GET', $search_uri);
	    $res_decoded = \GuzzleHttp\json_decode($res->getBody());

        $query_model = new Query;

        return view('pages.search', [
        	'meta' => $res_decoded->meta,
            'results' => $res_decoded->results,
            'query' => $query_model
        ]);
    }

    private function _getPaper($id){

	    $search_uri = 'http://127.0.0.1:5002/papers?id=' . $id;

	    $res = $this->_client->request('GET', $search_uri);
	    $res_decoded = \GuzzleHttp\json_decode($res->getBody());

	    return $res_decoded->results[0];
    }

	private function _getAuthor($id){

		$search_uri = 'http://127.0.0.1:5002/authors?id=' . $id;

		$res = $this->_client->request('GET', $search_uri);
		$res_decoded = \GuzzleHttp\json_decode($res->getBody());

		return $res_decoded->result;
	}

	/**
	 * Retrieve cluster data
	 *
	 * @param Request $request
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showClusters(Request $request){

		$query_type = $request->query('query_type');
		$entity_id = $request->query('entity_id');
		$max_ref_count = $request->query('max_ref_count');

		$query_model = new Query;

		if(!$query_type){

			return view('pages.clustering', [
				'json' => 'Oops',
				'query' => $query_model
			]);
		}

		if($query_type % 2 == 0){

			$entity_type = 'paper';
			$root = $this->_getPaper($entity_id);
		}
		else{

			$entity_type = 'author';
			$root = $this->_getAuthor($entity_id);
		}

		$statement = $this->_query_types[$query_type];
		$statement = str_replace('%%%', $entity_id, $statement);
		$statement = str_replace('&&&&', $max_ref_count, $statement);

		$query = [
			"statements" => [
				[
					"statement" => $statement,
					"resultDataContents" => ["graph"]
				]
			]
		];

		$headers = [
			'Accept' => 'application/json',
		];

		$uri = 'http://localhost:7474/db/data/transaction/commit';

		$client = new Client();

		$res = $client->post($uri, [
			'headers' => $headers,
			'json' => $query
		]);

		// Get the entity titles from the result

		$results = \GuzzleHttp\json_decode($res->getBody())->results;
		$titles = [];

		foreach($results[0]->data as $result){
			foreach($result->graph->nodes as $node){

				if($node->labels[0] == 'Author' && !in_array($node->properties->name, $titles)){

					array_push($titles, $node->properties->name);
				}
			}
		}

		return view('pages.clustering', [
			'json' => $res->getBody(),
			'titles' => $titles,
			'root' => $root,
			'entity_type' => $entity_type,
			'query' => $query_model
		]);
	}
}