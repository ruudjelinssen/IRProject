<?php


namespace App\Http\Controllers;

use App\Query;
use GuzzleHttp\Client;
use Illuminate\Http\Request;

class APIController extends Controller{

    private $_client;

    /**
     * APIController constructor.
     */

    public function __construct(){

        $this->_client = new Client();
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

	/**
	 * Retrieve cluster data
	 *
	 * @param Request $request
	 * @return \Illuminate\Contracts\View\Factory|\Illuminate\View\View
	 */

	public function showClusters(Request $request){

		$request->query('query');

		$query = [
			"statements" => [
				[
					"statement" => "MATCH (a0:Author)-[r0:Wrote]-(p0:Paper {p_id: 6257})<-[:ReferencedIn*0..3]-(p1:Paper)-[w1:Wrote]-(a1:Author) RETURN p0,r0,p1,a0,w1,a1",
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

		return view('pages.clustering', [
			'json' => $res->getBody()
		]);
	}
}