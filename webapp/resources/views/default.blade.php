<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
<head>
    @include('includes.head')
</head>
<body>
<div id="app">
    <div class="container-fluid">
        <div class="row">
            <nav class="col-xs-3 sidebar-wrapper">
                @include('includes.sidebar')
            </nav>
            <main class="col-xs-9 col-xs-offset-3 main-wrapper">
                @yield('page-template')
            </main>
        </div>
    </div>
</div>


<script src="{{asset('js/app.js')}}" type="application/javascript"></script>

@yield('page-footer')

</body>
</html>
