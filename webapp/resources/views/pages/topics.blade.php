@extends('default')

@section('page-template')
    <div class="row" id="TopicsContainer">
        <div class="col-xs-12">
            <h1 class="TopicsContainerTitle">{{$topic_info->name}}</h1>
        </div>
        <div class="col-xs-6">
            <h2>Top related papers</h2>
            @foreach($topic_info->papers as $paper)
                <a href="{{route('view paper', $paper->id)}}?query_type=paper_by&max_ref_count=2&entity_id={{$paper->id}}"
                   class="PaperTitle js-paperTitle {{$loop->iteration <=10 ? '' : 'Hidden'}}" data-paper-id="{{$paper->id}}">{{$paper->title}}</a>
            @endforeach
            <div class="ButtonContainer">
                <button class="btn btn-default js-prevPaperButton" disabled data-next-start="-10">< Previous 10</button>
                <button class="btn btn-default js-nextPaperButton" data-next-start="10">Next 10 ></button>
            </div>
        </div>
        <div class="col-xs-6">
            <h2>Top related authors</h2>
            @foreach($topic_info->authors as $author)
                <a href="{{route('view author', $author->id)}}?query_type=author_by&max_ref_count=2&entity_id={{$author->id}}"
                   class="PaperTitle js-authorTitle {{$loop->iteration <=10 ? '' : 'Hidden'}}" data-author-id="{{$author->id}}">{{$author->name}}</a>
            @endforeach
            <div class="ButtonContainer">
                <button class="btn btn-default js-prevAuthorButton" disabled data-next-start="-10">< Previous 10</button>
                <button class="btn btn-default js-nextAuthorButton" data-next-start="10">Next 10 ></button>
            </div>
        </div>
        <div class="col-xs-12">
            <iframe class="EvolutionVisualisation" src="http://127.0.0.1:5003/visualization/topicevolution/{{$topic_id}}"></iframe>
            <iframe class="TopicAuthorEvolutionVisualisation" src="http://127.0.0.1:5003/visualization/topicauthorevolution/{{$topic_id}}"></iframe>
        </div>
    </div>
@endsection

@section('page-footer')
    <script src="{{asset('js/topics.js')}}" type="application/javascript"></script>
@endsection