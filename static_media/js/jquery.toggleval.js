/* -------------------------------------------------- *
 * ToggleVal 2.1
 * Updated: 1/16/09
 * -------------------------------------------------- *
 * Author: Aaron Kuzemchak
 * URL: http://aaronkuzemchak.com/
 * Copyright: 2008-2009 Aaron Kuzemchak
 * License: MIT License
** -------------------------------------------------- */

(function($){$.fn.toggleVal=function(theOptions){if(!theOptions||typeof(theOptions)=="object"){theOptions=$.extend({focusClass:"tv-focused",changedClass:"tv-changed",populateFrom:"default",text:null,removeLabels:false},theOptions)}else if(typeof(theOptions)=="string"&&theOptions.toLowerCase()=="destroy"){var destroy=true}return this.each(function(){if(destroy){$(this).unbind("focus.toggleval").unbind("blur.toggleval").removeData("defText");return false}var defText="";switch(theOptions.populateFrom){case"alt":defText=$(this).attr("alt");$(this).val(defText);break;case"label":defText=$("label[for='"+$(this).attr("id")+"']").text();$(this).val(defText);break;case"custom":defText=theOptions.text;$(this).val(defText);break;default:defText=$(this).val()}$(this).addClass("toggleval").data("defText",defText);if(theOptions.removeLabels==true){$("label[for='"+$(this).attr("id")+"']").remove()}$(this).bind("focus.toggleval",function(){if($(this).val()==$(this).data("defText")){$(this).val("")}$(this).addClass(theOptions.focusClass).removeClass(theOptions.changedClass)}).bind("blur.toggleval",function(){if($(this).val()==""){$(this).val($(this).data("defText"))}$(this).removeClass(theOptions.focusClass);if($(this).val()!=$(this).data("defText")){$(this).addClass(theOptions.changedClass)}else{$(this).removeClass(theOptions.changedClass)}})})}})(jQuery);