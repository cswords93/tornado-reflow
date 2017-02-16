var FORM;
var PROFILE_TABLE;

window.onload = loadDoc;

function loadDoc(){
	FORM = document.getElementById("profile-form");
	PROFILE_TABLE = document.getElementById("myNewProfileTable")
	displayErrors();
}

function displayErrors(){
	errorsContainer = document.getElementById("errorsContainer");
	if (errorsContainer.children.length > 0){
		errorsContainer.style.display = "block";
	}
}

function new_input(){
	var time_input = create_input("time","text","timeIn",inputChange)
	var temp_input = create_input("temperature","text","tempIn",inputChange);
	
	var tableLength = PROFILE_TABLE.rows.length;
	var row = PROFILE_TABLE.insertRow(tableLength);
	
	var cell1 = row.insertCell(0);
	var cell2 = row.insertCell(1);
	var cell3 = row.insertCell(2);
	var cell4 = row.insertCell(3);
	
	cell1.innerHTML = tableLength;
	cell2.appendChild(time_input);
	cell3.appendChild(temp_input);
}

function create_input(name, type, className, onchange){
	var input = document.createElement("input");
	input.name = name;
	input.type = type;
	input.className = className;
	input.onchange = onchange;
	return input;
}

function delete_input(){
	var last = PROFILE_TABLE.lastChild;
	PROFILE_TABLE.removeChild(last);
}


function inputChange(){
	var time_ins = document.getElementsByClassName("timeIn");
	var temp_ins = document.getElementsByClassName("tempIn");
	var preheat = Number(document.getElementById("preheat").value);
	
	var len = time_ins.length;
	
	data = [];
	
	for(i = 0 ; i < len ; i ++){
		time = time_ins[i].value;
		temp = temp_ins[i].value;
		
		if(time != "" && temp != ""){
			data.push([time, temp]);
		}
	}
	plot(data, preheat);
}
