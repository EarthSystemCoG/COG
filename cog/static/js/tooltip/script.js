var tooltip=function(){

	// global variables that specifies tooltip attributes
	var id = 'tt';
	var top = 3;
	var left = 3;
	var maxw = 210;
	var speed = 10;
	var timer = 20;
	var endalpha = 95;
	var alpha = 0;
	var tt,t,c,b,h;
	var ie = document.all ? true : false;
	
	return{
	
		// function that instantoates (first time) and shows the tooltip
		show:function(widget, v, w) {
				    
			if (tt == null) {
				tt = document.createElement('div');
				tt.setAttribute('id',id);
				t = document.createElement('div');
				t.setAttribute('id',id + 'top');
				c = document.createElement('div');
				c.setAttribute('id',id + 'cont');
				b = document.createElement('div');
				b.setAttribute('id',id + 'bot');
				tt.appendChild(t);
				tt.appendChild(c);
				tt.appendChild(b);
				document.body.appendChild(tt);
				tt.style.opacity = 0;
				tt.style.filter = 'alpha(opacity=0)';
				// locate the tooltip close to the mouse event
				//document.onmousemove = this.pos_mouse;
			}
			
			tt.style.display = 'block';
			c.innerHTML = v;
			tt.style.width = w ? w + 'px' : 'auto';
			
			if(!w && ie){
				t.style.display = 'none';
				b.style.display = 'none';
				tt.style.width = tt.offsetWidth;
				t.style.display = 'block';
				b.style.display = 'block';
			}
			
			if(tt.offsetWidth > maxw){tt.style.width = maxw + 'px'}
			h = parseInt(tt.offsetHeight) + top;
			clearInterval(tt.timer);
			tt.timer = setInterval(function(){tooltip.fade(1)},timer);
			
			// locate the tooltip close to the project text
			this.pos_project_text(widget);
			
		},
		
		// function to position the tooltip close to the mouse event
		pos_mouse:function(e){
			// positions the tooltip according to the location of the onmousemove event
			var u = ie ? event.clientY + document.documentElement.scrollTop : e.pageY;
			var l = ie ? event.clientX + document.documentElement.scrollLeft : e.pageX;
			tt.style.top = (u - h) + 'px';
			tt.style.left = (l + left) + 'px';
		},
		
		// function to position the tooltip to the left of the project text
		pos_project_text:function(widget){
			
			var rect = widget.getBoundingClientRect();
		    var elementLeft,elementTop; //x and y
			var scrollTop = document.documentElement.scrollTop ? document.documentElement.scrollTop:document.body.scrollTop;
			var scrollLeft = document.documentElement.scrollLeft ? document.documentElement.scrollLeft:document.body.scrollLeft;
			elementTop = rect.top+scrollTop;
			elementLeft = rect.left+scrollLeft;
		
			tt.style.top = (elementTop - h) + 'px';
			tt.style.left = (elementLeft - maxw) + 'px';
		},
		
		// function to fade the tooltip
		fade:function(d){
			var a = alpha;
			if((a != endalpha && d == 1) || (a != 0 && d == -1)){
				var i = speed;
				if(endalpha - a < speed && d == 1){
					i = endalpha - a;
				}else if(alpha < speed && d == -1){
					i = a;
				}
				alpha = a + (i * d);
				tt.style.opacity = alpha * .01;
				tt.style.filter = 'alpha(opacity=' + alpha + ')';
			}else{
				clearInterval(tt.timer);
				if(d == -1){tt.style.display = 'none'}
			}
		},
		
		// function to hide the tooltip
		hide:function(){
			clearInterval(tt.timer);
			tt.timer = setInterval(function(){tooltip.fade(-1)},timer);
		}
		
	};
}();

