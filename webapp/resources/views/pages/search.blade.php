@extends('default')

@section('head')

@endsection

@section('page-template')

    <div class="row">
        <div class="col-xs-12 CoverContainer">

            <img class="CoverImage" src="{{asset('images/papers.jpg')}}">
            <div class="CoverOverlay"></div>

            {{ Form::model($query, ['method' => 'get', 'id' => 'SearchForm'])}}

                {{Form::text('query', '', ['id' => 'SearchInput', 'placeholder' => 'Search for papers, authors, years, and more..'])}}
                {{Form::submit('Search', ['class' => 'btn btn-default SearchSubmit'])}}

            {{Form::close()}}
        </div>
    </div>

    <div class="row">

        <div class="col-xs-12 TopInfoPanel">
            <span class="TotalResults">Total results: {{$meta->total}}</span>

            {{ Form::model($query, ['method' => 'get', 'id' => 'OrderingForm', 'class' => 'form-inline'])}}

            <div class="form-group">
                <label>Sort by:</label>
                {{Form::select('order', [
                    'relevance' => 'Relevance', 'alphabetical' => 'Alphabetical', 'year' => 'Year'
                  ], null, ['class' => 'form-control js-orderingSelect'])}}
                {{Form::text('query', '', ['class' => 'Hidden'])}}
            </div>

            {{Form::close()}}
        </div>

        @foreach($results as $result)
        <div class="col-xs-8">
            <section class="ResultCard">
                <h1 class="ResultTitle">
                    <a href="/clustering?query_type=paper_by&entity_id={{$result->id}}&max_ref_count=2">{{$result->title}}</a>
                </h1>
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
                        <li class="QuickFact">
                            <a href="/clustering?query_type=author_by&entity_id={{$author->id}}&max_ref_count=2">{{$author->title}}</a>
                        </li>
                    @endforeach
                </ul>
                <div class="HighlightedSnippets">{!! $result->highlight !!}</div>
                <div>{{$result->abstract}}</div>
            </section>
        </div>
        @endforeach
    </div>

@endsection

@section('page-footer')
    <script src="{{asset('js/search.js')}}" type="application/javascript"></script>
@endsection