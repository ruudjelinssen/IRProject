@extends('default')

@section('head')

@endsection

@section('page-template')

    <div class="row">
        <div class="col-xs-12 CoverContainer">
            <div class="CoverInnerContainer">
                <img class="CoverImage" src="{{asset('images/papers.jpg')}}">
                <div class="CoverOverlay"></div>

                {{ Form::model($query, ['method' => 'get', 'id' => 'SearchForm', 'class' => 'form-inline text-center'])}}
                <div class="form-group">

                    {{Form::text('query', '', ['id' => 'SearchInput', 'class' => 'form-control', 'placeholder' => 'Search for papers, authors, years, and more..'])}}
                    {{Form::submit('Search', ['class' => 'btn btn-default SearchSubmit'])}}
                </div>

                {{Form::close()}}
            </div>
        </div>
    </div>

    <div class="row">

        <div class="col-xs-12 TopInfoPanel">
            <span class="TotalResults">Showing top 10 results out of {{$meta->total}} </span>

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

        <div class="col-xs-8">
            <div class="row">
                @foreach($results as $result)
                    <div class="col-xs-12">
                        <section class="ResultCard">
                            <h1 class="ResultTitle">
                                <a href="{{route('view paper', $result->id)}}?query_type=paper_by&max_ref_count=2&entity_id={{$result->id}}">{{$result->title}}</a>
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
                                        <a href="{{route('view author', $author->id)}}?query_type=author_by&max_ref_count=2&entity_id={{$author->id}}">{{$author->title}}</a>
                                    </li>
                                @endforeach
                            </ul>
                            <div class="HighlightedSnippets">{!! $result->highlight !!}</div>
                            <div>{{$result->abstract}}</div>
                        </section>
                    </div>
                @endforeach
            </div>
        </div>

        <div class="col-xs-4">
            <div class="panel panel-default RelatedTopics">
                <div class="panel-heading">
                    <h3 class="panel-title">Related Topics</h3>
                </div>
                <div class="panel-body">
                    @if(count($related_topics) > 0)
                        @foreach($related_topics as $topic)
                            <a href="{{route('explore by topic', $topic->id)}}">{{$topic->name}}</a>
                        @endforeach
                    @else
                        No related topics could be found for this query.
                    @endif
                </div>
            </div>
        </div>
    </div>

@endsection

@section('page-footer')
    <script src="{{asset('js/search.js')}}" type="application/javascript"></script>
@endsection