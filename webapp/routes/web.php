<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::any('/search', [
    'as' => 'search',
    'uses' => 'APIController@showSearch',
]);

Route::any('/clustering', [
	'as' => 'clustering',
	'uses' => 'APIController@showClusters',
]);

Route::any('/evolution', [
	'as' => 'evolution',
	'uses' => 'APIController@showEvolution',
]);

Route::any('/topics', [
	'as' => 'topics',
	'uses' => 'APIController@showTopics',
]);