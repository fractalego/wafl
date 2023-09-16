def get_html_from_dialogue_item(
    text,
    index,
    conversation_id,
    bot_is_computing_answer,
    reload_messages=False,
    autofocus=False,
):
    if text.find("bot:") == 0:
        if bot_is_computing_answer:
            return (
                f"<div id='messages-{index}'"
                f"hx-post='/{conversation_id}/{index}/messages'"
                f"hx-swap='outerHTML'"
                f"hx-target='#messages-{index}'"
                f"hx-trigger='every 1s'"
                f">" + text[4:].strip() + "</div>"
            )

        if reload_messages:
            return (
                f"<div id='messages-{index}' class='shadow-lg dialogue-row-bot' style='font-size:20px; '"
                f"hx-post='/{conversation_id}/load_messages'"
                f"hx-swap='innerHTML'"
                f"hx-target='#messages'"
                f"hx-trigger='load'"
                f">" + text[4:].strip() + "</div>"
            )

        else:
            return (
                f"<div id='messages-{index}' class='shadow-lg dialogue-row-bot' style='font-size:20px; '"
                f">" + text[4:].strip() + "</div>"
            )

    if text.find("user:") == 0:
        autofocus_str = "autofocus" if autofocus else ""
        return (
            f"<textarea {autofocus_str} id='textarea-{index}'"
            f"class='shadow-lg dialogue-row-user' name='query' rows='1' style='font-size:20px; min-height:50px;' type='text'"
            f"hx-post='/{conversation_id}/{index}/input'"
            f"hx-swap='outerHTML'"
            f"hx-target='#messages-{index+1}'"
            f"hx-trigger='keydown[!shiftKey&&keyCode==13]'"
            f">" + text[5:] + "</textarea>"
            f"""
<script>
$("#textarea-{index}").on("keydown", function(e){{
  if (e.keyCode == 13 && !e.shiftKey)
  {{
    // prevent default behavior
    e.preventDefault();
    return false;
  }}
}});
</script>
            """
        )

    return (
        "<div class='dialogue-row-comment' style='font-size:20px; '>"
        + text.strip()
        + "</div>"
    )