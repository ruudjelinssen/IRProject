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

        $request->query('query');

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

		return view('pages.clustering', [
			'dummy' => 'hello'
		]);
	}
}