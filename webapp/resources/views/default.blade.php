<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
<head>
    @include('includes.head')
</head>
<body>
<div id="app">

    @yield('page-template')

</div>

<script src="{{asset('js/app.js')}}" type="application/javascript"></script>

</body>
</html>
