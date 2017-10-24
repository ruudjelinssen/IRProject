@extends('default')

@section('head')
    <script src="https://d3js.org/d3.v3.min.js"></script>
@endsection

@section('page-template')

    <div id="GraphData" class="Hidden">{{$json}}</div>

    <div class="row">
        <div class="col-xs-12">
            <section class="ResultCard">
                <h1 class="ResultTitle">{{$paper_info->title}}</h1>
                <div class="QuickFacts">
                    @if($paper_info->year)
                        <div class="QuickFact"><span class="lnr lnr-calendar-full"></span>{{$paper_info->year}}</div>
                    @endif
                    @if($paper_info->event_type)
                        <div class="QuickFact"><span class="lnr lnr-earth"></span>{{$paper_info->event_type}}</div>
                    @endif
                    <div class="QuickFact"><span class="lnr lnr-file-empty"></span> {{$paper_info->pdf_name}}</div>
                </div>

                <span class="lnr lnr-user"></span>
                <ul class="AuthorList">
                    @foreach($paper_info->authors as $author)
                        <li class="QuickFact">
                            <a href="{{route('view author', $author->id)}}?query_type=author_by&max_ref_count=2&entity_id={{$author->id}}">{{$author->title}}</a>
                        </li>
                    @endforeach
                </ul>
                <div>{{$paper_info->abstract}}</div>
                <div>
                    <strong>Related Topics:</strong>
                    <ul class="AuthorList">
                        @foreach($topics as $topic)
                            <li class="QuickFact">
                                <a href="{{route('explore by topic', $topic->id)}}">{{$topic->name}}</a>
                            </li>
                        @endforeach
                    </ul>
                </div>
            </section>
        </div>
    </div>
    <div class="row">
        <div class="col-xs-9">
            {{ Form::model($query, ['method' => 'get', 'id' => 'ClusteringForm', 'class' => 'form-inline'])}}

            <div class="form-group">
                {{Form::select('query_type', [
                    'paper_by' => 'Influence of authors & papers on this paper',
                    'paper_on' => 'Influence of this paper on other papers and authors',
                    'cluster_paper' => 'Clustering given this paper',
                  ], null, ['class' => 'form-control'])}}
                <label for="ReferencedIn">With up to: </label>
                {{Form::number('max_ref_count', 2, ['class' => 'form-control'])}}
                {{Form::number('entity_id', $paper_info->id, ['class' => 'Hidden'])}}
                <span>References</span>
                {{Form::submit('Search', ['class' => 'btn btn-default SearchSubmit'])}}
            </div>

            {{Form::close()}}
            <div id="Graph"></div>
        </div>
        <section id="ResultsPanel" class="col-xs-3">
            <div class="panel panel-default">
                <h1 class="panel-heading">Found Related Authors</h1>
                <div class="panel-body">
                    <ul>
                        @foreach($authors as $author)
                            <li><a href="{{route('view author', $author['id'])}}?query_type=author_by&max_ref_count=2&entity_id={{$author['id']}}">{{$author['title']}}</a></li>
                        @endforeach
                    </ul>
                </div>
            </div>
        </section>
    </div>
@endsection

@section('page-footer')
    <script src="{{asset('js/clustering.js')}}" type="application/javascript"></script>
@endsection