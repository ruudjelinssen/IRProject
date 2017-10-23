<nav class="navbar navbar-default navbar-fixed-top" id="MainNavBar">
    <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
            <a class="navbar-brand" href="{{route('home')}}">IR & DM Project</a>
        </div>

        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
            <ul class="nav navbar-nav">
                <li>
                    <a class="NavLink {{ \Request::route()->getName() === 'explore by search' ? 'is-active' : '' }}"
                       href="{{route('explore by search')}}"
                    >
                        Explore By Search
                    </a>
                </li>
                <li>
                    <a class="NavLink {{ \Request::route()->getName() === 'explore by topic' ? 'is-active' : '' }}"
                       href="{{route('explore by topic', 0)}}"
                    >
                        Explore By Topic
                    </a>
                </li>
                <li>
                    <a class="NavLink {{ \Request::route()->getName() === 'topic visualisation' ? 'is-active' : '' }}"
                       href="{{route('topic visualisation')}}"
                    >
                        Visualise With LDA
                    </a>
                </li>
            </ul>
        </div><!-- /.navbar-collapse -->
    </div><!-- /.container-fluid -->
</nav>