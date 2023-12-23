$("textarea").on("keydown", function(e){
  if (e.keyCode == 13 && !e.shiftKey)
  {
    // prevent default behavior
    e.preventDefault();
    return false;
  }
});