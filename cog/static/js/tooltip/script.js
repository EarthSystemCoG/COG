var tooltip=function(){

	// global variables that specifies tooltip attributes
	var id = 'tt';
	var top = -12; // vertical position above project short name
	var left = 0;
    var size = "198px";
	var maxw = 210;  // take width below (w) + whatever padding is wanted to take outside the project browser
	var speed = 10;
	var timer = 20;
	var endalpha = 95;
	var alpha = 0;
	var tt,t,c,b,h;
    var sjm, tbl, tblBody, row, text, cell_1, cell_2;
	var ie = document.all ? true : false;
	
	return{
	
		// function that instantiates (first time) and shows the tooltip
        // v=inner_text, w=width
		show:function(widget, v, w) {
            //console.log('in show function');
            text = document.createTextNode(v);
            // first time page is loaded, create the pop up. This only happens once.
            // styles can be set here or in the .css file. Both work.
            if (tbl == null) {
                    //console.log('in inner_loop');
                    tbl = document.createElement('table');
                    tblBody = document.createElement('tbody');
                    row = document.createElement('tr');
                    cell_1 = document.createElement('td');
                    cell_1.style.verticalAlign = 'middle';
                    cell_1.style.background = '#f2e886';
                    cell_1.style.width = size;
                    row.appendChild(cell_1);
                    tblBody.appendChild(row);

                    //tt = document.createElement('div');
                    //tt.setAttribute('id', id);
                    //t = document.createElement('div');
                    //t.setAttribute('id', id + 'top');
                    //c = document.createElement('div');
                    //c.setAttribute('id', id + 'cont');
                    //b = document.createElement('div');
                    //b.setAttribute('id', id + 'bot');
                    //tt.appendChild(t);
                    //tt.appendChild(c);
                    //tt.appendChild(sjm);
                    //tt.appendChild(b);
                    //c.innerHTML = v;

                    // add arrow
                    sjm = document.createElement('div');
                    sjm.setAttribute('class','arrow-right');
                    sjm.setAttribute.display = 'inline';
                    cell_2 = document.createElement('td');
                    cell_2.appendChild(sjm);
                    cell_2.style.verticalAlign = 'bottom';
                    cell_2.style.padding = "0";
                    cell_2.style.paddingBottom = "2px";
                    row.appendChild(cell_2); // append arrow to row

                    tblBody.appendChild(row); // append row to tbody
                    tbl.appendChild(tblBody); // append tbody to table
                    document.body.appendChild(tbl); // add table to the display

                    tbl.style.opacity = 0;
                    tbl.style.filter = 'alpha(opacity=0)';
                    tbl.style.width = w ? w + 'px' : 'auto'; //width comes from w, height is automatic
                }

                // these two styles are required for the table to appear. They must exist at all time even when the
                // table is nolonger null, so must be OUTSIDE the if statement
                tbl.style.display = 'block';  // these are duplicated in the css, but that is required
                tbl.style.position = 'absolute'; // these are duplicated in the css, but that is required

                // change the text every time. Note .appendChild would not work here.
                // this must be outside the if statement so it happens every time.
                tbl.rows[0].cells[0].innerHTML = v;

			if(!w && ie){
				//t.style.display = 'none';
				//b.style.display = 'none';
				tbl.style.width = tbl.offsetWidth;
				//t.style.display = 'block';
				//b.style.display = 'block';
			}
			
			if(tbl.offsetWidth > maxw){tbl.style.width = maxw + 'px'}
			h = parseInt(tbl.offsetHeight) + top;
			clearInterval(tbl.timer);
			tbl.timer = setInterval(function(){tooltip.fade(1)},timer);
			
			// locate the tooltip close to the project text
			this.pos_project_text(widget);
			
		},
		
		// function to position the tooltip close to the mouse event
		pos_mouse:function(e){
            //console.log('in pos_mouse')
			// positions the tooltip according to the location of the onmousemove event
			var u = ie ? event.clientY + document.documentElement.scrollTop : e.pageY;
			var l = ie ? event.clientX + document.documentElement.scrollLeft : e.pageX;
			tbl.style.top = (u - h) + 'px';
			tbl.style.left = (l + left) + 'px';
		},
		
		// function to position the tooltip to the left of the project text
		pos_project_text:function(widget){
			//console.log('in pos_project');
			var rect = widget.getBoundingClientRect();
		    var elementLeft,elementTop; //x and y
			var scrollTop = document.documentElement.scrollTop ? document.documentElement.scrollTop:document.body.scrollTop;
			var scrollLeft = document.documentElement.scrollLeft ? document.documentElement.scrollLeft:document.body.scrollLeft;
			elementTop = rect.top+scrollTop;
			elementLeft = rect.left+scrollLeft;
		    //must have position = absolute
			tbl.style.top = (elementTop - h) + 'px';
			tbl.style.left = (elementLeft - maxw) + 'px';
		},
		
		// function to fade the tooltip
		fade:function(d){
            //console.log('in fade');
			var a = alpha;
			if((a != endalpha && d == 1) || (a != 0 && d == -1)){
				var i = speed;
				if(endalpha - a < speed && d == 1){
					i = endalpha - a;
				}else if(alpha < speed && d == -1){
					i = a;
				}
				alpha = a + (i * d);
				tbl.style.opacity = alpha * .01;
				tbl.style.filter = 'alpha(opacity=' + alpha + ')';

			}else{
				clearInterval(tbl.timer);
				if(d == -1){tbl.style.display = 'none'}
			}

		},
		
		// function to hide the tooltip
		hide:function(){
            //console.log('in hide');
			clearInterval(tbl.timer);
			tbl.timer = setInterval(function(){tooltip.fade(-1)},timer);
		}

	};
}();

