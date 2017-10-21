@extends('default')

@section('head')
    <script src="https://d3js.org/d3.v3.min.js"></script>
@endsection

@section('page-template')

    <div id="GraphData" class="Hidden">{{$json}}</div>

    <div id="NavBar" class="row navbar navbar-default navbar-static-top">

        <div class="col-xs-10 col-xs-offset-1">
            {{ Form::model($query, ['method' => 'get', 'id' => 'ClusteringForm', 'class' => 'form-inline'])}}

                <div class="form-group">
                    {{Form::select('query_type', [
                        'paper_by' => 'Authors Influencing Paper', 'author_by' => 'Authors Influencing Author',
                        'paper_on' => 'Paper influence on', 'author_on' => 'Author influence on',
                        'cluster_paper' => 'Clustering Given Paper', 'cluster_author' => 'Clustering Given Author'
                      ], null, ['class' => 'form-control'])}}
                    {{Form::text('entity_id', '', ['class' => 'form-control', 'placeholder' => 'the ID of the entity'])}}
                    <label for="ReferencedIn">With up to: </label>
                    {{Form::number('max_ref_count', 2, ['class' => 'form-control'])}}
                    <span>References</span>
                    {{Form::submit('Search', ['class' => 'btn btn-default SearchSubmit'])}}
                </div>

            {{Form::close()}}
        </div>
    </div>

    <div id="Graph"></div>

    <section id="RootEntityPanel" class="col-xs-3 col-xs-offset-9">
        <div class="panel panel-default">
            <h1 class="panel-heading">
                @if($entity_type == 'paper')
                    Paper Information
                @endif
                @if($entity_type == 'author')
                    Author Information
                @endif
            </h1>
            <div class="panel-body">
                @if($entity_type == 'paper')
                    {{$root->title}}
                @endif
                @if($entity_type == 'author')
                    {{$root->title}}
                @endif
            </div>
        </div>
    </section>

    <section id="ResultsPanel" class="col-xs-3 col-xs-offset-9">
        <div class="panel panel-default">
            <h1 class="panel-heading">Results</h1>
            <div class="panel-body">
                <ul>
                    @foreach($titles as $title)
                        <li><a href="/search?author={{$title}}">{{$title}}</a></li>
                    @endforeach
                </ul>
            </div>
        </div>
    </section>
@endsection

@section('page-footer')
    <script src="{{asset('js/clustering.js')}}" type="application/javascript"></script>
@endsection