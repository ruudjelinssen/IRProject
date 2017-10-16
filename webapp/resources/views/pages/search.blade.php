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
                        <div class="QuickFacts">
                            @if($result->year)
                                <div class="QuickFact"><span class="lnr lnr-calendar-full"></span>{{$result->year}}</div>
                            @endif
                            @if($result->event_type)
                                <div class="QuickFact"><span class="lnr lnr-earth"></span>{{$result->event_type}}</div>
                            @endif
                            <div class="QuickFact"><span class="lnr lnr-file-empty"></span> {{$result->pdf_name}}</div>
                        </div>

                        <span class="lnr lnr-user"></span>
                        <ul class="AuthorList">
                            @foreach($result->authors as $author)
                                <li class="QuickFact"> {{$author}}</li>
                            @endforeach
                        </ul>
                        <div>{{$result->abstract}}</div>
                    </section>
                </div>
        @endforeach
        </div>
    </div>

@endsection