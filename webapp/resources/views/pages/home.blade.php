@extends('default')
@section('page-template')
    <div class="jumbotron text-center" id="HomeTron">
        <h1 class="display-3">NIPS Papers Retrieval and Analysis</h1>
        <p class="lead">To begin your journey, you can search for papers.</p>

        {{ Form::model($query, ['method' => 'get', 'url' => route('explore by search'), 'id' => 'HomeSearch', 'class' => 'form-inline'])}}
        <div class="form-group">
        {{Form::text('query', '', ['id' => 'SearchInput', 'placeholder' => 'Search for papers, authors, years, and more..', 'class'=> 'form-control'])}}
        {{Form::submit('Search', ['class' => 'btn btn-default SearchSubmit'])}}
        </div>
        {{Form::close()}}
        <hr class="my-4">
        <p class="lead">Or choose a topic to start exploring further.</p>
        <ul class="AllTopicsList list-group">
            @foreach($all_topics as $topic)
                <li class="TopicName js-topicName list-group-item" data-topic-id="{{$topic->id}}">
                    <a href="{{route('explore by topic', $topic->id)}}">{{$topic->name}}</a></li>
            @endforeach
        </ul>
        <hr class="my-4">
        <p class="lead">You can also view an LDA visualisation!</p>
        <a class="VisButton btn btn-success" href="{{route('topic visualisation')}}">To the visualisation</a>
    </div>
@endsection