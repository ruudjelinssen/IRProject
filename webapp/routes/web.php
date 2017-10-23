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

Route::any('/', [
	'as' => 'home',
	'uses' => 'APIController@showHome',
]);

Route::any('/search', [
    'as' => 'explore by search',
    'uses' => 'APIController@showSearch',
]);

Route::any('/topics/{topicID?}', [
	'as' => 'explore by topic',
	'uses' => 'APIController@showTopics',
]);

Route::any('/topic-visualisation', [
	'as' => 'topic visualisation',
	'uses' => 'APIController@showLDA',
]);

Route::any('/paper/{paperID?}', [
	'as' => 'view paper',
	'uses' => 'APIController@showPaper',
]);

Route::any('/author/{authorID?}', [
	'as' => 'view author',
	'uses' => 'APIController@showAuthor',
]);