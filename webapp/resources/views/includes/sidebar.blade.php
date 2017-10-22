<div id="Sidebar">
    <h1 class="ProjectTitle">IRDM Project</h1>

    <ul class="nav">
        @foreach(Route::getRoutes() as $route_instance)
            <li>
                <a class="NavLink {{ substr(Request::path(), 0, strlen($route_instance->uri())) === $route_instance->uri() ? 'is-active' : '' }}"
                   href="{{route($route_instance->getName())}}">{{$route_instance->getName()}}</a>
            </li>
        @endforeach
    </ul>
</div>