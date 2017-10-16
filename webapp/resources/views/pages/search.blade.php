@extends('default')

@section('head')

@endsection

@section('page-template')

    <div class="container-fluid">

        <div class="row">
            <div class="col-xs-8 col-xs-offset-2 CoverContainer">

                <img class="CoverImage" src="{{asset('images/papers.jpg')}}">
                <div class="CoverOverlay"></div>

                {{ Form::model($query, ['method' => 'get', 'id' => 'SearchForm'])}}

                    {{Form::text('query', '', ['id' => 'SearchInput', 'placeholder' => 'Search for papers, authors, years, and more..'])}}
                    {{Form::submit('Search', ['class' => 'btn btn-default SearchSubmit'])}}

                {{Form::close()}}
            </div>
        </div>

        <div class="row">
        @foreach($results as $result)

                <div class="col-xs-6 col-xs-offset-3">
                    <section class="ResultCard">
                        <h1 class="ResultTitle">{{$result->title}}</h1>
                        <div>{{$result->abstract}}</div>
                        <div>{{$result->year}}</div>
                        <div>{{$result->event_type}}</div>
                        <div>{{$result->pdf_name}}</div>
                        <span>Authors:</span>
                        <ul>
                            @foreach($result->authors as $author)
                                <li>{{$author}}</li>
                            @endforeach
                        </ul>
                    </section>
                </div>
        @endforeach
        </div>
    </div>

@endsection