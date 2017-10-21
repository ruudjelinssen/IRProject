// --------- Parse the data we get from the PHP -----------

const data = JSON.parse(document.getElementById('GraphData').innerHTML);

function idIndex(a,id) {
	for (let i=0;i<a.length;i++) {
		if (a[i].id === id) return i;}
	return null;
}

const color = d3.scale.category10();

let node_array=[], links=[];
data.results[0].data.forEach(function (row) {
	row.graph.nodes.forEach(function (n) {
		if (idIndex(node_array,n.id) === null) {
			const node = {id: n.id, label: n.labels[0], title: n.properties.name || n.properties.title, group: n.labels[0]};
			if(n.properties.p_id === parseInt(location.search.split('entity_id=')[1].split('&')[0])
				|| n.properties.a_id === parseInt(location.search.split('entity_id=')[1].split('&')[0])){
				node.fixed = true;
				node.group = 'Root';
			}
			node_array.push(node);
		}
	});
	links = links.concat( row.graph.relationships.map(function(r) {
		return {source:idIndex(node_array,r.startNode),target:idIndex(node_array,r.endNode),type:r.type};
	}));
});

viz = {nodes:node_array, links:links};
console.log(viz);

// ------------ Now create the d3 graph visualisation ----------------

const width = 800, height = 500;
const fill = d3.scale.category20();

// Setup svg div

const svg = d3.select("#Graph").append("svg")
	.attr("width", "100%").attr("height", "100%")
	.attr("pointer-events", "all");

const force = d3.layout.force()
	.nodes(viz.nodes)
	.links(viz.links)
	.size([width,height])
	.linkDistance([200])
	.charge([-500])
	.theta(0.1)
	.gravity(0.05)
	.start();

const edges = svg.selectAll("line")
	.data(viz.links)
	.enter()
	.append("line")
	.attr('marker-end','url(#arrowhead)')
	.style("stroke","#ccc")
	.style("pointer-events", "none");

const nodes = svg.selectAll("circle")
	.data(viz.nodes)
	.enter()
	.append("circle")
	.attr({"r":20})
	.style("fill",function(d,i){return color(d.group);})
	.call(force.drag);


const nodeLabels = svg.selectAll(".nodelabel")
	.data(viz.nodes)
	.enter()
	.append("text")
	.attr({"x":function(d){return d.x;},
		"y":function(d){return d.y;},
		"class":"nodelabel",
		"stroke":"black"})
	.text(function(d){return d.title || '';});

const edgePaths = svg.selectAll(".edgepath")
	.data(viz.links)
	.enter()
	.append('path')
	.attr({'d': function(d) {return 'M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y},
		'class':'edgepath',
		'fill-opacity':0,
		'stroke-opacity':0,
		'fill':'blue',
		'stroke':'red',
		'id':function(d,i) {return 'edgepath'+i}})
	.style("pointer-events", "none");

const edgeLabels = svg.selectAll(".edgelabel")
	.data(viz.links)
	.enter()
	.append('text')
	.style("pointer-events", "none")
	.attr({'class':'edgelabel',
		'id':function(d, i){return 'edgelabel'+i},
		'dx':80,
		'dy':0,
		'font-size':10,
		'fill':'#aaa'});

edgeLabels.append('textPath')
	.attr('xlink:href',function(d,i) {return '#edgepath'+i})
	.style("pointer-events", "none")
	.text(function(d){return d.type});


svg.append('defs').append('marker')
	.attr({'id':'arrowhead',
		'viewBox':'-0 -5 10 10',
		'refX':25,
		'refY':0,
		'orient':'auto',
		'markerWidth':10,
		'markerHeight':10,
		'xoverflow':'visible'})
	.append('svg:path')
	.attr('d', 'M 0,-5 L 10 ,0 L 0,5')
	.attr('fill', '#ccc')
	.attr('stroke','#ccc');


force.on("tick", function(){

	edges.attr({"x1": function(d){return d.source.x;},
		"y1": function(d){return d.source.y;},
		"x2": function(d){return d.target.x;},
		"y2": function(d){return d.target.y;}
	});

	nodes.attr({"cx":function(d){return d.x;},
		"cy":function(d){return d.y;}
	});

	nodeLabels.attr("x", function(d) { return d.x; })
		.attr("y", function(d) { return d.y; });

	edgePaths.attr('d', function(d) { var path='M '+d.source.x+' '+d.source.y+' L '+ d.target.x +' '+d.target.y;
		//console.log(d)
		return path});

	edgeLabels.attr('transform',function(d,i){
		if (d.target.x<d.source.x){
			bbox = this.getBBox();
			rx = bbox.x+bbox.width/2;
			ry = bbox.y+bbox.height/2;
			return 'rotate(180 '+rx+' '+ry+')';
		}
		else {
			return 'rotate(0)';
		}
	});
});