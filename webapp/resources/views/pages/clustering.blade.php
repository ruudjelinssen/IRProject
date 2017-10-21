@extends('default')

@section('head')
    <script src="https://d3js.org/d3.v3.min.js"></script>
@endsection

@section('page-template')

    <div id="GraphData" class="Hidden">{{$json}}</div>

    <div id="NavBar" class="row navbar navbar-default navbar-static-top">

        <div class="col-xs-6 col-xs-offset-3">
            <form class="form-inline">
                <div class="form-group">
                    <select class="form-control">
                        <option>Papers influenced by</option>
                        <option>Authors influenced by</option>
                        <option>Paper influence on</option>
                        <option>Author influence on</option>
                    </select>
                    <input type="text" class="form-control">
                </div>
            </form>
        </div>
    </div>

    <div id="Graph"></div>
@endsection

@section('page-footer')
    <script src="{{asset('js/clustering.js')}}" type="application/javascript"></script>
@endsection