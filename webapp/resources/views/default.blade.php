<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
<head>
    @include('includes.head')
</head>
<body>
<div id="app">
    <div class="container-fluid">
        <div class="row">
            @include('includes.sidebar')
            <main class="col-xs-10 col-xs-offset-1 main-wrapper">
                @yield('page-template')
            </main>
        </div>
    </div>
</div>


<script src="{{asset('js/app.js')}}" type="application/javascript"></script>

@yield('page-footer')

</body>
</html>
