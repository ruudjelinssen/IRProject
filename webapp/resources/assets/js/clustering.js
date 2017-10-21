const data = JSON.parse(document.getElementById('GraphData').innerHTML);

function idIndex(a,id) {
	for (var i=0;i<a.length;i++) {
		if (a[i].id == id) return i;}
	return null;
}

var nodes=[], links=[];
data.results[0].data.forEach(function (row) {
	row.graph.nodes.forEach(function (n) {
		if (idIndex(nodes,n.id) == null)
			nodes.push({id:n.id,label:n.labels[0],title:n.properties.name});
	});
	links = links.concat( row.graph.relationships.map(function(r) {
		return {source:idIndex(nodes,r.startNode),target:idIndex(nodes,r.endNode),type:r.type};
	}));
});
viz = {nodes:nodes, links:links};


console.log(viz);

var width = 800, height = 800;
// force layout setup
var force = d3.layout.force().charge(-200).linkDistance(30).size([width, height]);

// setup svg div
var svg = d3.select("#Graph").append("svg")
	.attr("width", "100%").attr("height", "100%")
	.attr("pointer-events", "all");



force.nodes(viz.nodes).links(viz.links).start();

// render relationships as lines
var link = svg.selectAll(".link")
	.data(viz.links).enter()
	.append("line").attr("class", "link");

// render nodes as circles, css-class from label
var node = svg.selectAll(".node")
	.data(viz.nodes).enter()
	.append("circle")
	.attr("class", function (d) { return "node "+d.label })
	.attr("r", 10)
	.call(force.drag);

// html title attribute for title node-attribute
node.append("title")
	.text(function (d) { return d.title; })

// force feed algo ticks for coordinate computation
force.on("tick", function() {
	link.attr("x1", function(d) { return d.source.x; })
		.attr("y1", function(d) { return d.source.y; })
		.attr("x2", function(d) { return d.target.x; })
		.attr("y2", function(d) { return d.target.y; });

	node.attr("cx", function(d) { return d.x; })
		.attr("cy", function(d) { return d.y; });
});