@extends('default')

@section('head')
    <script
            src="https://code.jquery.com/jquery-3.2.1.min.js"
            integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
            crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
@endsection

@section('page-template')

    <!-- This is a hidden form used for easy laravel submission -->

    {{ Form::model($query, ['method' => 'get', 'id' => 'TopicForm', 'class'=>'Hidden'])}}
        {{Form::number('topic_id', '', ['class' => 'js-topicFormTopic'])}}
        {{Form::number('paper_id', '', ['class' => 'js-topicFormPaperId'])}}
        {{Form::number('author_id', '', ['class' => 'js-topicFormAuthorId'])}}
    {{Form::close()}}

    <div class="row" id="TopicsContainer">
        <div class="col-xs-6">
            <h1 class="TopicsContainerTitle">Available Topics</h1>
            <a class="VisButton btn btn-success" href="{{route('topic visualisation')}}">Visualise these topics</a>
            @if($author_name != '')
                <p>
                    Based on found topics for <em>{{$author_name}}</em>.
                </p>
                <p><span class="PaperTitle js-showAllTopics">Click here</span> to see all available topics.</p>
            @endif
            <ul class="AvailableTopicsList list-group">
                @foreach($all_topics as $topic)
                    <li class="TopicName js-topicName list-group-item {{ $query_info['topic_id'] == $topic->id && $query_info['topic_id'] != '' ? 'active' : '' }}" data-topic-id="{{$topic->id}}">{{$topic->name}}</li>
                @endforeach
            </ul>
        </div>
        <div class="col-xs-6">
            @if($topic_info != null)
                <div class="panel panel-default">
                    <h1 class="panel-heading">{{$topic_info->name}}</h1>
                    <div class="panel-body">
                        <h2>Top related papers</h2>
                        @foreach($topic_info->papers as $paper)
                            <div class="PaperTitle js-paperTitle {{$loop->iteration <=10 ? '' : 'Hidden'}}" data-paper-id="{{$paper->id}}">{{$paper->title}}</div>
                        @endforeach
                        <div class="ButtonContainer">
                            <button class="btn btn-default js-prevPaperButton" disabled data-next-start="-10">< Previous 10</button>
                            <button class="btn btn-default js-nextPaperButton" data-next-start="10">Next 10 ></button>
                        </div>
                        <h2>Top related authors</h2>
                        <span><em>Click on authors to see related topics</em></span>
                        @foreach($topic_info->authors as $author)
                            <div class="PaperTitle js-authorTitle {{$loop->iteration <=10 ? '' : 'Hidden'}}" data-author-id="{{$author->id}}">{{$author->name}}</div>
                        @endforeach
                        <div class="ButtonContainer">
                            <button class="btn btn-default js-prevAuthorButton" disabled data-next-start="-10">< Previous 10</button>
                            <button class="btn btn-default js-nextAuthorButton" data-next-start="10">Next 10 ></button>
                        </div>
                    </div>
                </div>
            @endif
        </div>
    </div>

    @if($paper_info)
    <section class="modal fade" id="PaperModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title" id="myModalLabel">Paper Information</h4>
                </div>
                <div class="modal-body">
                    <h2 class="ModalPaperTitle">{{$paper_info->title}}</h2>
                    <div><span class="lnr lnr-calendar-full"></span> {{$paper_info->year}}</div>
                    <div>
                        <span class="lnr lnr-user"></span>
                        @foreach($paper_info->authors as $author)
                            <span class="QuickFact">
                                {{$author->title}}{{$loop->iteration < count($paper_info->authors) ? ', ' : ' '}}
                            </span>
                        @endforeach
                    </div>
                    <div><span class="lnr lnr-earth"></span> {{$paper_info->event_type ? $paper_info->event_type : 'Not Available'}}</div>
                    <div><span class="lnr lnr-file-empty"></span> {{$paper_info->pdf_name ? $paper_info->pdf_name : 'Not Available'}}</div>
                    <div class="PaperAbstract"><strong>Abstract:</strong> {{$paper_info->abstract ? $paper_info->abstract : 'Not Available'}}</div>
                    <div><strong>Explore topics related to this paper:</strong>
                        @foreach($paper_topics as $topic)
                            <span class="QuickFact">
                                <span class="PaperTitle js-modalTopicNames" data-topic-id="{{$topic->id}}">{{$topic->name}}</span>{{$loop->iteration < count($paper_topics) ? ', ' : ' '}}
                            </span>
                        @endforeach
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </section>
    @endif
@endsection

@section('page-footer')
    <script src="{{asset('js/topics.js')}}" type="application/javascript"></script>
@endsection