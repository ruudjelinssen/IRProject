@extends('default')

@section('head')
    <script src="https://d3js.org/d3.v3.min.js"></script>
@endsection

@section('page-template')

    <div id="GraphData" class="Hidden">{{$json}}</div>

    <div class="row">
        <div class="col-xs-12">
            <section class="ResultCard ResultCardEntity">
                <h1 class="ResultTitle">{{$author_info->title}}</h1>
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
                    'author_by' => 'Influence of authors & papers on this author',
                    'author_on' => 'Influence of this author on other papers and authors',
                    'cluster_author' => 'Clustering given this author',
                  ], null, ['class' => 'form-control'])}}
                <label for="ReferencedIn">With up to: </label>
                {{Form::number('max_ref_count', 2, ['class' => 'form-control'])}}
                {{Form::number('entity_id', $author_info->id, ['class' => 'Hidden'])}}
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
                        @foreach($titles as $title)
                            <li><a href="/search?author={{$title}}">{{$title}}</a></li>
                        @endforeach
                    </ul>
                </div>
            </div>
        </section>
        <div class="col-xs-12">
            <iframe class="TopicAuthorEvolutionVisualisation" src="http://127.0.0.1:5003/visualization/authortopicevolution/{{$author_info->id}}"></iframe>
        </div>
    </div>
@endsection

@section('page-footer')
    <script src="{{asset('js/clustering.js')}}" type="application/javascript"></script>
@endsection