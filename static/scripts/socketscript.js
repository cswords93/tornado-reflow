// -- Socket Functions //
var socket = new WebSocket("ws://"+document.domain+":"+location.port +
"/socket");

		
socket.onopen = function(event){
	console.log("Connected to server");
}

socket.onclose = function(event){
	console.log("Disconnected from server");
}

socket.onmessage = function(event){
	var JSONMessage = JSON.parse(event.data);
	var run_time = JSONMessage["run_time"];
	var temp = JSONMessage["temperature"];
	console.log(temp);
	console.log(run_time);
	
	var state = JSONMessage["oven_state"];
	var lines = graphDoc().getElementById("oven-plot-paths");
	var lastLine = lines.lastChild;	
	var ovenTemperature = document.getElementById("ovenTemperature");
	var ovenTargetTemperature = document.getElementById("ovenTargetTemperature");
	var ovenState = document.getElementById("ovenState");
	
	ovenTemperature.innerHTML = temp;
	ovenState.innerHTML = state;

	plotPoint(run_time, temp, "oven-plot-points");
	
	if(lastLine === null){
		
		drawLine(50, 500, run_time, temp, "oven-plot-paths");
		
	} else {
		
		drawLine(lastLine.getAttribute("x2"), 
		lastLine.getAttribute("y2"), run_time, temp, 
		"oven-plot-paths");
	}
}

function startOven(){
	var profile = document.getElementById("profile-select").value;
	var duration = document.getElementById("duration").innerHTML;
	
	if (profile !== ""){
		var obj = {"CMD":"START","PROFILE":profile};
		var json = JSON.stringify(obj);
		socket.send(json);
		startTimer(duration);
	} else {
		alert("Please select a profile before starting.");
	}
}

function stopOven(){
	var obj = {
		"CMD":"STOP"
	};
	var json = JSON.stringify(obj);
	socket.send(json);
	resetStatusTable();
}


