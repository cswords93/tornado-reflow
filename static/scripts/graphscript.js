
/*Converts a value to the corect coordinate so it will fit
 * on the line graph along the y axis */
function convertTemp(value, max, length){

	var percent = 100 - value / max * 100;
	var result = (length) / 100 * percent;
	return Math.round(result);
}

/*Converts a time value to the corect coordinate so it will fit
 * on the line graph along the x axis */
function convertTime(value, max, length){

	var percent = value / max * 100;
	var result = (length) / 100 * percent;
	return Math.round(result);
}

/*Creates a new SVG circle to be used as a data point on the graph */
function createPoint(x, y){
	var point = document.createElementNS('http://www.w3.org/2000/svg','circle');
	var radius = 2; 
	
	point.setAttribute('r',radius);
	point.setAttribute('cx', x);
	point.setAttribute('cy',y);
	return point;
}

/* Returns the SVG document */
function graphDoc(){
	var svgObject = document.getElementById("svg-embed");
	var svgDoc = svgObject.contentDocument;
	return svgDoc;
}

/* Plots a new point on the line graph */
function plotPoint(time, temp, type){

	var timeX = convertTime(time,420,700) + 50;
	var tempY = convertTemp(temp,250,500) + 50;
	var point = createPoint(timeX, tempY);
	var svg = graphDoc();
	
	var points = svg.getElementById(type);
	points.appendChild(point);
	
}

/* Removes all current points plotted on the path */
function clearPoints(){
	var svg = graphDoc();
	var points = svg.getElementById("profile-plot-points");
	while(points.firstChild){
		points.removeChild(points.firstChild);
	}
}

/* Removes all current lines connecting the points plotted on the 
 * path */
function clearPaths(){
	var svg = graphDoc();
	var paths = svg.getElementById("profile-plot-paths");
	while(paths.firstChild){
		paths.removeChild(paths.firstChild);
	}
}

/* Draws a line on the line graph */
function drawLine(x1, y1, x2, y2, type){
	var svg = graphDoc();
	var line = document.createElementNS('http://www.w3.org/2000/svg','line');
	line.setAttribute("x1",x1);
	line.setAttribute("y1",y1);
	line.setAttribute("x2",convertTime(x2, 420, 700) + 50);
	line.setAttribute("y2",convertTemp(y2, 250, 500) + 50);
	
	svg.getElementById(type).appendChild(line);
}

/* Plots a two dimensional array of times and temperatures */
function plot(data , preheat){
	clearPaths();
	clearPoints();
	var svg = graphDoc();
	var lines = svg.getElementById("profile-plot-paths");
	var all = data.length;
	var startTemp;
	
	if (preheat != 0){
		
		startTemp = convertTemp(preheat, 250, 500) + 50;
		
	} else {
		
		startTemp = convertTemp(25, 250, 500) + 50;;
	}
	
	
	for(var i = 0 ; i < all ; i++){
		var lastLine = lines.lastChild;
		var time = data[i][0];
		var temp = data[i][1];

		plotPoint(time, temp , "profile-plot-points");
		
		if(lastLine === null){
			
			drawLine(50, startTemp, time, temp, "profile-plot-paths");
			
		} else {
			
			drawLine(lastLine.getAttribute("x2"), 
			lastLine.getAttribute("y2"), time, temp,
			"profile-plot-paths");
		}
	}
}
