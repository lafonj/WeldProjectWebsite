var realCalendar = [];
var dateCell = [];

$(document).ready(function() {
	$('[data-toggle="tooltip"]').tooltip();
	NoYears = 4;
	StartYear = 2011;
	MainContainer = document.getElementById('MainContainer');
	for(var year=0; year<NoYears; year++){
		for(var month=0; month<12; month++){
			if(month%4==0){
				var currRow = document.createElement('div');
				currRow.setAttribute('class', 'row');
				MainContainer.appendChild(currRow);
			}
			var currCell = document.createElement('div');
			currCell.setAttribute('class', 'col-md-3');
			tableCreate(currCell,month,year+StartYear);
			currRow.appendChild(currCell);		
		}
		
	}
})

function addDate(date){
	var selCell = document.getElementById(date);
	if(selCell.getAttribute('IOstatus')==0){
		realCalendar.push(date);
		sendCalendar()
		var index = dateCell.indexOf(date);
		if(index>=0){
			dateCell.splice(index, 1);
			$('#'+date).tooltip('destroy');				
			selCell.removeAttribute('data-toggle');
			selCell.removeAttribute('data-original-title');
			selCell.removeAttribute('data-container');
			selCell.removeAttribute('data-placement');
		}
		selCell.style.backgroundColor = '#33a6cc';
		selCell.setAttribute('IOstatus', 1);
	}else{
		selCell.style.backgroundColor = 'transparent';
		selCell.setAttribute('IOstatus', 0);
		var index = realCalendar.indexOf(date);
		realCalendar.splice(index, 1);
		sendCalendar()
	}
}

function tableCreate(currCell,month,year){
	var allMonths = ['January', 'February','March','April','May','June','July','August','September','October','November','December',];
	var tbl=document.createElement('table');
	tbl.setAttribute('class','table');
	var monthStart = new Date(year,month,1);
	var monthEnd = new Date(year, month + 1, 1);
	var monthLength = Math.round((monthEnd - monthStart) / (1000 * 60 * 60 * 24));
	var dateshift = monthStart.getDay()+1;
	var thead = document.createElement('thead')
	var tr = document.createElement('tr');
	var td = document.createElement('th');
	td.setAttribute('colspan',7);
	td.appendChild(document.createTextNode(allMonths[month]+'-'+year.toString()));
	tr.appendChild(td);
	thead.appendChild(tr);
	tr = document.createElement('tr');
	tr.innerHTML='<th>Su</th><th>Mo</th><th>Tu</th><th>We</th><th>Th</th><th>Fr</th><th>Sa</th>';
	thead.appendChild(tr);
	tbl.appendChild(thead);
	tbody = document.createElement('tbody');
	tbl.appendChild(tbody)
	for(var i=0;i<6;i++){
	    var tr=document.createElement('tr');
	    for(var j=1;j<=7;j++){
			var td=document.createElement('td');
			calendarDay = i*7+j+1-dateshift;
			if(calendarDay>=1 && calendarDay<=monthLength){				
				td.appendChild(document.createTextNode(calendarDay.toString()))
				td.setAttribute('onclick','addDate("' + year.toString()+'-'+('0'+(month+1).toString()).slice(-2)+'-'+('0'+calendarDay.toString()).slice(-2)+'")');
				td.setAttribute('IOstatus', 0);
				td.setAttribute('id',year.toString()+'-'+('0'+(month+1).toString()).slice(-2)+'-'+('0'+calendarDay.toString()).slice(-2));
				td.setAttribute('class','mousey');
			}else{
			td.appendChild(document.createTextNode(''));
			}			
			tr.appendChild(td);
	    }
	    tbody.appendChild(tr);
	}
	currCell.appendChild(tbl);
}

function sendCalendar(){
	var encCalendar = encodeURIComponent(realCalendar);
	$.ajax({
		url:'/cgi-bin/PatternFinder.py?realCalendar='+encCalendar,
		complete: function (response) {
			console.log(response.responseText);
			splitRes = response.responseText.split("\n");
			newDate = splitRes[1];
			newScore = splitRes[0];
			StartDate = splitRes[2];
			Fuzziness = splitRes[3];
			if(splitRes[4]==1){
				CycleThrough = 'days';
			} else if(splitRes[4]==2){
				CycleThrough = 'month(s)';
			} else{
				CycleThrough = 'year(s)';
			}
			CycleFreq = splitRes[5];
			
			//$('[data-toggle="tooltip"]').tooltip('destroy');
			for(var i in dateCell){
				console.log(dateCell)
				cCell = document.getElementById(dateCell[i]);
				cCell.style.backgroundColor = 'transparent';
				$('#'+dateCell[i]).tooltip('destroy');				
				cCell.removeAttribute('data-toggle');
				cCell.removeAttribute('data-original-title');
				cCell.removeAttribute('data-container');
				cCell.removeAttribute('data-placement');				
			}
			dateCell = [];
			var newDateCell = document.getElementById(newDate)
			if(newDateCell != null && realCalendar.indexOf(newDate)<0){
				dateCell.push(newDate);
				newDateCell.style.backgroundColor = '#CC8C33';
				newDateCell.setAttribute('data-toggle',"tooltip");
				newDateCell.setAttribute('data-original-title', 'Prediction score = '+ newScore.toString() +'<br> Traveling every ' + CycleFreq.toString() + ' ' + CycleThrough + ' &plusmn' + Fuzziness.toString() + ' days starting from ' + StartDate.toString());
				newDateCell.setAttribute('data-container', 'body');
				newDateCell.setAttribute('data-placement', 'top');
				$('[data-toggle="tooltip"]').tooltip({html: true});
				
			}
		},
		error: function () {
			console.log('Error'); 
		}
	}); 
}
